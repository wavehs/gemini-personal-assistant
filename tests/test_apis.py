import pytest
from unittest.mock import patch, MagicMock
import os
import requests

from apis.weather import get_weather

def test_get_weather_success():
    """
    Tests the get_weather function with a successful API call.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "weather": [{"main": "Clear", "description": "clear sky"}],
        "main": {"temp": 25}
    }
    mock_response.raise_for_status.return_value = None

    with patch('os.getenv', return_value="fake_api_key"), \
         patch('requests.get', return_value=mock_response) as mock_requests_get:

        location = "London"
        result = get_weather(location)

        mock_requests_get.assert_called_once_with(
            "http://api.openweathermap.org/data/2.5/weather",
            params={"q": location, "appid": "fake_api_key", "units": "metric"}
        )
        assert "The weather in London is currently Clear (clear sky) with a temperature of 25°C." in result

def test_get_weather_no_api_key():
    """
    Tests the get_weather function when the API key is not found.
    """
    with patch('os.getenv', return_value=None):
        result = get_weather("London")
        assert "Error: OpenWeather API key not found." in result

def test_get_weather_request_exception():
    """
    Tests the get_weather function when a RequestException occurs.
    """
    with patch('os.getenv', return_value="fake_api_key"), \
         patch('requests.get', side_effect=requests.exceptions.RequestException("Test error")):

        result = get_weather("London")
        assert "Error fetching weather data: Test error" in result

def test_get_weather_unexpected_error():
    """
    Tests the get_weather function when an unexpected error occurs.
    """
    with patch('os.getenv', return_value="fake_api_key"), \
         patch('requests.get', side_effect=Exception("Unexpected error")):

        result = get_weather("London")
        assert "An unexpected error occurred: Unexpected error" in result
