import asyncio
from datetime import datetime, timedelta
from module.bot import Bot
from module.handlers.ai_handler import get_ai_response
from aiogram.enums import ParseMode
from module.database import db
from module.images_handler import get_image_url_for_class
from aiogram.types import URLInputFile, InlineKeyboardMarkup, InlineKeyboardButton
import logging
import random

#import re

class ReminderScheduler:
    def __init__(self):
        self.bot = Bot()
        self.reminders = {}

    def get_all_reminders(self):
        #if user_id in db.get_all_subscribers():
        reminders = db.get_reminders()
        #self.reminders[user_id] = reminders
        logging.info(f"Reminders: {reminders}")
        return reminders
        #return []


    async def send_reminder(self, user_id, reminder_time, class_name, concepts=None, reminder_type="class", header_text=None, platform_info=None, url=None):

        if db.is_subscribed(user_id):
            reminder_history = []
            response = ""
            if isinstance(reminder_time, str):
                reminder_time = datetime.strptime(reminder_time, "%Y-%m-%d %H:%M:%S")
            image_url = get_image_url_for_class(class_name)
            date = datetime.now()
            dat = date.strftime("%Y-%m-%d %H:%M:%S")

            prompt = f"""
            Generate a unique and engaging reminder message with emojis for a {class_name} class at {reminder_time.strftime('%I:%M %p')} on {reminder_time.strftime('%d %B %Y')}.
            Todays date is {dat}.
            {'the session will be held on ' + platform_info if platform_info else ''}.
            {"concepts to cover" + concepts + "." if concepts else ''}
            This is a {reminder_type} reminder.
            if todays date {dat} matches the reminder date {reminder_time.strftime('%Y-%m-%d %H:%M:%S')} when mark the session for today.
            Remember to state the class name using a definite article (e.g. the or a).
            Make the post attractive and engaging with interesting content and emojis.
            also make sure you bolden the class name and time.
            make the post professional and apealing to the target audience.
            format your response in a markdown format making it beautiful.
            remember to use only one asteriks(*) to wrap a text like this *bold_text* to bolden it
            """
            #response = await get_ai_response(prompt)
            if header_text:
                response = f"{header_text}\n\n"
            response += await get_ai_response(prompt)
            reminder_history.append(response)

            try:
                photo = URLInputFile(image_url)
                chat_member = await self.bot.get_chat_member(user_id, user_id=user_id)
                user = chat_member.user

                greetings = ["Hey", "Hello", "Hi", "Greetings", "Good day", "Howdy"]
                greeting = random.choice(greetings)

                username = "@" + user.username or user.first_name
                personalized_response = f"{greeting}, *{username}!! 👋\n\n{response.strip()}*"

                keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Join Class", url=url)]])
                await self.bot.send_photo(user_id, photo, caption=personalized_response, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
                return {"caption": personalized_response, "photo": photo}
            except Exception as e:
                print(f"Error sending image: {e}")
                await self.bot.send_message(user_id, personalized_response, parse_mode=ParseMode.MARKDOWN)
                return {"caption": personalized_response, "photo": None}
        return {"caption": "", "photo": None}

    def set_reminder(self, reminder_time, class_name, platform_info, concepts=None):
        #    #if user_id not in self.reminders:
            #    self.reminders[user_id] = [{"time": reminder_time, "class_name": class_name}]
            #else:
        db.add_reminder(reminder_time, class_name, platform_info, concepts)
        for user_id in db.get_all_subscribers():
            asyncio.create_task(self._schedule_reminders( user_id, reminder_time, class_name, platform_info, concepts))

    async def _schedule_reminders(self, user_id, reminder_time, class_name, platform_info, concepts):
        now = datetime.now()
        daily_reminder = reminder_time - timedelta(days=1)
        thirty_min_reminder = reminder_time - timedelta(minutes=30)

        if now < daily_reminder:
            await asyncio.sleep((daily_reminder - now).total_seconds())
            await self.send_reminder(user_id, reminder_time, class_name, "daily", platform_info=platform_info, concepts=concepts)

        if now < thirty_min_reminder:
            await asyncio.sleep((thirty_min_reminder - now).total_seconds())
            await self.send_reminder(user_id, reminder_time, class_name, "30-minute", platform_info=platform_info, concepts=concepts)

        if now < reminder_time:
            await asyncio.sleep((reminder_time - now).total_seconds())
            await self.send_reminder(user_id, reminder_time, class_name, "immediate", platform_info=platform_info, concepts=concepts)

reminder_scheduler = ReminderScheduler()
