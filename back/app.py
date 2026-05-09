import os
import requests
from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from dotenv import load_dotenv
from back.model_functions import load_peft_model, format_math_expressions
import json
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from back.database import engine, SessionLocal
from back.models import Base, Chat, Message, User
from sqlalchemy.orm import Session
from back.auth import hash_password, verify_password



load_dotenv()

Base.metadata.create_all(bind=engine)
print("DATABASE CREATED")


app = FastAPI()


# - - - - - - - - - - - - - - - - - - - - - 



# - - - - - - - - - - - - - - - - - - - - - 
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# 🔹 Загрузка модели
# =========================
model_path = os.getenv("MODEL_PATH")  # путь к модели
lora_path = os.getenv("LORA_PATH")  # путь к модели
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
current_date = datetime.now().strftime("%d.%m.%Y") # ТЕКУЩАЯ ДАТА



model, tokenizer = load_peft_model()





# =========================
# 🔹 Tavily поиск
# =========================
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def search_web(query):
    url = "https://api.tavily.com/search"

    current_date = datetime.now().strftime("%d %B %Y")

    response = requests.post(url, json={
        "api_key": TAVILY_API_KEY,
        "query": query,   # БЕЗ даты
        "search_depth": "basic",
        "max_results": 3
    })

    print(f"[SEARCH_WEB] query: {query}")

    data = response.json()
    print("[SEARCH_WEB] raw response:", data)

    results = []

    for r in data.get("results", []):
        title = r.get("title", "")
        content = r.get("content", "")
        url_src = r.get("url", "")

        results.append(
            f"Источник: {title}\n"
            f"Содержание: {content}\n"
            f"Ссылка: {url_src}\n"
        )
        print(results)

    if not results:
        return f"На {current_date} поиск не дал результатов по запросу: {query}"

    return f"Актуальные данные на {current_date}:\n\n" + "\n".join(results)

# =========================
# 🔹 Генерация
# =========================
def generate_answer(messages):

    safe_messages = []

    for msg in messages:
        role = str(msg["role"])
        content = msg["content"]

        if isinstance(content, list):
            content = " ".join(map(str, content))
        elif isinstance(content, dict):
            content = str(content)
        else:
            content = str(content)

        safe_messages.append({
            "role": role,
            "content": content
        })

    print(json.dumps(safe_messages, ensure_ascii=False, indent=2))

    text = tokenizer.apply_chat_template(
        safe_messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=6096
    )

    input_device = next(model.parameters()).device
    inputs = {k: v.to(input_device) for k, v in inputs.items()}
    outputs = model.generate(
        **inputs,
        max_new_tokens=2048,
        temperature=0.5,
        do_sample=True
    )

    input_length = inputs["input_ids"].shape[1]

    generated_tokens = outputs[0][input_length:]

    return format_math_expressions(tokenizer.decode(generated_tokens, skip_special_tokens=True))


# =========================
# 🔹 Логика (search + LLM)
# =========================
def pipeline(chat_history):
    if not chat_history:
        return "История пуста."


    normalized_history = []

    for msg in chat_history:
        normalized_history.append({
            "role": str(msg["role"]),
            "content": str(msg["content"])
        })

    last_user_msg = normalized_history[-1]["content"]

    use_search = any(word in last_user_msg.lower() for word in [
        "кто", "новости", "последние", "объясни", "как работает", 'новые', 
        'найди', 'недавно'
    ])

    context = ""
    if use_search:
        print('USE SEARCH')
        context = search_web(last_user_msg)
    else: print('NOT USE SEARCH')
    messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}. Учитывай актуальную информацию на текущий момент: {current_date}"}
    ]
    

    if context:
        messages.append({
            "role": "system",
            "content": f"Дополнительный контекст:\n{context}"
        })

    messages.extend(normalized_history[-8:])  # ограничение истории

    return generate_answer(messages)

# =========================
# 🔹 API схема
# =========================
class ChatRequest(BaseModel):
    message: str

# @app.post("/chat")
# def chat(req: ChatRequest):
#     answer = pipeline(req.message)
#     return {"response": answer}

class RegisterRequest(BaseModel):

    email: str

    password: str

class LoginRequest(BaseModel):

    email: str

    password: str

@app.post("/register")
def register(
    req: RegisterRequest,
    db: Session = Depends(get_db)
):

    # Проверяем существует ли email
    existing_user = db.query(User).filter(
        User.email == req.email
    ).first()

    if existing_user:

        return {
            "error": "Пользователь уже существует"
        }

    # Хэшируем пароль
    password_hash = hash_password(
        req.password
    )

    # Создаём пользователя
    new_user = User(
        email=req.email,
        password_hash=password_hash
    )

    db.add(new_user)

    db.commit()

    return {
        "message": "Пользователь создан"
    }

@app.post("/login")
def login(
    req: LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == req.email
    ).first()

    if not user:

        return {
            "error": "Пользователь не найден"
        }

    valid_password = verify_password(
        req.password,
        user.password_hash
    )

    if not valid_password:

        return {
            "error": "Неверный пароль"
        }

    return {
        "message": "Успешный вход",
        "user_id": user.id,
        "email": user.email
    }


# =========================
# CREATE CHAT
# =========================
@app.post("/create_chat")
async def create_chat(
    req: Request,
    db: Session = Depends(get_db)
):

    data = await req.json()

    user_id = data.get("user_id")

    new_chat = Chat(

        user_id=user_id,

        title="Новый чат"
    )

    db.add(new_chat)

    db.commit()

    db.refresh(new_chat)

    return {

        "id": new_chat.id,

        "title": new_chat.title
    }

@app.post("/chat")
async def chat(
    req: Request,
    db: Session = Depends(get_db)
):

    data = await req.json()

    chat_id = data.get("chat_id")

    messages = data.get("messages", [])


    # =========================
    # Генерация ответа
    # =========================
    answer = pipeline(messages)


    # =========================
    # Ищем чат
    # =========================
    chat = db.query(Chat).filter(
        Chat.id == chat_id
    ).first()


    if not chat:

        return {
            "error": "Чат не найден"
        }


    # =========================
    # Последнее user message
    # =========================
    last_user_message = messages[-1]


    # =========================
    # Сохраняем user message
    # =========================
    user_msg = Message(

        chat_id=chat.id,

        role="user",

        content=last_user_message["content"]
    )

    db.add(user_msg)


    # =========================
    # Сохраняем assistant message
    # =========================
    assistant_msg = Message(

        chat_id=chat.id,

        role="assistant",

        content=answer
    )

    db.add(assistant_msg)


    # =========================
    # Автоматический title
    # =========================
    if chat.title == "Новый чат":

        title = last_user_message[
            "content"
        ][:30]

        chat.title = title


    db.commit()


    return {
        "response": answer
    }

# =========================
# GET USER CHATS
# =========================
@app.get("/chats/{user_id}")
def get_chats(
    user_id: int,
    db: Session = Depends(get_db)
):

    chats = db.query(Chat).filter(

        Chat.user_id == user_id

    ).all()

    return {

        "chats": [

            {
                "id": chat.id,
                "title": chat.title
            }

            for chat in chats
        ]
    }


@app.delete("/chat/{chat_id}")
def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db)
):

    chat = db.query(Chat).filter(
        Chat.id == chat_id
    ).first()

    if not chat:

        return {
            "error": "Чат не найден"
        }

    # Удаляем сообщения
    db.query(Message).filter(
        Message.chat_id == chat_id
    ).delete()

    # Удаляем чат
    db.delete(chat)

    db.commit()

    return {
        "message": "Чат удалён"
    }


@app.get("/chats/{user_id}")
def get_chats(
    user_id: int,
    db: Session = Depends(get_db)
):

    chats = db.query(Chat).filter(
        Chat.user_id == user_id
    ).order_by(Chat.id.desc()).all()

    result = []

    for chat in chats:

        result.append({
            "id": chat.id,
            "title": chat.title
        })

    return {
        "chats": result
    }

# =========================
# GET CHAT MESSAGES
# =========================
@app.get("/messages/{chat_id}")
def get_messages(
    chat_id: int,
    db: Session = Depends(get_db)
):

    messages = db.query(Message).filter(

        Message.chat_id == chat_id

    ).all()

    return {

        "messages": [

            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content
            }

            for msg in messages
        ]
    }

class CreateChatRequest(BaseModel):

    user_id: int


@app.post("/create_chat")
def create_chat(
    req: CreateChatRequest,
    db: Session = Depends(get_db)
):

    new_chat = Chat(

        user_id=req.user_id,

        title="Новый чат"
    )

    db.add(new_chat)

    db.commit()

    db.refresh(new_chat)

    return {
        "id": new_chat.id,
        "title": new_chat.title
    }


@app.delete("/chat/{chat_id}")
def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db)
):

    messages = db.query(Message).filter(
        Message.chat_id == chat_id
    ).all()

    for msg in messages:

        db.delete(msg)

    chat = db.query(Chat).filter(
        Chat.id == chat_id
    ).first()

    if chat:

        db.delete(chat)

    db.commit()

    return {
        "message": "Чат удалён"
    }

# print(search_web("NVIDIA GeForce RTX 5000 series specs"))