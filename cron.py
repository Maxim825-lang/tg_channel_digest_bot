"""
Cron job — запускается по расписанию Render Cron Jobs.
Добавьте сюда логику: ежедневная рассылка, очистка БД и т.д.
"""
import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_cron():
    logger.info("Cron job запущен")
    # TODO: добавьте вашу логику здесь
    logger.info("Cron job завершён")


if __name__ == "__main__":
    asyncio.run(run_cron())
