import os
import aiohttp

async def get_news(category: str) -> str:
    """
    Fetches top news headlines for a given category from NewsAPI.org.
    """
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "Ошибка: Ключ для API новостей не найден."

    # Map user-friendly categories to API categories
    category_map = {
        "world": "general",
        "technology": "technology",
    }
    api_category = category_map.get(category.lower(), "general")

    base_url = "https://newsapi.org/v2/top-headlines"
    params = {
        "category": api_category,
        "country": "us",  # Fetching top headlines from a major region
        "pageSize": 5,    # Get top 5 articles
        "apiKey": api_key
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(base_url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                if data.get("status") != "ok" or not data.get("articles"):
                    return f"Не удалось получить новости в категории '{category}'. Попробуйте позже."

                articles = data["articles"]

                # Format the response
                response_lines = [f"Вот 5 главных новостей в категории '{category}':\n"]
                for article in articles:
                    title = article.get('title', 'Без заголовка')
                    url = article.get('url', '')
                    response_lines.append(f"- {title}")
                    if url:
                        response_lines.append(f"  {url}")

                return "\n".join(response_lines)

        except aiohttp.ClientError as e:
            print(f"Error fetching news data: {e}")
            return "Произошла ошибка при запросе новостей. Пожалуйста, попробуйте еще раз."
        except Exception as e:
            print(f"An unexpected error occurred in get_news: {e}")
            return "Произошла непредвиденная ошибка при получении новостей."
