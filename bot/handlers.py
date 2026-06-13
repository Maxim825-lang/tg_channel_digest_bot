import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from bot.keyboards import main_menu

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\nЯ готов помочь. Напишите что-нибудь.",
        reply_markup=main_menu(),
    )


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message):
    await message.answer(
        "📋 <b>Доступные команды:</b>\n"
        "/start — начать\n"
        "/help — помощь",
        parse_mode="HTML",
    )


@router.message()
async def echo(message: Message):
    await message.answer(f"Вы написали: {message.text}")
