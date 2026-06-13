# Деплой на Render

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

## 4. Создай Background Worker на Render

1. Зайди на [render.com](https://render.com) → **New** → **Background Worker**
2. Подключи GitHub репозиторий
3. Render автоматически найдёт `render.yaml` и настроит сервис

## 5. Добавь Environment Variables

В настройках сервиса на Render → **Environment**:

| Ключ | Значение |
|------|----------|
| `BOT_TOKEN` | токен от BotFather |
| `ADMIN_ID` | твой Telegram ID |

## 6. Cron Job (опционально)

Если нужна периодическая задача (рассылка, напоминания):

1. Render → **New** → **Cron Job**
2. Command: `python cron.py`
3. Schedule: например `0 9 * * *` (каждый день в 09:00 UTC)

## Проверка

После деплоя напиши боту `/start` в Telegram — он должен ответить.
