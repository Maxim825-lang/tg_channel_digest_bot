import asyncio
import json
import logging
import os
import sys

from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def handle_root(request):
    return web.Response(text="OK")


async def handle_health(request):
    return web.Response(
        text=json.dumps({"status": "ok", "service": "telegram-bot"}),
        content_type="application/json"
    )


async def run_web_server(port: int):
    app = web.Application()
    app.router.add_get("/", handle_root)
    app.router.add_get("/health", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Web server listening on 0.0.0.0:{port}")
    await asyncio.Event().wait()


async def run_all():
    token = os.getenv("BOT_TOKEN")
    if not token or token == "PASTE_TOKEN_HERE":
        logger.error("BOT_TOKEN не задан! Установите переменную окружения BOT_TOKEN.")
        sys.exit(1)

    port = int(os.getenv("PORT", 10000))
    logger.info(f"Starting: web server on port {port} + Telegram polling")

    from bot.main import main as bot_main
    await asyncio.gather(
        run_web_server(port),
        bot_main(),
    )


if __name__ == "__main__":
    asyncio.run(run_all())
