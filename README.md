# vkr_gen_model

Модель: Qwen/Qwen2.5-7B-Instruct

```bash

vkr_gen_model/
        │
        ├── README.md
        ├── requirements.txt # зависимости
        ├── package-lock.json 
        │
        ├── chatbot/ 
        │ └── ai-chat/
        │       └── next/ 
        │       └── app/ 
        │       └── components/ 
        │       └── lib/ 
        │       └── node_modules/ 
        │       └── public/
        │       └── store/ 
        │
        ├── data/ # датасеты
        │
        ├── test_interface/ # черновой интерфейс
        │
        ├── valid_visual/ # визуализация результатов обучения 
        │
        ├── back/ # бэкенд проекта
        │       └── .env 
        │       └── app.py # основной файл api 
        │       └── auth.py # авторизация 
        │       └── client.py # черновой интерфейс про проверки api 
        │       └── database.py # бд 
        │       └── model_functions.py # загрузка модели и генерация
        │       └── models.py # модели бд
        │       └── text_form.py # форматирование спец. символов в генерации
        │
        ├── data.ipynb # обработка ru датасетов
        ├── data_en.ipynb # обработка en датасета
        ├── model_train.ipynb # обучение модели на англ. данных
        ├── model_train_rus.ipynb # обучение модели на рус. данных
        ├── tests_gen_model.ipynb # тестирование генеративной модели
        │
        ├── chat.db # файл базы данных SQLite
        │
        ├── data_en_training.json # обучающие данные на английском языке
        ├── data_ru_training.json # обучающие данные на русском языке
        │
        ├── db.png # схема бд
        ├── gen_res.md # файл с результатами генерации
        ├── instruction.md 
        └── questions.txt # вопросы для тестирования/валидации
```