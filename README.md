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

# Telethon (для чтения чужих каналов)
TELETHON_ENABLED=false
TELEGRAM_API_ID=0
TELEGRAM_API_HASH=

# OpenAI (необязательно)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

## Как включить реальный сбор каналов (Telethon)

1. Получите `TELEGRAM_API_ID` и `TELEGRAM_API_HASH` на [my.telegram.org](https://my.telegram.org) → App configuration.

2. Пропишите в `.env`:
   ```
   TELETHON_ENABLED=true
   TELEGRAM_API_ID=123456
   TELEGRAM_API_HASH=abcdef...
   TELETHON_SESSION=telethon_session
   ```

3. Авторизуйтесь (один раз локально):
   ```bash
   python login_telethon.py
   ```
   Введите номер телефона и код из Telegram. Создастся файл `telethon_session.session`.

4. Запустите бота:
   ```bash
   python run.py
   ```

5. Добавьте каналы через бота и нажмите «📰 Получить выжимку сейчас».

### OpenAI (необязательно)

Если хотите AI-выжимку вместо extractive summary — пропишите:
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### Render и Telethon

Telethon хранит сессию в файле `.session`. На Render Free нет persistent disk,
поэтому Telethon лучше использовать **только локально** или подключить Render Disk.
Для production рекомендуется хранить session как base64 в env и загружать через
[StringSession](https://docs.telethon.dev/en/stable/modules/sessions.html).

## Деплой на Render

См. [DEPLOY_RENDER.md](DEPLOY_RENDER.md).

Краткая инструкция:
1. **New → Web Service** (не Background Worker — он платный)
2. Подключи репозиторий — `render.yaml` настроит всё автоматически
3. Задай `BOT_TOKEN` и `ADMIN_ID` в Environment Variables
4. Free план доступен для Web Service
# redeploy Sun Jun 14 00:22:56 MSK 2026
