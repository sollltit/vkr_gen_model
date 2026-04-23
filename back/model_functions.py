import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
import streamlit as st
import re
import os
from dotenv import load_dotenv

load_dotenv()

model_path = os.getenv("MODEL_PATH")  # путь к модели
lora_path = os.getenv("LORA_PATH")  # путь к модели

def load_model(model = model_path, lora = lora_path):
    """Загружаем модель"""
    print("🔄 Загружаем модель...")
    try:
        # Загружаем конфиг 
        model = AutoModelForCausalLM.from_pretrained('./qwen_model', dtype = torch.float16, device_map = 'auto')
        model = PeftModel.from_pretrained(model, 'qwen2.5_fine-tune\checkpoint-210')
        model.eval()
        tokenizer = AutoTokenizer.from_pretrained('./qwen_model')
        return model, tokenizer
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке модели: {e}")
        raise e
    
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