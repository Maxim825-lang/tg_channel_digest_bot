import logging
import re

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.db.database import add_channel, get_channels, set_digest_time, get_settings, ensure_user
from bot.keyboards import (
    main_menu,
    BTN_ADD_CHANNEL, BTN_MY_CHANNELS, BTN_DIGEST_TIME,
    BTN_GET_DIGEST, BTN_SETTINGS, BTN_HELP,
)
from bot.states import Form

router = Router()
logger = logging.getLogger(__name__)


def normalize_channel(text: str) -> str | None:
    text = text.strip()
    match = re.match(r"(?:https?://)?t\.me/([a-zA-Z0-9_]{5,})", text)
    if match:
        return "@" + match.group(1)
    if re.match(r"^@[a-zA-Z0-9_]{5,}$", text):
        return text
    return None


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await ensure_user(message.from_user.id)
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я помогу следить за Telegram-каналами и получать ежедневные выжимки.\n"
        "Выберите действие в меню ниже:",
        reply_markup=main_menu(),
    )


@router.message(Command("help"))
@router.message(F.text == BTN_HELP)
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❓ <b>Как пользоваться ботом:</b>\n\n"
        "1. <b>Добавить канал</b> — отправьте @username или ссылку t.me/channel\n"
        "2. <b>Мои каналы</b> — список добавленных каналов\n"
        "3. <b>Время рассылки</b> — задайте время ежедневного дайджеста (HH:MM)\n"
        "4. <b>Получить выжимку сейчас</b> — немедленно сгенерировать дайджест\n"
        "5. <b>Настройки</b> — текущие параметры\n\n"
        "Для навигации используйте кнопки меню.",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@router.message(F.text == BTN_ADD_CHANNEL)
async def btn_add_channel(message: Message, state: FSMContext):
    await state.set_state(Form.waiting_channel)
    await message.answer(
        "Отправьте ссылку на Telegram-канал или username, например:\n"
        "<code>@channelname</code> или <code>https://t.me/channelname</code>",
        parse_mode="HTML",
    )


@router.message(F.text == BTN_MY_CHANNELS)
async def btn_my_channels(message: Message, state: FSMContext):
    await state.clear()
    channels = await get_channels(message.from_user.id)
    if not channels:
        await message.answer(
            "У вас пока нет каналов.\nНажмите «➕ Добавить канал», чтобы добавить первый.",
            reply_markup=main_menu(),
        )
    else:
        lines = "\n".join(f"{i + 1}. {ch}" for i, ch in enumerate(channels))
        await message.answer(
            f"📋 <b>Ваши каналы ({len(channels)}):</b>\n\n{lines}",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )


@router.message(F.text == BTN_DIGEST_TIME)
async def btn_digest_time(message: Message, state: FSMContext):
    await state.set_state(Form.waiting_time)
    await message.answer(
        "Введите время рассылки в формате <b>HH:MM</b>, например <code>09:00</code>",
        parse_mode="HTML",
    )


@router.message(F.text == BTN_GET_DIGEST)
async def btn_get_digest(message: Message, state: FSMContext):
    await state.clear()
    channels = await get_channels(message.from_user.id)
    if not channels:
        await message.answer("Сначала добавьте каналы.", reply_markup=main_menu())
        return
    await message.answer("⏳ Генерирую выжимку...", reply_markup=main_menu())
    lines = "\n".join(f"• {ch}" for ch in channels)
    await message.answer(
        f"📰 <b>Выжимка по каналам:</b>\n\n{lines}\n\n"
        "<i>Функция генерации контента будет добавлена позже.</i>",
        parse_mode="HTML",
    )


@router.message(F.text == BTN_SETTINGS)
async def btn_settings(message: Message, state: FSMContext):
    await state.clear()
    await ensure_user(message.from_user.id)
    settings = await get_settings(message.from_user.id)
    channels = await get_channels(message.from_user.id)
    await message.answer(
        "⚙️ <b>Ваши настройки:</b>\n\n"
        f"🕐 Время рассылки: <b>{settings['digest_time']}</b>\n"
        f"🌍 Часовой пояс: <b>{settings['timezone']}</b>\n"
        f"📋 Каналов добавлено: <b>{len(channels)}</b>",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@router.message(Form.waiting_channel)
async def process_channel(message: Message, state: FSMContext):
    channel = normalize_channel(message.text or "")
    if not channel:
        await message.answer(
            "Неверный формат. Отправьте username канала, например:\n"
            "<code>@channelname</code> или <code>https://t.me/channelname</code>",
            parse_mode="HTML",
        )
        return
    await ensure_user(message.from_user.id)
    added = await add_channel(message.from_user.id, channel)
    await state.clear()
    if added:
        await message.answer(f"✅ Канал {channel} добавлен!", reply_markup=main_menu())
    else:
        await message.answer(
            f"Канал {channel} уже есть в вашем списке.",
            reply_markup=main_menu(),
        )


@router.message(Form.waiting_time)
async def process_time(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not re.match(r"^\d{2}:\d{2}$", text):
        await message.answer(
            "Неверный формат. Введите время в формате <b>HH:MM</b>, например <code>09:00</code>",
            parse_mode="HTML",
        )
        return
    hours, minutes = map(int, text.split(":"))
    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        await message.answer(
            "Время вне допустимого диапазона. Введите корректное время, например <code>09:00</code>",
            parse_mode="HTML",
        )
        return
    await ensure_user(message.from_user.id)
    await set_digest_time(message.from_user.id, text)
    await state.clear()
    await message.answer(
        f"✅ Время рассылки установлено: <b>{text}</b>",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@router.message()
async def fallback(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(
            "Я не понял команду. Используйте кнопки меню или /start",
            reply_markup=main_menu(),
        )
