import os
import aiosqlite

# render.yaml exposes DATABASE_PATH; fall back to local path for development
DB_PATH = os.getenv("DATABASE_PATH", os.getenv("DB_PATH", "data/bot.db"))


async def init_db():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                digest_time TEXT NOT NULL DEFAULT '09:00',
                timezone TEXT NOT NULL DEFAULT 'UTC'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel TEXT NOT NULL,
                UNIQUE(user_id, channel)
            )
        """)
        await db.commit()


async def ensure_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,)
        )
        await db.commit()


async def add_channel(user_id: int, channel: str) -> bool:
    """Returns True if added, False if already exists."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO channels (user_id, channel) VALUES (?, ?)",
                (user_id, channel),
            )
            await db.commit()
        return True
    except aiosqlite.IntegrityError:
        return False


async def get_channels(user_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT channel FROM channels WHERE user_id = ? ORDER BY id",
            (user_id,),
        )
        rows = await cursor.fetchall()
    return [row[0] for row in rows]


async def set_digest_time(user_id: int, digest_time: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET digest_time = ? WHERE user_id = ?",
            (digest_time, user_id),
        )
        await db.commit()


async def get_settings(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT digest_time, timezone FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
    if row:
        return {"digest_time": row[0], "timezone": row[1]}
    return {"digest_time": "09:00", "timezone": "UTC"}
