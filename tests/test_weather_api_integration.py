import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from features.weather_feature import handle_weather_intent

@pytest.mark.asyncio
async def test_weather_feature_integration_success():
    """
    Integration test for the weather feature, mocking the aiohttp response.
    """
    # Mock response from the weather API
    mock_api_response = {
        "weather": [{"main": "Clouds", "description": "overcast clouds"}],
        "main": {"temp": 15.5}
    }

    # Create a mock for the async response object
    mock_response = AsyncMock()
    mock_response.json.return_value = mock_api_response
    mock_response.raise_for_status = MagicMock()

    # The __aenter__ method of the context manager should return the mock response
    async def __aenter__(*args, **kwargs):
        return mock_response

    # The __aexit__ method of the context manager
    async def __aexit__(*args, **kwargs):
        pass

    # Patch os.getenv to return a dummy API key
    with patch.dict(os.environ, {"OPENWEATHER_API_KEY": "test_key"}):
        # Patch the session.get method to return our mock context manager
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__ = __aenter__
            mock_get.return_value.__aexit__ = __aexit__

            entities = {"location": "Berlin"}
            result = await handle_weather_intent(entities)

            expected_message = "The weather in Berlin is currently Clouds (overcast clouds) with a temperature of 15.5°C."
            assert result == expected_message
            mock_get.assert_called_once()
