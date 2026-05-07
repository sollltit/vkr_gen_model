import os
import requests
from fastapi import FastAPI, Request
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from dotenv import load_dotenv
from back.model_functions import load_peft_model, format_math_expressions
import json
from datetime import datetime

load_dotenv()

app = FastAPI()

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



@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    messages = data.get("messages", [])
    answer = pipeline(messages)
    return {"response": answer}


# print(search_web("NVIDIA GeForce RTX 5000 series specs"))