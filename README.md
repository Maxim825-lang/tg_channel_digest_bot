# tg_bot_20260613_235649

**Задача:** залей на рендер+крон
**Тип:** generic
**Стек:** Python 3.10+ · aiogram 3 · aiosqlite

## Быстрый старт

```bash
# 1. Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 2. Установите зависимости
pip install -r requirements.txt

# 3. Заполните .env
cp .env.example .env
# Вставьте BOT_TOKEN от @BotFather
# Вставьте ADMIN_ID (ваш Telegram ID — узнать через @userinfobot)

# 4. Запуск
python run.py
```

## Структура проекта
```
.
├── run.py                # Точка входа
├── requirements.txt
├── .env.example
├── bot/
│   ├── main.py           # Инициализация aiogram
│   ├── handlers.py       # Обработчики команд
│   ├── keyboards.py      # Клавиатуры
│   ├── states.py         # FSM состояния
│   └── db/
│       └── database.py   # SQLite операции
└── data/
    └── applications.db   # Создаётся автоматически
```

## .env
```
BOT_TOKEN=your_token_here
ADMIN_ID=your_telegram_id_here
```
