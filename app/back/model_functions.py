import os
import requests
import torch
import streamlit as st
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import re

load_dotenv()

model_path = os.getenv("MODEL_PATH", "./qwen_model")
lora_path = os.getenv("LORA_PATH")
tavily_api_key = os.getenv("TAVILY_API_KEY")
sys_prompt = os.getenv("SYSTEM_PROMPT")

# =========================
# 🔹 Загрузка модели
# =========================
@st.cache_resource
def load_peft_model(model_path=model_path, lora_path=lora_path):
    """Загрузка модели + LoRA"""
    print("🔄 Загружаем модель...")

    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )

        if lora_path and lora_path != "None":
            print("🔗 Подключаем LoRA...")
            model = PeftModel.from_pretrained(model, lora_path)

        model.eval()

        tokenizer = AutoTokenizer.from_pretrained(model_path)

        print("✅ Модель загружена")
        return model, tokenizer

    except Exception as e:
        print(f"❌ Ошибка при загрузке модели: {e}")
        raise


# =========================
# 🔹 Поиск в интернете
# =========================
def search_web(query):
    """Поиск через Tavily API"""

    if not tavily_api_key:
        return ""

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": tavily_api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": 3
            },
            timeout=20
        )

        data = response.json()

        results = []
        for item in data.get("results", []):
            content = item.get("content", "")
            if content:
                results.append(content)

        return "\n".join(results)

    except Exception as e:
        print(f"Ошибка поиска: {e}")
        return ""


# =========================
# 🔹 Генерация ответа
# =========================
def generate_response_peft(prompt):
    """Генерация ответа с optional search"""

    model, tokenizer = load_peft_model()

    # простая эвристика — когда нужен поиск
    search_keywords = [
        "кто", "что", "новости", "последние",
        "современные", "актуальные", "объясни"
    ]

    use_search = any(word in prompt.lower() for word in search_keywords)

    context = ""
    if use_search:
        context = search_web(prompt)

    final_prompt = f"""{sys_prompt}

Контекст:
{context}

Вопрос:
{prompt}

Ответ:
"""

    inputs = tokenizer(
        final_prompt,
        return_tensors="pt",
        truncation=True,
        max_length=4096
    ).to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.7,
            do_sample=True,
            top_p=0.9
        )

    generated_tokens = output[0][inputs["input_ids"].shape[-1]:]

    response = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    )

    # если у тебя есть render_latex
    formatted = format_math_expressions(response)

    return formatted
    
def format_math_expressions(text):

    """
    Функция для обработки математических формул, которые генерирует модель,
    чтобы те понятно выводилиссь пользователю. Формулы обрабатываются с помощью регулярных выражений
    """

    replacements = {
        r'\\frac\{([^}]+)\}\{([^}]+)\}': r'\1/\2',
        r'\\sqrt\{([^}]+)\}': r'√(\1)',
        r'\\pi': 'π',
        r'\\infty': '∞',
        r'\\alpha': 'α',
        r'\\beta': 'β',
        r'\\gamma': 'γ',
        r'\\theta': 'θ',
        r'\\lambda': 'λ',
        r'\\times': '×',
        r'\\cdot': '·',
        r'\\approx': '≈',
        r'\\neq': '≠',
        r'\\leq': '≤',
        r'\\geq': '≥',
        r'\^\{([^}]+)\}': r'^\1',
        r'_\{([^}]+)\}': r'_\1',
    }
    
    formatted_text = text
    for pattern, replacement in replacements.items():
        formatted_text = re.sub(pattern, replacement, formatted_text)
    
    return formatted_text # функция возвращает форматированный текст