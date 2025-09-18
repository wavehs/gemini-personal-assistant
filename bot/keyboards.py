from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def create_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Creates the main menu inline keyboard.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🌦️ Weather", callback_data="feature_weather"),
        InlineKeyboardButton(text="📰 News", callback_data="feature_news")
    )
    builder.row(
        InlineKeyboardButton(text="🚌 Transport", callback_data="feature_transport"),
        InlineKeyboardButton(text="🛒 Pantry", callback_data="feature_pantry")
    )
    builder.row(
        InlineKeyboardButton(text="📅 Calendar", callback_data="feature_calendar")
    )
    return builder.as_markup()
