import os
import requests
from fastapi import FastAPI, Request
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from dotenv import load_dotenv
from back.model_functions import load_peft_model, format_math_expressions
import json

load_dotenv()

app = FastAPI()

# =========================
# 🔹 Загрузка модели
# =========================
model_path = os.getenv("MODEL_PATH")  # путь к модели
lora_path = os.getenv("LORA_PATH")  # путь к модели
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")



model, tokenizer = load_peft_model()





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

    print(f"[SEARCH_WEB] query: {query}")

    data = response.json()

    results = []
    for r in data.get("results", []):
        results.append(r["content"])

    return "\n".join(results)

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

    print("=== DEBUG ===")
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
        max_length=4096
    )

    input_device = next(model.parameters()).device
    inputs = {k: v.to(input_device) for k, v in inputs.items()}
    outputs = model.generate(
        **inputs,
        max_new_tokens=2048,
        temperature=0.7,
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
        "кто", "что", "новости", "последние", "объясни", "как работает", 'новые', 
        'найди', 'недавно'
    ])

    context = ""
    if use_search:
        context = search_web(last_user_msg)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
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