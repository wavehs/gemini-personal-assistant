from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.keyboards import create_main_menu_keyboard

router = Router()

@router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(
        f"Hello, {message.from_user.full_name}!\n\n"
        "I am your personal assistant. I can help you with:\n"
        "- 🌦️ Weather forecasts\n"
        "- 📰 Latest news\n"
        "- 🚌 Transport routes\n"
        "- 🛒 Pantry and shopping lists\n"
        "- 📅 Google Calendar events\n\n"
        "Type /help to see all available commands and features."
    )

@router.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """
    This handler receives messages with `/help` command
    and shows the main menu.
    """
    await message.answer(
        "How can I help you today?",
        reply_markup=create_main_menu_keyboard()
    )

from aiogram.types import Message
from core.intent_detector import detect_intent
from features.weather_feature import handle_weather_intent

@router.callback_query()
async def process_callback_query(callback_query: CallbackQuery):
    """
    This handler processes all callback queries from inline keyboards.
    """
    await callback_query.answer() # Acknowledge the button press
    await callback_query.message.edit_text(
        f"You selected the option: {callback_query.data}. Feature coming soon!"
    )

@router.message()
async def message_handler(message: Message) -> None:
    """
    This handler processes all text messages and uses the intent detector.
    """
    intent_data = await detect_intent(message.text)
    intent = intent_data.get("intent")
    entities = intent_data.get("entities", {})

    response_message = "I'm not sure how to handle that."

    if intent == "weather":
        response_message = await handle_weather_intent(entities)
    # Future intents will be handled here
    # elif intent == "commute":
    #     response_message = await handle_commute_intent(entities)

    await message.answer(response_message)
