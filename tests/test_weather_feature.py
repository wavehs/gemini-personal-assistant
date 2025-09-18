import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from aiogram.types import User, Chat, Message

from features.weather_feature import handle_weather_intent, handle_set_city_intent

# Helper to create a mock message, avoiding dependency on test_bot
def create_mock_message(text: str) -> MagicMock:
    mock_message = MagicMock(spec=Message)
    mock_message.from_user = User(id=123, is_bot=False, first_name="Test", last_name="User")
    mock_message.chat = Chat(id=456, type="private")
    mock_message.text = text
    mock_message.answer = AsyncMock()
    return mock_message

@pytest.mark.asyncio
@patch('features.weather_feature.get_weather', new_callable=AsyncMock)
@patch('features.weather_feature.get_user_data')
async def test_handle_weather_intent_with_location_in_entities(mock_get_user_data, mock_get_weather):
    """
    Tests handle_weather_intent when location is in the entities dict.
    """
    mock_get_weather.return_value = "Mocked weather for London"
    mock_message = create_mock_message("погода в лондоне")
    entities = {"location": "London"}

    result = await handle_weather_intent(mock_message, entities)

    mock_get_user_data.assert_not_called() # Should not check user data
    mock_get_weather.assert_called_once_with("London")
    assert result == "Mocked weather for London"

@pytest.mark.asyncio
@patch('features.weather_feature.get_weather', new_callable=AsyncMock)
@patch('features.weather_feature.get_user_data')
async def test_handle_weather_intent_with_saved_location(mock_get_user_data, mock_get_weather):
    """
    Tests handle_weather_intent when location is retrieved from user data.
    """
    mock_get_weather.return_value = "Mocked weather for Paris"
    mock_get_user_data.return_value = "Paris" # User has a saved city
    mock_message = create_mock_message("погода")
    entities = {} # No location in entities

    result = await handle_weather_intent(mock_message, entities)

    mock_get_user_data.assert_called_once_with(123, "city")
    mock_get_weather.assert_called_once_with("Paris")
    assert result == "Mocked weather for Paris"

@pytest.mark.asyncio
@patch('features.weather_feature.get_weather', new_callable=AsyncMock)
@patch('features.weather_feature.get_user_data')
async def test_handle_weather_intent_no_location(mock_get_user_data, mock_get_weather):
    """
    Tests handle_weather_intent when no location is available anywhere.
    """
    mock_get_user_data.return_value = None # No saved city
    mock_message = create_mock_message("погода")
    entities = {}

    result = await handle_weather_intent(mock_message, entities)

    mock_get_user_data.assert_called_once_with(123, "city")
    mock_get_weather.assert_not_called()
    assert "Я не знаю вашего города" in result

@pytest.mark.asyncio
@patch('features.weather_feature.update_user_data')
async def test_handle_set_city_intent(mock_update_user_data):
    """
    Tests the handle_set_city_intent function.
    """
    mock_message = create_mock_message("мой город москва")
    entities = {"location": "Москва"}

    result = await handle_set_city_intent(mock_message, entities)

    mock_update_user_data.assert_called_once_with(123, "city", "Москва")
    assert "Я запомнил ваш город: Москва" in result

@pytest.mark.asyncio
async def test_handle_set_city_intent_no_location():
    """
    Tests handle_set_city_intent when no location is provided in entities.
    """
    mock_message = create_mock_message("мой город")
    entities = {} # No location

    result = await handle_set_city_intent(mock_message, entities)
    assert "Пожалуйста, укажите город" in result
