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


# диапазоны Unicode для китайских/японских/корейских иероглифов (CJK)
CJK_RANGES = [
    (0x4E00, 0x9FFF),    # CJK Unified Ideographs (основной блок, китайские иероглифы)
    (0x3400, 0x4DBF),    # CJK Unified Ideographs Extension A
    (0x20000, 0x2A6DF),  # CJK Unified Ideographs Extension B
    (0xF900, 0xFAFF),    # CJK Compatibility Ideographs
    (0x3000, 0x303F),    # CJK Symbols and Punctuation
    (0xFF00, 0xFFEF),    # Halfwidth/Fullwidth Forms
]


def _contains_cjk(text: str) -> bool:
    """Проверяет, содержит ли строка символы из CJK-диапазонов"""
    for ch in text:
        code = ord(ch)
        for start, end in CJK_RANGES:
            if start <= code <= end:
                return True
    return False


@lru_cache(maxsize=1)
def get_cjk_bad_words_ids():
    """
    Сканирует весь словарь токенизатора и возвращает список id токенов,
    которые при декодировании содержат китайские/CJK символы.
    """
    _, tokenizer = load_peft_model()

    vocab = tokenizer.get_vocab()
    bad_ids = []

    for token_str, token_id in vocab.items():
        # декодируем токен в реальный текст (BPE-ключи могут быть закодированы байтами)
        try:
            decoded = tokenizer.decode([token_id])
        except Exception:
            continue

        if _contains_cjk(decoded):
            bad_ids.append([token_id])

    print(f"[CJK FILTER] найдено {len(bad_ids)} токенов с CJK-символами из {len(vocab)} токенов словаря")

    return bad_ids


# загрузкат модели
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

        print("Модель загружена")
        return model, tokenizer

    except Exception as e:
        print(f"Ошибка при загрузке модели: {e}")
        raise


# поиск
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


# генерация ответа
def generate_response_peft(prompt):
    """Генерация ответа с optional search"""

    model, tokenizer = load_peft_model()
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
    return response
    

def clean_markdown(text: str):

    # заголовки
    text = re.sub(
        r"(#{1,6}\s)",
        r"\n\n\1",
        text
    )

    # списки
    text = re.sub(
        r"(\n?)([-*]\s)",
        r"\n\2",
        text
    )

    # нумерованные списки
    text = re.sub(
        r"(\d+\.\s)",
        r"\n\1",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    text = re.sub(
    r"python\s+def",
    "```python\ndef",
    text
)

    if "```python" in text and not text.strip().endswith("```"):
        text += "\n```"
        
    return text.strip()