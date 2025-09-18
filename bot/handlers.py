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
        f"Здравствуйте, {message.from_user.full_name}!\n\n"
        "Я ваш личный ассистент. Я могу помочь с:\n"
        "- 🌦️ Прогнозом погоды\n"
        "- 📰 Последними новостями\n\n"
        "Просто напишите мне, что вас интересует."
    )


@router.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """
    This handler receives messages with `/help` command
    and shows the main menu.
    """
    await message.answer(
        "Чем я могу вам помочь?",
        reply_markup=create_main_menu_keyboard()
    )


from core.intent_detector import detect_intent, model
from features.weather_feature import handle_weather_intent, handle_set_city_intent
from features.news_feature import handle_news_intent
from core.assistant_prompt import ASSISTANT_PROMPT


async def get_conversational_response(user_text: str) -> str:
    """
    Generates a conversational response using the Gemini model.
    """
    if not model:
        return "Извините, у меня сейчас технические неполадки. Я не могу ответить."

    full_prompt = f"{ASSISTANT_PROMPT}\n\nПользователь: \"{user_text}\"\nАссистент:"
    try:
        response = await model.generate_content_async(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error during conversational response generation: {e}")
        return "Произошла ошибка при обработке вашего запроса."


@router.callback_query()
async def process_callback_query(callback_query: CallbackQuery):
    """
    This handler processes all callback queries from inline keyboards.
    """
    await callback_query.answer()  # Acknowledge the button press
    await callback_query.message.edit_text(
        f"Вы выбрали: {callback_query.data}. Эта функция скоро появится!"
    )


@router.message()
async def message_handler(message: Message) -> None:
    """
    This handler processes all text messages.
    It first tries to detect a specific 'tool-using' intent.
    If no specific intent is found, it uses a conversational AI model to respond.
    """
    # Bypass intent detection for single-word messages that are likely greetings
    if message.text and len(message.text.split()) == 1:
        if message.text.lower() in ["привет", "здравствуй", "здравствуйте", "hi", "hello"]:
            response_message = await get_conversational_response(message.text)
            await message.answer(response_message)
            return

    intent_data = await detect_intent(message.text)
    intent = intent_data.get("intent")
    entities = intent_data.get("entities", {})

    response_message = ""

    if intent == "weather":
        response_message = await handle_weather_intent(message, entities)
    elif intent == "set_city":
        response_message = await handle_set_city_intent(message, entities)
    elif intent == "news":
        response_message = await handle_news_intent(message, entities)
    else:
        # If no specific tool intent, treat as a general conversation
        response_message = await get_conversational_response(message.text)

    await message.answer(response_message)
