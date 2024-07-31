import asyncio
from datetime import datetime, timedelta
from module.bot import Bot
from module.handlers.ai_handler import get_ai_response
from aiogram.enums import ParseMode
from module.database import db
#import re

class ReminderScheduler:
    def __init__(self):
        self.bot = Bot()
        self.reminders = {}

    def get_user_reminders(self, user_id):
        if user_id in db.get_all_subscribers():
            self.reminders[user_id] = db.get_reminders(user_id)
            return self.reminders[user_id]
        return []


    async def send_reminder(self, user_id, reminder_time, class_name, reminder_type="class", header_text=None):
        if db.is_subscribed(user_id):
            reminder_history = []
            response = ""
            if isinstance(reminder_time, str):
                reminder_time = datetime.strptime(reminder_time, "%Y-%m-%d %H:%M:%S")

            prompt = f"""
            Generate a unique and engaging reminder message with emojis for a {class_name} class at {reminder_time.strftime('%I:%M %p')} on {reminder_time.strftime('%d %B %Y')}.
            This is a {reminder_type} reminder.
            Remember to state the class name using a definite article (e.g. "the" or "a").
            Make the post attractive and engaging with interesting content and emojis
            """

            if header_text:
                response = f"{header_text}\n\n"
            response += await get_ai_response(prompt)
            reminder_history.append(response)

            await self.bot.send_message(user_id, response, parse_mode=ParseMode.MARKDOWN)

    def set_reminder(self, reminder_time, class_name, platform_info):
        for user_id in db.get_all_subscribers():
            #if user_id not in self.reminders:
            #    self.reminders[user_id] = [{"time": reminder_time, "class_name": class_name}]
            #else:
            db.add_reminder(user_id, reminder_time, class_name, platform_info)
            asyncio.create_task(self._schedule_reminders(user_id, reminder_time, class_name))

    async def _schedule_reminders(self, user_id, reminder_time, class_name):
        now = datetime.now()
        daily_reminder = reminder_time - timedelta(days=1)
        thirty_min_reminder = reminder_time - timedelta(minutes=30)

        if now < daily_reminder:
            await asyncio.sleep((daily_reminder - now).total_seconds())
            await self.send_reminder(user_id, reminder_time, class_name, "daily")

        if now < thirty_min_reminder:
            await asyncio.sleep((thirty_min_reminder - now).total_seconds())
            await self.send_reminder(user_id, reminder_time, class_name, "30-minute")

        if now < reminder_time:
            await asyncio.sleep((reminder_time - now).total_seconds())
            await self.send_reminder(user_id, reminder_time, class_name, "immediate")

reminder_scheduler = ReminderScheduler()
