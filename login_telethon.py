"""
Авторизация Telethon — запускать один раз локально.
Создаёт файл {TELETHON_SESSION}.session для последующего использования ботом.

Запуск:
    python login_telethon.py
"""
import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv()


async def main():
    api_id_raw = os.getenv("TELEGRAM_API_ID", "0")
    api_hash = os.getenv("TELEGRAM_API_HASH", "")
    session_name = os.getenv("TELETHON_SESSION", "telethon_session")

    try:
        api_id = int(api_id_raw)
    except ValueError:
        print("Ошибка: TELEGRAM_API_ID должен быть числом.")
        sys.exit(1)

    if api_id == 0 or not api_id_raw.strip():
        print(
            "Ошибка: TELEGRAM_API_ID не задан.\n"
            "Получите API_ID и API_HASH на https://my.telegram.org → App configuration\n"
            "и пропишите их в .env файле."
        )
        sys.exit(1)

    if not api_hash:
        print(
            "Ошибка: TELEGRAM_API_HASH не задан.\n"
            "Получите API_ID и API_HASH на https://my.telegram.org → App configuration\n"
            "и пропишите их в .env файле."
        )
        sys.exit(1)

    try:
        from telethon import TelegramClient
        from telethon.errors import SessionPasswordNeededError
    except ImportError:
        print("Ошибка: telethon не установлен. Выполните: pip install telethon")
        sys.exit(1)

    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"Уже авторизованы как: {me.first_name} (id={me.id})")
        await client.disconnect()
        return

    phone = input("Введите номер телефона (в формате +7...): ").strip()
    await client.send_code_request(phone)

    code = input("Введите код из Telegram (цифры): ").strip()
    try:
        await client.sign_in(phone, code)
    except SessionPasswordNeededError:
        password = input("Введите пароль двухфакторной аутентификации: ").strip()
        await client.sign_in(password=password)

    me = await client.get_me()
    print(f"Успешная авторизация: {me.first_name} (id={me.id})")
    print(f"Telethon session saved → {session_name}.session")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
