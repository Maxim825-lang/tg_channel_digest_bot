from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

BTN_ADD_CHANNEL = "➕ Добавить канал"
BTN_MY_CHANNELS = "📋 Мои каналы"
BTN_DIGEST_TIME = "⏰ Время рассылки"
BTN_GET_DIGEST = "📰 Получить выжимку сейчас"
BTN_SETTINGS = "⚙️ Настройки"
BTN_HELP = "❓ Помощь"


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_ADD_CHANNEL), KeyboardButton(text=BTN_MY_CHANNELS)],
            [KeyboardButton(text=BTN_DIGEST_TIME), KeyboardButton(text=BTN_GET_DIGEST)],
            [KeyboardButton(text=BTN_SETTINGS), KeyboardButton(text=BTN_HELP)],
        ],
        resize_keyboard=True,
    )
