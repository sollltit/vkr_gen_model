import os
import requests
from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from dotenv import load_dotenv
from back.model_functions import load_peft_model, clean_markdown, get_cjk_bad_words_ids
import json
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from back.database import engine, SessionLocal
from back.models import Base, Chat, Message, User
from sqlalchemy.orm import Session
from back.auth import hash_password, verify_password
from fastapi.responses import StreamingResponse
import asyncio
from back.text_form import normalize_markdown, format_math_expressions, fix_latex
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

Base.metadata.create_all(bind=engine)
print("DATABASE CREATED")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # или конкретный URL фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

# модель

model_path = os.getenv("MODEL_PATH")  # путь к модели
lora_path = os.getenv("LORA_PATH")  # путь к модели
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
current_date = datetime.now().strftime("%d.%m.%Y") # ТЕКУЩАЯ ДАТА



model, tokenizer = load_peft_model()

# поиск

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

# генерация ответа

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

    # input_device = next(model.parameters()).device
    # inputs = {k: v.to(input_device) for k, v in inputs.items()}
    # outputs = model.generate(
    #     **inputs,
    #     max_new_tokens=4096,
    #     temperature=0.5,
    #     do_sample=True
    # )
    input_device = next(model.parameters()).device
    inputs = {k: v.to(input_device) for k, v in inputs.items()}

    cjk_bad_words_ids = get_cjk_bad_words_ids()

    generate_kwargs = {
        "max_new_tokens": 4096,
        "temperature": 0.6,
        "do_sample": True,
    }
    if cjk_bad_words_ids:  # передаём фильтр только если список не пустой
        generate_kwargs["bad_words_ids"] = cjk_bad_words_ids

    outputs = model.generate(
        **inputs,
        **generate_kwargs
    )

    input_length = inputs["input_ids"].shape[1]

    generated_tokens = outputs[0][input_length:]

    decoded = tokenizer.decode(
    generated_tokens,
    skip_special_tokens=True
    )


    print("=== RAW MODEL OUTPUT ===")
    print(repr(decoded))
    print("=== END RAW ===")

    # обработка формул и спец символов
    decoded = fix_latex(decoded)
    decoded = normalize_markdown(decoded)
    decoded = format_math_expressions(decoded)
    return decoded


def should_search(user_message: str) -> bool:
    """
    Спрашивает у модели, нужен ли веб-поиск для ответа на вопрос.
    Использует короткий промпт и минимум токенов для скорости.
    """
    classifier_prompt = [
        {
            "role": "system",
            "content": (
                "Ты — классификатор запросов. Тебе дают вопрос пользователя. "
                "Определи, нужна ли для ответа АКТУАЛЬНАЯ информация из интернета "
                "(например: новости, последние события, текущие даты, "
                "биографии конкретных людей, свежие технологии, цены, погода, "
                "факты о реальных событиях после 2024 года). "
                "Если вопрос про общие знания, код, математику, объяснение понятий, "
                "которые не меняются со временем — поиск не нужен. "
                "Ответь СТРОГО одним словом: ДА или НЕТ. Без пояснений."
            )
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    text = tokenizer.apply_chat_template(
        classifier_prompt,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    )

    input_device = next(model.parameters()).device
    inputs = {k: v.to(input_device) for k, v in inputs.items()}

    outputs = model.generate(
        **inputs,
        max_new_tokens=5,       # нужно буквально одно слово
        temperature=0.1,        # минимум случайности — нужна стабильность да/нет
        do_sample=False         # детерминированный ответ
    )

    input_length = inputs["input_ids"].shape[1]
    generated_tokens = outputs[0][input_length:]

    decision = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    ).strip().lower()

    print(f"[SEARCH CLASSIFIER] вопрос: {user_message[:50]}... -> ответ модели: '{decision}'")

    return "да" in decision


def pipeline(chat_history):
    if not chat_history:
        return "История пуста."

    normalized_history = []

    for msg in chat_history:
        normalized_history.append({
            "role": str(msg["role"]),
            "content": f'{str(msg["content"])}'
        })

    last_user_msg = normalized_history[-1]["content"]

    # модель сама решает, нужен ли поиск
    use_search = should_search(last_user_msg)

    context = ""
    if use_search:
        print('USE SEARCH')
        context = search_web(last_user_msg)
    else:
        print('NOT USE SEARCH')
    messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}. Учитывай актуальную информацию на текущий момент: {current_date}"}
    ]
    if context:
        messages.append({ 
            "role": "system",
            "content": f"Дополнительный контекст:\n{context}"
        })
    messages.extend(normalized_history[-10:])  # ограничение истории
    return generate_answer(messages)


# API 
class ChatRequest(BaseModel):

    message: str

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
    # проверка есть ли email в бд
    existing_user = db.query(User).filter(
        User.email == req.email
    ).first()
    if existing_user:
        return {
            "error": "Пользователь уже существует"
        }
    # хэш пароля
    password_hash = hash_password(
        req.password
    )
    # создание пользователя
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


# создание нового чата
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

    answer = pipeline(messages) # генерация ответа

    # поиск чата
    chat = db.query(Chat).filter(
        Chat.id == chat_id
    ).first()

    if not chat:
        return {
            "error": "Чат не найден"
        }

    last_user_message = messages[-1]
    user_msg = Message(

        chat_id=chat.id,
        role="user",
        content=last_user_message["content"]
    )
    db.add(user_msg)
    assistant_msg = Message(

        chat_id=chat.id,
        role="assistant",
        content=answer
    )

    db.add(assistant_msg)

    # название чата
    if chat.title == "Новый чат":

        title = last_user_message[
            "content"
        ][:30]

        chat.title = title
    db.commit()

    return {
        "response": answer
    }


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
    db.query(Message).filter(
        Message.chat_id == chat_id
    ).delete()
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


@app.get("/search_chats/{user_id}")
def search_chats(
    user_id: int,
    query: str,
    db: Session = Depends(get_db)
):

    # все чаты пользователя
    chats = db.query(Chat).filter(
        Chat.user_id == user_id
    ).all()

    result_chats = []
    for chat in chats:

        title_match = query.lower() in (
            chat.title or ""
        ).lower()
        message_match = False

        for msg in chat.messages:

            if query.lower() in (
                msg.content or ""
            ).lower():

                message_match = True
                break

        if title_match or message_match:
            result_chats.append({
                "id": chat.id,
                "title": chat.title
            })
    return {

        "chats": result_chats
    }


@app.post("/chat_stream")
async def chat_stream(
    req: Request,
    db: Session = Depends(get_db)
):

    data = await req.json()
    messages = data.get("messages", [])
    chat_id = data.get("chat_id")
    last_user_message = messages[-1]
    db_message = Message(

        chat_id=chat_id,
        role="user",
        content=last_user_message["content"]
    )

    db.add(db_message)
    db.commit()

    # генерация
    answer = pipeline(messages)

    # стриминг
    async def generate():

        full_text = ""
        for char in answer:
            full_text += char
            yield char
            await asyncio.sleep(0.003)


        chat = db.query(Chat).filter(
            Chat.id == chat_id
        ).first()

        if chat and chat.title == "Новый чат":
            first_text = last_user_message["content"]
            generated_title = first_text[:40]
            chat.title = generated_title
            db.commit()
        assistant_message = Message(

            chat_id=chat_id,
            role="assistant",
            content=full_text
        )

        db.add(assistant_message)
        db.commit()

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )