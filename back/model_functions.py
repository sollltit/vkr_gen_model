import os
import requests
import torch
import streamlit as st
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import re
from transformers import BitsAndBytesConfig
from functools import lru_cache

load_dotenv()

model_path = os.getenv("MODEL_PATH", "./qwen_model")
lora_path = os.getenv("LORA_PATH", './qwen2.5_fine-tune/checkpoint-210')
tavily_api_key = os.getenv("TAVILY_API_KEY")
sys_prompt = os.getenv("SYSTEM_PROMPT")

# =========================
# 🔹 Загрузка модели
# =========================


@lru_cache(maxsize=1)
def load_peft_model(model_path=model_path, lora_path=lora_path):
    """Загрузка модели + LoRA"""
    print("🔄 Загружаем модель...")

    try:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            llm_int8_enable_fp32_cpu_offload=True

        )

        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            quantization_config=bnb_config,
            device_map="auto",
            offload_folder="./offload",
        )

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
                "max_results": 4
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
        "современные", "актуальные", 'недавно', 'характеристики', 'совместимость'
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
    )

    input_device = next(model.parameters()).device
    inputs = {k: v.to(input_device) for k, v in inputs.items()}
    torch.cuda.empty_cache()
    with torch.no_grad():
        # torch.cuda.empty_cache()
        output = model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.55,
            do_sample=True,
            top_p=0.95
        )

    generated_tokens = output[0][inputs["input_ids"].shape[-1]:]

    response = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    )

    # если у тебя есть render_latex
    # formatted = format_math_expressions(response)

    return response
    

def format_math_expressions(text: str) -> str:
    """
    Приводит LaTeX-формулы к корректному виду для отображения в Streamlit/Markdown.
    НЕ ломает LaTeX, а наоборот — оборачивает его в $...$
    """

    # 1. Убираем лишние escape-символы типа \\ → \
    text = text.replace("\\\\", "\\")

    # 2. Формулы в квадратных скобках [ ... ] → $$ ... $$
    text = re.sub(r'\[\s*(.*?)\s*\]', r'$$\1$$', text, flags=re.DOTALL)

    # 3. Inline формулы \( ... \) → $ ... $
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text)

    # 4. Уже существующие $$ не трогаем, но чистим лишние пробелы
    text = re.sub(r'\$\$\s*(.*?)\s*\$\$', r'$$\1$$', text, flags=re.DOTALL)

    # 5. Чистим дубли пробелов
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text
    