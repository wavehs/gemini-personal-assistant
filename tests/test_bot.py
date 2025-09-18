import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from aiogram.types import Message, User, Chat, CallbackQuery, InlineKeyboardMarkup

from bot.handlers import command_start_handler, command_help_handler, message_handler, process_callback_query
from bot.keyboards import create_main_menu_keyboard

# Helper to create a mock message
def create_mock_message(text: str) -> MagicMock:
    mock_message = MagicMock(spec=Message)
    mock_message.from_user = User(id=123, is_bot=False, first_name="Test", last_name="User")
    mock_message.chat = Chat(id=456, type="private")
    mock_message.text = text
    mock_message.answer = AsyncMock()
    return mock_message

# Helper to create a mock callback query
def create_mock_callback_query(data: str) -> MagicMock:
    mock_callback_query = MagicMock(spec=CallbackQuery)
    mock_callback_query.data = data
    mock_callback_query.message = create_mock_message("")
    mock_callback_query.answer = AsyncMock()
    mock_callback_query.message.edit_text = AsyncMock()
    return mock_callback_query

@pytest.mark.asyncio
async def test_command_start_handler():
    """
    Tests the /start command handler.
    """
    mock_message = create_mock_message("/start")

    await command_start_handler(mock_message)

    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert f"Здравствуйте, {mock_message.from_user.full_name}!" in call_args

@pytest.mark.asyncio
async def test_command_help_handler():
    """
    Tests the /help command handler.
    """
    mock_message = create_mock_message("/help")

    await command_help_handler(mock_message)

    mock_message.answer.assert_called_once()
    assert "Чем я могу вам помочь?" in mock_message.answer.call_args[0][0]
    assert isinstance(mock_message.answer.call_args[1]['reply_markup'], InlineKeyboardMarkup)

@pytest.mark.asyncio
@patch('bot.handlers.detect_intent', new_callable=AsyncMock)
@patch('bot.handlers.handle_weather_intent', new_callable=AsyncMock)
async def test_message_handler_weather_intent(mock_handle_weather, mock_detect_intent):
    """
    Tests the message handler with a 'weather' intent.
    """
    mock_detect_intent.return_value = {"intent": "weather", "entities": {"location": "Berlin"}}
    mock_handle_weather.return_value = "Weather in Berlin is sunny."

    mock_message = create_mock_message("What's the weather in Berlin?")

    await message_handler(mock_message)

    mock_detect_intent.assert_called_once_with("What's the weather in Berlin?")
    mock_handle_weather.assert_called_once_with(mock_message, {"location": "Berlin"})
    mock_message.answer.assert_called_once_with("Weather in Berlin is sunny.")

@pytest.mark.asyncio
@patch('bot.handlers.detect_intent', new_callable=AsyncMock)
@patch('bot.handlers.get_conversational_response', new_callable=AsyncMock)
async def test_message_handler_unknown_intent(mock_get_conv_response, mock_detect_intent):
    """
    Tests the message handler with an 'unknown' intent, which should trigger the conversational fallback.
    """
    mock_detect_intent.return_value = {"intent": "unknown", "entities": {}}
    mock_get_conv_response.return_value = "This is a conversational response."

    mock_message = create_mock_message("Some random text")

    await message_handler(mock_message)

    mock_detect_intent.assert_called_once_with("Some random text")
    mock_get_conv_response.assert_called_once_with("Some random text")
    mock_message.answer.assert_called_once_with("This is a conversational response.")

@pytest.mark.asyncio
async def test_process_callback_query():
    """
    Tests the callback query handler.
    """
    mock_callback_query = create_mock_callback_query("feature_weather")

    await process_callback_query(mock_callback_query)

    mock_callback_query.answer.assert_called_once()
    mock_callback_query.message.edit_text.assert_called_once_with(
        "Вы выбрали: feature_weather. Эта функция скоро появится!"
    )

def test_create_main_menu_keyboard():
    """
    Tests the creation of the main menu keyboard.
    """
    keyboard = create_main_menu_keyboard()
    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 3 # 3 rows
    assert len(keyboard.inline_keyboard[0]) == 2 # 2 buttons in first row
    assert keyboard.inline_keyboard[0][0].text == "🌦️ Weather"
    assert keyboard.inline_keyboard[0][0].callback_data == "feature_weather"
