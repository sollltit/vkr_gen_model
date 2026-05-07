__________
# *API*

Запуск API:

```bash
uvicorn back.app:app --host 0.0.0.0 --port 8000

# ИЛИ

uvicorn back.app:app --reload    
```

___________
*Запуск streamlit (тестовый интерфейс):*

```py
streamlit run back/client.py
```

_______________________________________

# *Node.js*

1.    Создание проекта

```bash
    npx create-next-app@latest ai-chat 
    cd ai-chat 
```

2.   Установка библиотек

```bash
    npm install axios react-markdown remark-gfm rehype-katex katex lucide-react zustand 
```

3.   Установка shadcn/ui 

```bash
    npx shadcn@latest init

    -> Radix
    -> Nova - Lucide / Geist
```

4.   Добавление готовых UI-компонентов на базе shadcn/ui

```bash
    npx shadcn@latest add button card scroll-area textarea
```

5.   Запуск 

```bash
    npm run dev
```