# app.py
import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from dotenv import load_dotenv
from .model_functions import load_model, format_math_expressions

load_dotenv()

app = FastAPI()

# =========================
# 🔹 Загрузка модели
# =========================
model_path = os.getenv("MODEL_PATH")  # путь к модели
lora_path = os.getenv("LORA_PATH")  # путь к модели



model, tokenizer = load_model()





# =========================
# 🔹 Tavily поиск
# =========================
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def search_web(query):
    url = "https://api.tavily.com/search"

    response = requests.post(url, json={
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic",
        "max_results": 5
    })

    data = response.json()

    results = []
    for r in data.get("results", []):
        results.append(r["content"])

    return "\n".join(results)

# =========================
# 🔹 Генерация
# =========================
def generate_answer(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=2048,
        temperature=0.7,
        do_sample=True
    )

    return format_math_expressions(tokenizer.decode(outputs[0], skip_special_tokens=True))



os.getenv("SYSTEM_PROMPT")
# =========================
# 🔹 Логика (search + LLM)
# =========================
def pipeline(query):
    # простая эвристика
    use_search = any(word in query.lower() for word in [
        "кто", "что", "новости", "последние", "объясни", "как работает"
    ])

    context = ""
    if use_search:
        context = search_web(query)

    prompt = f"""{os.getenv("SYSTEM_PROMPT")} Используй контекст, если он есть.

Контекст:
{context}

Вопрос:
{query}

Дай точный и подробный ответ:
"""

    return generate_answer(prompt)

# =========================
# 🔹 API схема
# =========================
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    answer = pipeline(req.message)
    return {"response": answer}