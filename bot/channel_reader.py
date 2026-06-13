import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _is_telethon_enabled() -> bool:
    return os.getenv("TELETHON_ENABLED", "false").lower() == "true"


def _get_telethon_config() -> tuple[int, str, str]:
    """Returns (api_id, api_hash, session_name). api_id=0 means not configured."""
    try:
        api_id = int(os.getenv("TELEGRAM_API_ID", "0"))
    except ValueError:
        api_id = 0
    api_hash = os.getenv("TELEGRAM_API_HASH", "")
    session = os.getenv("TELETHON_SESSION", "telethon_session")
    return api_id, api_hash, session


async def fetch_channel_messages(
    channel_username: str,
    since_datetime: datetime,
    limit: int = 100,
) -> list[dict]:
    """
    Читает сообщения из канала через Telethon.

    Возвращает список dict:
      {"channel", "text", "date", "views", "link", "error"(только при ошибке)}

    Если Telethon не включён — возвращает список с одним элементом-ошибкой.
    """
    if not _is_telethon_enabled():
        return [{"error": "Telethon disabled", "channel": channel_username}]

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

    # since_datetime должен быть aware UTC
    if since_datetime.tzinfo is None:
        since_datetime = since_datetime.replace(tzinfo=timezone.utc)

    results: list[dict] = []
    username = channel_username.lstrip("@")

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
            link = None
            peer_id = getattr(entity, "username", None)
            if peer_id:
                link = f"https://t.me/{peer_id}/{msg.id}"

            results.append({
                "channel": channel_username,
                "text": msg.text,
                "date": msg_date.isoformat(),
                "views": views,
                "link": link,
            })

        await client.disconnect()

    except Exception as e:
        logger.error("Error fetching %s: %s", channel_username, e)
        return [{"error": str(e), "channel": channel_username}]

    return results
