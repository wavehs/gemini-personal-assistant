import os
import requests

def get_weather(location: str) -> str:
    """
    Fetches the current weather for a given location from OpenWeatherMap.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Error: OpenWeather API key not found."

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": api_key,
        "units": "metric"  # Use Celsius
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes

        data = response.json()

        main_weather = data.get("weather", [{}])[0].get("main", "N/A")
        description = data.get("weather", [{}])[0].get("description", "N/A")
        temp = data.get("main", {}).get("temp", "N/A")

        return f"The weather in {location} is currently {main_weather} ({description}) with a temperature of {temp}°C."

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"Sorry, I couldn't find the weather for {location}. Please check the location and try again."
        else:
            return f"Error fetching weather data: {e}"
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
