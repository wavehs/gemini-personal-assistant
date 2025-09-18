import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# --- Main application ---

async def main():
    """
    Main function to start the bot.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    )
    logging.info("Starting bot...")

    # Load environment variables from .env file
    load_dotenv()
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logging.error("TELEGRAM_BOT_TOKEN not found in .env file.")
        return

    # Initialize Bot and Dispatcher
    bot = Bot(token=bot_token)
    dp = Dispatcher()

    # Include routers
    from bot.handlers import router as bot_router
    dp.include_router(bot_router)

    # Start polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually.")
