# tg_bot_20260613_235649

**Тип:** Telegram-бот с web-интерфейсом для Render Free Web Service
**Стек:** Python 3.10+ · aiogram 3 · aiosqlite · aiohttp

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
# Web server: http://localhost:10000  (GET / и GET /health)
# Telegram polling: запущен параллельно
```

## Структура проекта

```
.
├── run.py                # Точка входа: web server + bot polling
├── requirements.txt
├── render.yaml           # Render Web Service конфигурация
├── .env.example
├── bot/
│   ├── main.py           # Инициализация aiogram
│   ├── handlers.py       # Обработчики команд
│   ├── keyboards.py      # Клавиатуры
│   ├── states.py         # FSM состояния
│   └── db/
│       └── database.py   # SQLite операции
└── data/
    └── bot.db            # Создаётся автоматически
```

## .env

```
BOT_TOKEN=your_token_here
ADMIN_ID=your_telegram_id_here
```

## Деплой на Render

См. [DEPLOY_RENDER.md](DEPLOY_RENDER.md).

Краткая инструкция:
1. **New → Web Service** (не Background Worker — он платный)
2. Подключи репозиторий — `render.yaml` настроит всё автоматически
3. Задай `BOT_TOKEN` и `ADMIN_ID` в Environment Variables
4. Free план доступен для Web Service
# redeploy Sun Jun 14 00:22:56 MSK 2026
