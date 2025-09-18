import pytest
from unittest.mock import patch, MagicMock

from features.weather_feature import handle_weather_intent

@pytest.mark.asyncio
async def test_handle_weather_intent_with_location():
    """
    Tests the handle_weather_intent function with a valid location.
    """
    # Mock the get_weather function
    with patch('features.weather_feature.get_weather') as mock_get_weather:
        # Configure the mock to return a specific value
        mock_get_weather.return_value = "Mocked weather for London"

        entities = {"location": "London"}
        result = await handle_weather_intent(entities)

        # Assert that get_weather was called once with "London"
        mock_get_weather.assert_called_once_with("London")

        # Assert that the function returns the mocked value
        assert result == "Mocked weather for London"

import requests

@pytest.mark.asyncio
async def test_handle_weather_intent_without_location():
    """
    Tests the handle_weather_intent function without a location.
    """
    # Mock the get_weather function
    with patch('features.weather_feature.get_weather') as mock_get_weather:
        entities = {} # No location provided
        result = await handle_weather_intent(entities)

        # Assert that get_weather was NOT called
        mock_get_weather.assert_not_called()

        # Assert that the function returns the expected message
        assert "I need a location" in result


@pytest.mark.asyncio
@patch('apis.weather.os.getenv')
@patch('apis.weather.requests.get')
async def test_handle_weather_intent_with_nonexistent_location(mock_requests_get, mock_getenv):
    """
    Tests the handle_weather_intent function with a non-existent location
    that results in a 404 error.
    """
    # Mock os.getenv to return a dummy API key
    mock_getenv.return_value = "dummy_api_key"

    # Configure the mock to simulate a 404 Not Found response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
    mock_requests_get.return_value = mock_response

    # The location can be anything, as the API call is mocked
    entities = {"location": "InvalidCity"}
    result = await handle_weather_intent(entities)

    # Assert that the friendly error message is returned
    assert "Sorry, I couldn't find the weather for InvalidCity" in result
