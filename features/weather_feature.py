from aiogram.types import Message
from apis.weather import get_weather
from bot.user_data import get_user_data, update_user_data


async def handle_set_city_intent(message: Message, entities: dict) -> str:
    """
    Handles the 'set_city' intent to save the user's default city.
    """
    user_id = message.from_user.id
    location = entities.get("location")

    if not location:
        return "Пожалуйста, укажите город, который вы хотите сохранить. Например: 'Мой город Москва'."

    update_user_data(user_id, "city", location)
    return f"Отлично! Я запомнил ваш город: {location}. Теперь вы можете спрашивать погоду без указания города."


async def handle_weather_intent(message: Message, entities: dict) -> str:
    """
    Handles the 'weather' intent by checking for a location in the message,
    or falling back to the user's saved city.
    """
    user_id = message.from_user.id
    location = entities.get("location")

    if not location:
        # If no location in message, try to get it from user data
        location = get_user_data(user_id, "city")

    if not location:
        return "Я не знаю вашего города. Чтобы я его запомнил, напишите, например: 'мой город Москва'."

    weather_report = await get_weather(location)
    return weather_report
