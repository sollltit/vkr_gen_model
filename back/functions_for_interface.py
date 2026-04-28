import streamlit as st
import json
import uuid
from datetime import datetime
import time
import os
import re
from dotenv import load_dotenv


load_dotenv()

# файл для сохранения истории чатов
CHAT_HISTORY_FILE = "chat_history.json"

def safe_load_chat_history():

    """
    Функция для загрузки истории сообщений
    """

    try:
        if not os.path.exists(CHAT_HISTORY_FILE):
            return {}
        # чтение файла    
        with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        if not content:
            return {}
            
        data = json.loads(content)
        
        # проверка структуры данных
        if not isinstance(data, dict):
            raise ValueError('Некорректная структура данных')
            
        # конвертируем даты
        for chat_id, chat_data in data.items():
            if isinstance(chat_data, dict) and 'created_at' in chat_data:
                try:
                    chat_data['created_at'] = datetime.fromisoformat(chat_data['created_at'])
                except (ValueError, TypeError):
                    chat_data['created_at'] = datetime.now()
                    
        return data # возвращаем данные
    
    # если происходит ошибка и файл не находится, создаётся новый файл
    except (json.JSONDecodeError, ValueError) as e:
        st.error(f'Не удалось загрузить историю чатов. Создаю новую. Ошибка: {e}')
        try:
            # создание нового файла для бд
            with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        except:
            pass
        return {}
        
    except Exception as e:
        st.error(f'Неожиданная ошибка при загрузке истории: {e}') # вывод инфы об ошибке 
        return {}


def save_chat_history():

    """
    Функция для сохранения истории
    """

    try:
        # подготовка данных к сохранению
        data_to_save = {}
        for chat_id, chat_data in st.session_state.chat_sessions.items():
            # проверка того что данные корректны
            if isinstance(chat_data, dict) and 'messages' in chat_data:
                data_to_save[chat_id] = {
                    "title": chat_data.get("title", "Новый чат"),
                    "messages": chat_data.get("messages", []),
                    "created_at": chat_data.get("created_at", datetime.now()).isoformat()
                }
        
        # сохранение во временный файл
        temp_file = f"{CHAT_HISTORY_FILE}.temp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        
        # замена основного файла, если данные успешно сохранены
        os.replace(temp_file, CHAT_HISTORY_FILE)
        
    except Exception as e:
        st.error(f'Ошибка сохранения истории: {e}')

# обработка математических выражений 
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

SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")


def build_conversation_context(messages, max_context_messages=10, system_prompt = SYSTEM_PROMPT):

    """
    Функция для построения контекста
    """
    if not messages:
        return "" # возвращается пустая строка если сообщений в чате ещё нет
    
    # берутся последние N сообщений 
    recent_messages = messages[-max_context_messages:] if len(messages) > max_context_messages else messages

    # сбор контекста
    conversation = system_prompt
    for message in recent_messages:
        if message["role"] == "user":
            conversation += f"Вопрос: {message['content']}\n"
        elif message["role"] == "assistant":
            conversation += f"Ответ: {message['content']}\n"
    
    return conversation


# создание нового чата
def create_new_chat():

    """
    Функция для создания нового чата
    """

    chat_id = str(uuid.uuid4())[:8]
    # инфа о чате
    st.session_state.chat_sessions[chat_id] = {
        "title": f"Чат от {datetime.now().strftime('%H:%M')}",
        "messages": [],
        "created_at": datetime.now()
    }
    st.session_state.current_chat_id = chat_id
    st.session_state.new_chat_clicked = True
    save_chat_history() # сохранение
    st.rerun() # перезапуск

# удаление чата
def delete_chat(chat_id):

    """
    Функция для удаления чата
    """

    if chat_id in st.session_state.chat_sessions:
        del st.session_state.chat_sessions[chat_id] # удаляем чат
        if st.session_state.current_chat_id == chat_id:
            if st.session_state.chat_sessions:
                st.session_state.current_chat_id = list(st.session_state.chat_sessions.keys())[0]
            else:
                st.session_state.current_chat_id = None
        save_chat_history() # сохранение
        st.rerun() # перезапуск

# название чата
def get_chat_title(messages):

    """
    Функция для вывода названия чата
    """

    if messages:
        # в графе с названием чата будут выведены первые 30 символов первого сообщения в чате
        first_message = messages[0]['content'][:30]
        return f'{first_message}...' if len(first_message) == 30 else first_message
    else: return 'Новый чат' # вывод если сообщений в чате ещё нет
