from apis.weather import get_weather

async def handle_weather_intent(entities: dict) -> str:
    """
    Handles the 'weather' intent.

    Args:
        entities (dict): A dictionary of entities extracted by the intent detector.

    Returns:
        str: A message to be sent to the user.
    """
    location = entities.get("location")
    if not location:
        return "I need a location to check the weather. For example: 'What's the weather in Paris?'"

    weather_report = get_weather(location)
    return weather_report
