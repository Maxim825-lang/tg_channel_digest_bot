# Деплой на Render (Free Web Service)

## 1. Получи BOT_TOKEN

1. Открой Telegram → найди @BotFather
2. Отправь `/newbot`
3. Придумай имя и username для бота
4. Скопируй токен вида `123456789:ABCDEFghijklmn...`

## 2. Узнай ADMIN_ID

1. Открой Telegram → найди @userinfobot
2. Отправь `/start`
3. Скопируй число из поля **Id**

## 3. Залей проект на GitHub

```bash
git init
git add .
git commit -m "Initial bot project"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## 4. Создай Web Service на Render

1. Зайди на [render.com](https://render.com) → **New** → **Web Service**
2. Подключи GitHub репозиторий
3. Render автоматически найдёт `render.yaml` и настроит сервис
4. Plan: **Free**
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `python run.py`

> **Почему Web Service, а не Background Worker?**
> Render не предоставляет бесплатный план для Background Worker.
> Web Service на Free плане доступен — бот открывает HTTP-порт,
> а Telegram polling работает параллельно в том же процессе.

## 5. Добавь Environment Variables

В настройках сервиса на Render → **Environment** обязательно задай:

| Ключ | Значение |
|------|----------|
| `BOT_TOKEN` | токен от BotFather |
| `ADMIN_ID` | твой Telegram ID |

Остальные переменные уже заданы в `render.yaml` со значениями по умолчанию.

## 6. Health Check

Render автоматически проверяет `/health` — эндпоинт возвращает:
```json
{"status": "ok", "service": "telegram-bot"}
```

Корневой путь `/` возвращает `OK`.

## 7. Расписание (APScheduler)

Отдельный Cron Job на Render **не нужен** — APScheduler внутри бота
сам управляет расписанием (дайджесты, напоминания и т.д.).

## Проверка

После деплоя:
- Напиши боту `/start` в Telegram — он должен ответить
- Открой URL сервиса в браузере — должен вернуться `OK`
- `<url>/health` — должен вернуться JSON со статусом

## Локальный запуск

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Заполни BOT_TOKEN и ADMIN_ID в .env
python run.py
# Web server: http://localhost:10000
# Telegram polling: запущен параллельно
```
