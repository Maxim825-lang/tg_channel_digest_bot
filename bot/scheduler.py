"""
Ежедневный планировщик рассылки дайджестов.
Запускается как фоновая задача asyncio внутри run.py.
"""
import asyncio
import logging
from datetime import datetime, timezone

import aiosqlite

from bot.db.database import DB_PATH
from bot.digest import build_digest_for_user

logger = logging.getLogger(__name__)

CHUNK_SIZE = 3500


async def _get_all_users_with_time() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id, digest_time FROM users")
        rows = await cursor.fetchall()
    return [{"user_id": row[0], "digest_time": row[1]} for row in rows]


async def _send_digest(bot, user_id: int):
    try:
        digest = await build_digest_for_user(user_id)
    except Exception as e:
        logger.error("Digest build error for user %s: %s", user_id, e)
        return

    try:
        for i in range(0, max(len(digest), 1), CHUNK_SIZE):
            chunk = digest[i:i + CHUNK_SIZE]
            if chunk.strip():
                await bot.send_message(user_id, chunk, parse_mode="HTML")
    except Exception as e:
        logger.warning("Cannot send digest to user %s: %s", user_id, e)


async def scheduler_loop(bot):
    """
    Каждую минуту проверяет, нужно ли кому-то отправить дайджест.
    Совпадение по HH:MM в UTC.
    """
    logger.info("Scheduler started")
    sent_today: set[int] = set()
    last_day = datetime.now(timezone.utc).day

    while True:
        await asyncio.sleep(60)

        now = datetime.now(timezone.utc)
        current_hhmm = now.strftime("%H:%M")

        # Сброс флагов в новый день
        if now.day != last_day:
            sent_today.clear()
            last_day = now.day

        try:
            users = await _get_all_users_with_time()
        except Exception as e:
            logger.error("Scheduler: cannot read users: %s", e)
            continue

        for user in users:
            uid = user["user_id"]
            if uid in sent_today:
                continue
            if user["digest_time"] == current_hhmm:
                sent_today.add(uid)
                logger.info("Sending scheduled digest to user %s", uid)
                asyncio.create_task(_send_digest(bot, uid))
