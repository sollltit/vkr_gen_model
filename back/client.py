import streamlit as st
import requests
import re

API_URL = "http://localhost:8000/chat"

st.set_page_config(page_title="тест", layout="centered")

st.title("Chat 💬 ")



# def split_text_and_math(text: str):
#     """
#     Разбивает текст на части: обычный текст и LaTeX формулы $$...$$
#     """
#     parts = re.split(r'(\$\$.*?\$\$)', text, flags=re.DOTALL)
#     return parts

# def render_response(text: str):
#     parts = split_text_and_math(text)

#     for part in parts:
#         if part.startswith("$$") and part.endswith("$$"):
#             formula = part.strip("$").strip()
#             st.latex(formula)
#         else:
#             st.markdown(part)


# история чата
if "messages" not in st.session_state:
    st.session_state.messages = []

# отображение истории
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ввод пользователя
user_input = st.chat_input("Введите сообщение...")

if user_input:
    # показываем user
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # запрос к API 
    with st.chat_message("assistant"):
        with st.spinner("Генерация..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"messages": st.session_state.messages},
                    timeout=420
                )

                answer = response.json()["response"]
                if response.status_code != 200:
                    answer = f"Ошибка сервера: {response.text}"
                else:
                    try:
                        answer = response.json()["response"]
                    except Exception:
                        answer = f"Некорректный ответ API: {response.text}"

            except Exception as e:
                answer = f"Ошибка: {e}"

            st.markdown(answer, unsafe_allow_html=False)
            

    # сохраняем ответ
    st.session_state.messages.append({"role": "assistant", "content": answer})