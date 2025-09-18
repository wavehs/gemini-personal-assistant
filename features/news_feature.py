from aiogram.types import Message
from apis.news import get_news

async def handle_news_intent(message: Message, entities: dict) -> str:
    """
    Handles the 'news' intent by fetching news from the specified category.
    """
    # Default to 'world' news if no category is specified
    category = entities.get("category", "world")

    # The user might type "мировые" (world) or "технологии" (technology)
    # We should map these to the keys our API function expects.
    category_map_ru = {
        "мировые": "world",
        "технологии": "technology",
        "технология": "technology"
    }

    # Use the mapped category, otherwise use the original, or default to "world"
    final_category = category_map_ru.get(category.lower(), category)

    news_report = await get_news(final_category)
    return news_report
