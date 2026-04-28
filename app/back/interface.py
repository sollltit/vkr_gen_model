import streamlit as st
import requests
from datetime import datetime
from app.back.functions_for_interface import safe_load_chat_history, create_new_chat, save_chat_history, get_chat_title, delete_chat, build_conversation_context, format_math_expressions
from app.back.model_functions import generate_response_peft

SYSTEM_PROMPT = 'Ты — интеллектуальный помощник, специализирующийся на технических науках. Отвечай ТОЛЬКО на русском языке, максимально точно и с объяснением. Для генерации специальных символов и формул используй ТОЛЬКО формат LaTeX. Прописывай названия уравнений, формул и законов, если это используется в решении.'


# настройки страницы
st.set_page_config(
    page_title='Технический ассистент',
    page_icon='🤖',
    layout='wide',
    initial_sidebar_state='expanded'
)

# заголовок приложения
st.title('Технический ассистент 𖠌')
st.divider()


# инициализация данных
if 'chat_history_loaded' not in st.session_state:
    st.session_state.chat_history_loaded = True
    st.session_state.chat_sessions = safe_load_chat_history()
    
    if st.session_state.chat_sessions:
        st.session_state.current_chat_id = list(st.session_state.chat_sessions.keys())[0]
    else:
        st.session_state.current_chat_id = None

if 'new_chat_clicked' not in st.session_state:
    st.session_state.new_chat_clicked = False

if 'processing_message' not in st.session_state:
    st.session_state.processing_message = False

# боковая панель
with st.sidebar:
    st.title('💭 История чатов')
    # кнопка для создания нового чата
    if st.button(' ➕ Создать новый чат', use_container_width=True):
        create_new_chat()
    
    st.divider()
    
    if st.session_state.chat_sessions:
        for chat_id in list(st.session_state.chat_sessions.keys()):
            chat = st.session_state.chat_sessions[chat_id]
            col1, col2 = st.columns([4, 1])

            # кнопки для переключения чатов
            with col1:
                if st.button(
                    f'📌 {chat["title"]}', 
                    key=f'btn_{chat_id}',
                    use_container_width=True
                ):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()
            
            with col2:
                if st.button('⌦', key=f'del_{chat_id}'): # кнопка удаления чата
                    delete_chat(chat_id)
    
    else:
        st.info('Чатов нет. Создайте новый')
    
    st.divider()
    
    # вывод информации о том когда чат был создан
    if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_sessions:
        current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]
        st.text(f'Чат создан: {current_chat["created_at"].strftime("%d.%m.%y %H:%M")}') # вывод даты и времени

    st.divider()

    # переключатель темы приложения
    st.title("🎨 Настройки темы")
    theme = st.selectbox(
        "Цветовая схема:",
        ["Тёмная", "Светлая"]
    )
    # по умолчанию стоит тёмная
    # характеристики для светлой темы
    if theme == "Светлая":
        st.markdown("""
        <style>
        .main { background: #FFFFFF; }
        .stApp { background: #FFFFFF; }
        section[data-testid="stSidebar"] {
            background: #DAE5F2 !important;
            border-right: 5px solid #B8B8B8;
        }
        h1, h2, h3 { color: #940C3A !important;}
        p, div, span { color: #000000 !important; }
        .stButton>button { 
            background: #B8C2CF; 
            color: #FFFFFF !important;
            border-radius: 12px;
        }
        div[data-baseweb="select"] > div {
            background-color: #DAE5F2 !important;
        }
        div[data-baseweb="popover"] div {
            background-color: #DAE5F2 !important;
        }
        </style>
        """, unsafe_allow_html=True)

# основная область
with st.container():
    # пользователь сразу видит последний чат с моделью
    if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chat_sessions:
        current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]
        st.title(f'✎𓂃 {current_chat["title"]}')
    # вывод текста если ещё не создано ни одного чата
    else:
        st.title('Технический ассистент 🤖')
        st.markdown('Задайте вопрос.')
    
    # автоматическое создание первого чата
    if not st.session_state.current_chat_id and not st.session_state.chat_sessions:
        create_new_chat()
        st.rerun()
    
    # область чата
    if st.session_state.current_chat_id:
        current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]
        
        # показ сообщений в чате
        for message in current_chat["messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # поле для ввода вопроса
        if prompt := st.chat_input('Задайте вопрос...'):
            # добавление вопроса пользователя в историю
            current_chat["messages"].append({"role": "user", "content": prompt})
            
            # обновление заголовка чата при первом сообщении
            if len(current_chat["messages"]) == 1:
                current_chat["title"] = get_chat_title(current_chat["messages"])
            
            # сохраняем историю
            save_chat_history()
            
            # флаг обработки
            st.session_state.processing_message = True
            st.rerun()
        
        # генерация ответа
        if (current_chat["messages"] and 
            current_chat["messages"][-1]["role"] == "user" and
            st.session_state.processing_message):
            
            # сбор контекста (прошлые соо)
            conversation_context = build_conversation_context(current_chat["messages"])
            
            with st.chat_message('assistant'):
                with st.spinner('Думаю...'):
                    # работа модели
                    try:
                        full_response = generate_response_peft(conversation_context)

                        # if response.status_code == 200:
                        #     result = response.json()
                        #     full_response = result['response']
                            
                            # форматирование математических выражений
                        formatted_response = format_math_expressions(full_response)

                            # вывод ответа
                        st.markdown(formatted_response)
                            
                            # добавление ответа в историю
                        current_chat['messages'].append({"role": "assistant", "content": formatted_response})
                            
                            # сохранение в бд
                        save_chat_history()
                        
                        # # вывод ошибки если она произойдёт
                        # else:
                        #     error_msg = f'Ошибка API: {response.status_code}'
                        #     st.error(error_msg)
                        #     current_chat["messages"].append({"role": "assistant", "content": error_msg})
                        #     save_chat_history() # сохранение
                            
                    # except requests.exceptions.Timeout:
                    #     # вывод сообщения в случае, если модель не успела сгенерировать ответ
                    #     error_msg = 'Модель не ответила в течение 5 минут. Попробуйте задать более простой вопрос.'
                    #     st.error(error_msg)
                    #     current_chat["messages"].append({"role": "assistant", "content": error_msg})
                    #     save_chat_history() # сохранение
                        
                    except Exception as e:
                        error_msg = f'Произошла ошибка: {e}'
                        st.error(error_msg)
                        current_chat['messages'].append({"role": "assistant", "content": error_msg})
                        save_chat_history() # сохранение
             
            # флаг
            st.session_state.processing_message = False
            st.rerun() # перезапуск