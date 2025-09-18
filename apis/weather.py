import os
import aiohttp

async def get_weather(location: str) -> str:
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
        "units": "metric",  # Use Celsius
        "lang": "ru"        # Get description in Russian
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(base_url, params=params) as response:
                response.raise_for_status()  # Raise an exception for bad status codes

                data = await response.json()

                description = data.get("weather", [{}])[0].get("description", "нет данных")
                temp = data.get("main", {}).get("temp", "??")

                # Capitalize the first letter of the description
                description = description.capitalize()

                return f"Погода в городе {location}: {description}. Температура: {temp}°C."

        except aiohttp.ClientError as e:
            # Provide error messages in Russian
            return f"Ошибка при запросе погоды: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
