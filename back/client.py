import streamlit as st
import requests

API_URL = "http://localhost:8000/chat"

st.set_page_config(page_title="Qwen Chat Test", layout="centered")

st.title("💬 Qwen2.5-7B Chat Test UI")

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

    # запрос к API (модель НЕ загружается здесь)
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

            st.markdown(answer)

    # сохраняем ответ
    st.session_state.messages.append({"role": "assistant", "content": answer})