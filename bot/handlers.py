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

from core.google_auth import generate_auth_url, get_refresh_token
from bot.user_data import update_user_data

@router.message(Command("authorize_google"))
async def command_authorize_google(message: Message) -> None:
    """
    Starts the Google Calendar authorization process.
    """
    auth_url, state = generate_auth_url()
    if auth_url:
        response = (
            "Чтобы я мог читать ваше расписание, пожалуйста, перейдите по этой ссылке, "
            "разрешите доступ и скопируйте полученный код.\n\n"
            f"{auth_url}\n\n"
            "Затем отправьте мне этот код командой: /submit_google_code [вставьте код сюда]"
        )
    else:
        response = (
            "Не удалось начать процесс авторизации. "
            "Пожалуйста, убедитесь, что файл `client_secrets.json` настроен правильно."
        )
    await message.answer(response)


@router.message(Command("submit_google_code"))
async def command_submit_google_code(message: Message) -> None:
    """
    Receives the authorization code from the user and fetches the refresh token.
    """
    code = message.text.split(" ", 1)[-1]
    if not code or code == "/submit_google_code":
        await message.answer("Пожалуйста, укажите код после команды. Например: /submit_google_code [код]")
        return

    user_id = message.from_user.id
    refresh_token = get_refresh_token(code)

    if refresh_token:
        update_user_data(user_id, 'google_refresh_token', refresh_token)
        await message.answer("Отлично! Авторизация прошла успешно. Теперь я могу получить доступ к вашему календарю.")
    else:
        await message.answer("Не удалось получить токен. Пожалуйста, попробуйте снова, получив новый код авторизации через /authorize_google.")


def _parse_location_args(text: str) -> dict | None:
    """Helper to parse location arguments from a command."""
    try:
        # Remove the command part, e.g., "/set_home "
        args_str = text.split(" ", 1)[1]
        # Split by '|' to separate address and stop name
        parts = [p.strip() for p in args_str.split('|')]
        if len(parts) == 2:
            return {"address": parts[0], "stop": parts[1]}
        elif len(parts) == 1:
            return {"address": parts[0], "stop": None}
        return None
    except IndexError:
        return None

@router.message(Command("set_home"))
async def command_set_home(message: Message) -> None:
    """Saves the user's home address and nearest bus stop."""
    location_data = _parse_location_args(message.text)
    if not location_data:
        await message.answer(
            "Пожалуйста, укажите ваш домашний адрес и, по желанию, название остановки.\n"
            "Формат: /set_home [адрес] | [название остановки]"
        )
        return

    update_user_data(message.from_user.id, 'home_location', location_data)
    await message.answer(f"Ваш домашний адрес сохранен: {location_data['address']}")

@router.message(Command("set_university"))
async def command_set_university(message: Message) -> None:
    """Saves the user's university address and nearest bus stop."""
    location_data = _parse_location_args(message.text)
    if not location_data:
        await message.answer(
            "Пожалуйста, укажите адрес университета и, по желанию, название остановки.\n"
            "Формат: /set_university [адрес] | [название остановки]"
        )
        return

    update_user_data(message.from_user.id, 'university_location', location_data)
    await message.answer(f"Адрес университета сохранен: {location_data['address']}")


from core.intent_detector import detect_intent, model
from features.weather_feature import handle_weather_intent, handle_set_city_intent
from features.news_feature import handle_news_intent
from bot.user_data import get_user_history, add_to_user_history


async def get_conversational_response(user_text: str, history: list) -> str:
    """
    Generates a conversational response using the Gemini model, including history.
    """
    if not model:
        return "Извините, у меня сейчас технические неполадки. Я не могу ответить."

    try:
        # Start a chat session with the existing history
        chat = model.start_chat(history=history)
        # The system prompt is now part of the model's configuration,
        # but we prepend our assistant prompt for persona.
        # For this implementation, we will rely on the history and the initial prompt.
        # A more advanced implementation might use a system prompt.

        response = await chat.send_message_async(user_text)
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
    # Do not process empty messages
    if not message.text:
        return

    intent_data = await detect_intent(message.text)
    intent = intent_data.get("intent")
    entities = intent_data.get("entities", {})

    response_message = ""
    user_id = message.from_user.id
    user_text = message.text

    # Route to tool-using intents first
    if intent == "weather":
        response_message = await handle_weather_intent(message, entities)
    elif intent == "set_city":
        response_message = await handle_set_city_intent(message, entities)
    elif intent == "news":
        response_message = await handle_news_intent(message, entities)
    else:
        # If no specific tool intent, treat as a general conversation with memory
        history = get_user_history(user_id)
        response_message = await get_conversational_response(user_text, history)
        # Save the interaction to history
        add_to_user_history(user_id, user_text, response_message)

    await message.answer(response_message)
