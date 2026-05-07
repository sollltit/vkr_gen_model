Запуск API:

```py
uvicorn back.app:app --host 0.0.0.0 --port 8000

# ИЛИ

uvicorn back.app:app --reload    
```


Запуск streamlit:

```py
streamlit run back/client.py
```