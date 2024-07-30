from aiogram import Bot
from dotenv import load_dotenv
from os import getenv
from aiogram.enums import ParseMode  # Import ParseMode from the correct module
from aiogram.client.default import DefaultBotProperties

load_dotenv()
TOKEN_API = getenv("TOKEN_API")
GEMINI_API_KEY = getenv("GEMINI_API_KEY")
USE_GEMINI = getenv("USE_GEMINI", "true").lower() == "true"
USE_OLLAMA = getenv("USE_OLLAMA", "false").lower() == "true"


if TOKEN_API is None or GEMINI_API_KEY is None:
    raise ValueError("TOKEN_API or GEMINI_API_KEY environment variable is not set")


class Bot(Bot):
    def __init__(self):
        super().__init__(
            token=TOKEN_API,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    async def close(self):
        if hasattr(self, 'session') and not self.session.closed:
            await self.session.close()
