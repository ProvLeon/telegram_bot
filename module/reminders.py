import asyncio
import logging
from datetime import datetime, timedelta

class ReminderScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.tasks = []

    async def schedule_reminder(self, chat_id, message, delay):
        await asyncio.sleep(delay)
        await self.bot.send_message(chat_id=chat_id, text=message)
        logging.info(f"Sent reminder to chat_id {chat_id}")

    def add_reminder(self, chat_id, message, when):
        now = datetime.now()
        delay = (when - now).total_seconds()
        task = asyncio.create_task(self.schedule_reminder(chat_id, message, delay))
        self.tasks.append(task)
