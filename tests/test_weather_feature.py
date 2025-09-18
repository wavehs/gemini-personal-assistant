import pytest
from unittest.mock import patch, AsyncMock

from features.weather_feature import handle_weather_intent

@pytest.mark.asyncio
async def test_handle_weather_intent_with_location():
    """
    Tests the handle_weather_intent function with a valid location.
    """
    # Mock the get_weather function
    with patch('features.weather_feature.get_weather', new_callable=AsyncMock) as mock_get_weather:
        # Configure the mock to return a specific value
        mock_get_weather.return_value = "Mocked weather for London"

        entities = {"location": "London"}
        result = await handle_weather_intent(entities)

        # Assert that get_weather was called once with "London"
        mock_get_weather.assert_called_once_with("London")

        # Assert that the function returns the mocked value
        assert result == "Mocked weather for London"

@pytest.mark.asyncio
async def test_handle_weather_intent_without_location():
    """
    Tests the handle_weather_intent function without a location.
    """
    # Mock the get_weather function
    with patch('features.weather_feature.get_weather', new_callable=AsyncMock) as mock_get_weather:
        entities = {} # No location provided
        result = await handle_weather_intent(entities)

        # Assert that get_weather was NOT called
        mock_get_weather.assert_not_called()

        # Assert that the function returns the expected message
        assert "I need a location" in result
