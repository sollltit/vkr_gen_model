import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
import streamlit as st

MODEL_NAME = "sollltit/qwen_1.5B_FT"


@st.cache_resource
def load_peft_model(model_name = MODEL_NAME):
    """Загружаем PEFT модель"""
    print("🔄 Загружаем PEFT модель sollltit/qwen_1.5B_FT...")
    

    try:
        # Загружаем конфиг PEFT
        config = PeftConfig.from_pretrained(model_name)
        
        base_model = AutoModelForCausalLM.from_pretrained(
            config.base_model_name_or_path,
            dtype=torch.float16,
            device_map="cpu",
            trust_remote_code=True
        )
        
        # Загружаем PEFT адаптеры
        model = PeftModel.from_pretrained(base_model, model_name)
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        print("✅ PEFT модель загружена успешно")
        return model, tokenizer
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке PEFT модели: {e}")
        raise e


def generate_response_peft(prompt):
    """Генерируем ответ через PEFT модель"""
    model, tokenizer = load_peft_model()
    
    
    inputs = tokenizer(prompt, return_tensors="pt", padding = True).to(model.device)
    
    # input_ids = inputs.input_ids.to(model.device)
    # attention_mask = inputs.attention_mask.to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens = 350,
            max_length = 2048,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Убираем промпт из ответа
    response = response[len(prompt):].strip()
    
    if "<|end|>" in response:
        response = response.split("<|end|>")[0]
    
    return response.strip()