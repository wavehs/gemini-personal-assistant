import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import os
import aiohttp

from apis.weather import get_weather

@pytest.mark.asyncio
async def test_get_weather_success():
    """
    Tests the get_weather function with a successful API call.
    """
    mock_api_response = {
        "weather": [{"main": "Clear", "description": "clear sky"}],
        "main": {"temp": 25}
    }

    mock_response = AsyncMock()
    mock_response.json.return_value = mock_api_response
    mock_response.raise_for_status = MagicMock()

    async def __aenter__(*args, **kwargs):
        return mock_response
    async def __aexit__(*args, **kwargs):
        pass

    with patch('os.getenv', return_value="fake_api_key"):
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__ = __aenter__
            mock_get.return_value.__aexit__ = __aexit__

            location = "London"
            result = await get_weather(location)

            mock_get.assert_called_once()
            assert "The weather in London is currently Clear (clear sky) with a temperature of 25°C." in result

@pytest.mark.asyncio
async def test_get_weather_no_api_key():
    """
    Tests the get_weather function when the API key is not found.
    """
    with patch('os.getenv', return_value=None):
        result = await get_weather("London")
        assert "Error: OpenWeather API key not found." in result

@pytest.mark.asyncio
async def test_get_weather_request_exception():
    """
    Tests the get_weather function when a ClientError occurs.
    """
    with patch('os.getenv', return_value="fake_api_key"), \
         patch('aiohttp.ClientSession.get', side_effect=aiohttp.ClientError("Test error")):

        result = await get_weather("London")
        assert "Error fetching weather data: Test error" in result

@pytest.mark.asyncio
async def test_get_weather_unexpected_error():
    """
    Tests the get_weather function when an unexpected error occurs.
    """
    with patch('os.getenv', return_value="fake_api_key"), \
         patch('aiohttp.ClientSession.get', side_effect=Exception("Unexpected error")):

        result = await get_weather("London")
        assert "An unexpected error occurred: Unexpected error" in result
