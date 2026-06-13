import logging
import os
import re
from datetime import datetime, timezone

import aiohttp

logger = logging.getLogger(__name__)

_TG_PUBLIC_URL = "https://t.me/s/{}"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}


def _is_telethon_enabled() -> bool:
    return os.getenv("TELETHON_ENABLED", "false").lower() == "true"


def _get_telethon_config() -> tuple[int, str, str]:
    try:
        api_id = int(os.getenv("TELEGRAM_API_ID", "0"))
    except ValueError:
        api_id = 0
    api_hash = os.getenv("TELEGRAM_API_HASH", "")
    session = os.getenv("TELETHON_SESSION", "telethon_session")
    return api_id, api_hash, session


def _normalize_username(channel: str) -> str:
    """@durov / https://t.me/durov / t.me/durov → durov"""
    channel = channel.strip()
    m = re.match(r"(?:https?://)?t\.me/([a-zA-Z0-9_]+)", channel)
    if m:
        return m.group(1)
    return channel.lstrip("@")


async def fetch_public_channel_messages(
    channel_username: str,
    since_datetime: datetime,
    limit: int = 50,
) -> list[dict]:
    """
    Читает публичный канал через https://t.me/s/<username>.
    Работает только для открытых (публичных) каналов.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return [{"error": "beautifulsoup4 не установлен. Добавьте его в requirements.txt.", "channel": channel_username}]

    username = _normalize_username(channel_username)
    url = _TG_PUBLIC_URL.format(username)

    if since_datetime.tzinfo is None:
        since_datetime = since_datetime.replace(tzinfo=timezone.utc)

    try:
        async with aiohttp.ClientSession(headers=_HEADERS) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 404:
                    return [{"error": "Канал не найден на t.me/s/. Проверьте username.", "channel": channel_username}]
                if resp.status != 200:
                    return [{"error": f"t.me/s/ вернул статус {resp.status}.", "channel": channel_username}]
                html = await resp.text()
    except aiohttp.ClientError as e:
        logger.warning("Public fetch network error for %s: %s", channel_username, e)
        return [{"error": f"Сетевая ошибка при обращении к t.me/s/: {e}", "channel": channel_username}]

    soup = BeautifulSoup(html, "html.parser")
    message_divs = soup.select("div.tgme_widget_message")

    if not message_divs:
        # Страница есть, но сообщений нет — канал может быть приватным
        if "tgme_page_extra" in html or "channel is private" in html.lower():
            return [{"error": "Канал приватный или недоступен публично.", "channel": channel_username}]
        return [{"error": "Канал недоступен публично. Добавьте публичный канал или подключите Telethon.", "channel": channel_username}]

    results: list[dict] = []
    for div in message_divs:
        text_el = div.select_one(".tgme_widget_message_text")
        text = text_el.get_text("\n", strip=True) if text_el else ""
        if not text:
            continue

        time_el = div.select_one("time[datetime]")
        date_str = ""
        msg_date = None
        if time_el:
            date_str = time_el.get("datetime", "")
            try:
                msg_date = datetime.fromisoformat(date_str)
                if msg_date.tzinfo is None:
                    msg_date = msg_date.replace(tzinfo=timezone.utc)
            except ValueError:
                msg_date = None

        if msg_date and msg_date < since_datetime:
            continue

        data_post = div.get("data-post", "")
        if data_post:
            link = f"https://t.me/{data_post}"
        else:
            link = url

        views_el = div.select_one(".tgme_widget_message_views")
        views_text = views_el.get_text(strip=True) if views_el else "0"
        views = _parse_views(views_text)

        results.append({
            "channel": f"@{username}",
            "text": text,
            "date": date_str,
            "views": views,
            "link": link,
        })

        if len(results) >= limit:
            break

    if not results:
        return [{"error": "Нет сообщений за указанный период в публичном канале.", "channel": channel_username}]

    return results


def _parse_views(s: str) -> int:
    """'12.3K' → 12300, '1M' → 1000000, '42' → 42"""
    s = s.strip().replace(" ", "")
    if not s:
        return 0
    try:
        if s.endswith("K") or s.endswith("k"):
            return int(float(s[:-1]) * 1_000)
        if s.endswith("M") or s.endswith("m"):
            return int(float(s[:-1]) * 1_000_000)
        return int(s)
    except (ValueError, TypeError):
        return 0


async def _fetch_via_telethon(
    channel_username: str,
    since_datetime: datetime,
    limit: int,
) -> list[dict]:
    api_id, api_hash, session_name = _get_telethon_config()

    if api_id == 0:
        return [{"error": "TELEGRAM_API_ID not configured", "channel": channel_username}]
    if not api_hash:
        return [{"error": "TELEGRAM_API_HASH not configured", "channel": channel_username}]

    try:
        from telethon import TelegramClient
        from telethon.tl.types import Message
    except ImportError:
        return [{"error": "telethon not installed", "channel": channel_username}]

    if since_datetime.tzinfo is None:
        since_datetime = since_datetime.replace(tzinfo=timezone.utc)

    results: list[dict] = []
    username = _normalize_username(channel_username)

    try:
        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            await client.disconnect()
            return [{"error": "Telethon not authorized. Run login_telethon.py first.", "channel": channel_username}]

        try:
            entity = await client.get_entity(username)
        except Exception as e:
            await client.disconnect()
            logger.warning("Cannot get entity %s: %s", channel_username, e)
            return [{"error": f"Cannot access channel: {e}", "channel": channel_username}]

        async for msg in client.iter_messages(entity, limit=limit):
            if not isinstance(msg, Message):
                continue
            if not msg.text:
                continue

            msg_date = msg.date
            if msg_date.tzinfo is None:
                msg_date = msg_date.replace(tzinfo=timezone.utc)
            if msg_date < since_datetime:
                break

            views = getattr(msg, "views", 0) or 0
            peer_id = getattr(entity, "username", None)
            link = f"https://t.me/{peer_id}/{msg.id}" if peer_id else None

            results.append({
                "channel": f"@{username}",
                "text": msg.text,
                "date": msg_date.isoformat(),
                "views": views,
                "link": link,
            })

        await client.disconnect()

    except Exception as e:
        logger.error("Telethon error fetching %s: %s", channel_username, e)
        return [{"error": str(e), "channel": channel_username}]

    return results


async def fetch_channel_messages(
    channel_username: str,
    since_datetime: datetime,
    limit: int = 100,
) -> list[dict]:
    """
    Читает сообщения из канала.

    Приоритет:
      1. Telethon (если TELETHON_ENABLED=true и настроен)
      2. Public web fallback через t.me/s/<channel>
      3. Возвращает ошибку, если оба способа не дали результата.
    """
    if _is_telethon_enabled():
        results = await _fetch_via_telethon(channel_username, since_datetime, limit)
        real_msgs = [m for m in results if "error" not in m]
        if real_msgs:
            return results
        # Telethon не сработал — логируем и переходим к fallback
        for m in results:
            if "error" in m:
                logger.info("Telethon failed for %s (%s), trying public fallback", channel_username, m["error"])

    # Public web fallback
    logger.info("Using public web fallback for %s", channel_username)
    return await fetch_public_channel_messages(channel_username, since_datetime, limit)
