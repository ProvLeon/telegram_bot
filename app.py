import asyncio
import logging
from aiogram import Dispatcher
from module.bot import Bot
from module.handlers.user_handler import user_router
from module.handlers.admin_handler import admin_router
from aiohttp import ClientConnectorError
# Set up logging
logging.basicConfig(level=logging.INFO)

async def connect_with_retry(bot):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            await bot.get_me()
            logging.info("Successfully connected to Telegram API")
            return
        except ClientConnectorError as e:
            logging.warning(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(5)  # Wait 5 seconds before retrying
    raise Exception("Failed to connect to Telegram API after multiple attempts")


if __name__ == "__main__":
    bot = Bot()
    dp = Dispatcher()
    dp.include_router(user_router)

    async def main():
        await connect_with_retry(bot)
        await dp.start_polling(bot)

    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        asyncio.run(bot.session.close())
        logging.info("Bot session closed")



