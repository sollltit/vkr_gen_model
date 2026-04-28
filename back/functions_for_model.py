import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
import streamlit as st
import re
from IPython.display import Markdown

model_path = './qwen_model'
lora_path = 'qwen2.5_fine-tune/checkpoint-210'


@st.cache_resource
def load_peft_model(model = model_path, lora = lora_path):
    """Загружаем модель"""
    print("🔄 Загружаем модель...")
    try:
        # Загружаем конфиг 
        model = AutoModelForCausalLM.from_pretrained('./qwen_model', dtype = torch.float16, device_map = 'auto')
        model = PeftModel.from_pretrained(model, lora)
        model.eval()
        tokenizer = AutoTokenizer.from_pretrained('./qwen_model')
        return model, tokenizer
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке модели: {e}")
        raise e

def render_latex(text):
    # убираем лишние служебные токены (если есть)
    text = text.replace("<|assistant|>", "").strip()

    # заменяем \( \) → $
    text = re.sub(r"\\\((.*?)\\\)", r"$\1$", text)

    # заменяем \[ \] → $$
    text = re.sub(r"\\\[(.*?)\\\]", r"$$\1$$", text)

    return text


def generate_response_peft(prompt):
    """Генерируем ответ через модель"""
    model, tokenizer = load_peft_model()
    
    
    inputs = tokenizer(prompt, return_tensors="pt", padding = True).to(model.device)
    
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens = 2048,
            max_length = 2048,
            temperature=0.7
        )
        generated_tokens = output[0][inputs["input_ids"].shape[-1]:]
    formatted = render_latex(tokenizer.decode(generated_tokens, skip_special_tokens=True))

    return ((formatted))

    