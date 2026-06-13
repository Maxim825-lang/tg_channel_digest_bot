import logging
import os
from datetime import datetime, timedelta, timezone

from bot.channel_reader import fetch_channel_messages
from bot.db.database import get_channels
from bot.summarizer import KEYWORDS, summarize_messages, _score

logger = logging.getLogger(__name__)

MIN_TEXT_LEN = 30


async def build_digest_for_user(user_id: int) -> str:
    channels = await get_channels(user_id)
    if not channels:
        return "У вас нет добавленных каналов. Добавьте каналы через меню."

    since = datetime.now(timezone.utc) - timedelta(hours=24)

    all_messages: list[dict] = []
    errors: list[str] = []

    for channel in channels:
        msgs = await fetch_channel_messages(channel, since_datetime=since, limit=100)
        for m in msgs:
            if "error" in m:
                errors.append(f"{channel}: {m['error']}")
            else:
                all_messages.append(m)

    if not all_messages and errors:
        error_list = "\n".join(f"• {e}" for e in errors)
        return (
            "⚠️ Не удалось получить сообщения ни из одного канала.\n\n"
            f"{error_list}\n\n"
            "Возможные причины: канал приватный, нет сообщений за сутки, "
            "Telegram ограничил публичную страницу.\n"
            "Для приватных каналов подключите Telethon (см. README)."
        )

    # Убираем дубликаты по тексту
    seen_texts: set[str] = set()
    unique: list[dict] = []
    for m in all_messages:
        key = m.get("text", "")[:100]
        if key not in seen_texts:
            seen_texts.add(key)
            unique.append(m)

    # Фильтруем слишком короткие
    filtered = [m for m in unique if len(m.get("text", "")) >= MIN_TEXT_LEN]

    if not filtered:
        return "За последние 24 часа важных сообщений не найдено."

    # Топ по score
    scored = sorted(filtered, key=_score, reverse=True)
    top = scored[:15]

    result = await summarize_messages(top)

    if errors:
        error_list = "\n".join(f"• {e}" for e in errors[:5])
        result += f"\n\n⚠️ <i>Часть каналов недоступна:</i>\n{error_list}"

    return result
