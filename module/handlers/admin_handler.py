from aiogram.filters import Command
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from module.reminders import reminder_scheduler
from module.handlers.user_handler import handle_other_messages
from datetime import datetime
import logging
from module.database import db
import re


admin_router = Router()

def parse_custom_date(date_string):
    patterns = [
        r"(?:(\w+),\s)?(\d{1,2})(st|nd|rd|th) (\w+)(?:,?\s(\d{4}))? at (\d{1,2})(?::(\d{2}))?(am|pm)",
        r"(?:(\w+),\s)?(\d{1,2})(st|nd|rd|th) (\w+)(?:,?\s(\d{4}))? at (\d{1,2})(am|pm)",
        r"(?:(\w+),\s)?(\d{1,2})(st|nd|rd|th) (\w+)(?:,?\s(\d{4}))?"
    ]

    for pattern in patterns:
        match = re.match(pattern, date_string, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 5:  # New pattern without time
                weekday, day, _, month, year = groups
                current_year = datetime.now().year
                year = int(year) if year else current_year
                month_num = datetime.strptime(month, "%B").month
                date = datetime(year, month_num, int(day))
                return date
            else:
                weekday, day, _, month, year, hour, minute, ampm = groups if len(groups) == 8 else groups[:6] + (None,) + groups[6:]

                current_year = datetime.now().year
                year = int(year) if year else current_year
                month_num = datetime.strptime(month, "%B").month
                hour = int(hour) if hour else 0
                minute = int(minute) if minute else 0

                if ampm and ampm.lower() == 'pm' and hour != 12:
                    hour += 12
                elif ampm and ampm.lower() == 'am' and hour == 12:
                    hour = 0

                date = datetime(year, month_num, int(day), hour, minute)

                if weekday:
                    if date.strftime("%A").lower() != weekday.lower():
                        raise ValueError("Weekday doesn't match the date")

                return date

    raise ValueError("Invalid date format.")


async def is_admin(msg: types.Message):
    chat_admins = await msg.bot.get_chat_administrators(msg.chat.id)
    channel_owner = await msg.bot.get_chat_member(msg.chat.id, msg.from_user.id)
    logging.info(f"Admins: {chat_admins} {msg.from_user.id} {channel_owner}")
    #chat_admins = [admin for admin in chat_admins]
    admin_ids = [admin.user.id for admin in chat_admins]
    logging.info(f"Admin IDs: {admin_ids} {msg.from_user.id}")
    return msg.from_user.id in admin_ids

@admin_router.message(Command(commands=['ban']))
async def ban_user(msg: types.Message):
    if await is_admin(msg):
        parts = msg.text.split()
        if len(parts) == 2:
            user_id = int(parts[1])
            await msg.bot.ban_chat_member(chat_id=msg.chat.id, user_id=user_id)
            await msg.reply(f"User {user_id} has been banned.")
        else:
            await msg.reply("Usage: /ban <user_id>")
    else:
        await msg.reply("You don't have permission to use this command.")

@admin_router.message(Command(commands=['delete']))
async def delete_message(msg: types.Message):
    if await is_admin(msg):
        parts = msg.text.split()
        if len(parts) == 2:
            message_id = int(parts[1])
            await msg.bot.delete_message(chat_id=msg.chat.id, message_id=message_id)
            await msg.reply(f"Message {message_id} has been deleted.")
        else:
            await msg.reply("Usage: /delete <message_id>")
    else:
        await msg.reply("You don't have permission to use this command.")

@admin_router.message(Command('setclassreminder'))
async def set_class_reminder(msg: types.Message):
    if await is_admin(msg):
        command_parts = msg.text.split('"')
        logging.info(f"commands: {command_parts}")
        if len(command_parts) >= 5:
            time_str, class_name, platform_info = command_parts[1], command_parts[3], command_parts[5]
            logging.info(f"Setting class reminder for {class_name} at {time_str}")
            try:
                reminder_time = parse_custom_date(time_str)
                if reminder_time.hour == 0 and reminder_time.minute == 0:
                    reminder_time = reminder_time.replace(hour=0, minute=0)  # Set to midnight
                reminder_scheduler.set_reminder(reminder_time, class_name, platform_info)
                await msg.reply(f"Class reminder set for all subscribed users: {class_name} on {reminder_time.strftime('%d %B %Y at %I:%M%p')}")
            except ValueError:
                await msg.reply("Invalid time format. Please use format like '13th June 2024 at 3:00pm' or '13th June'")
        else:
            await msg.reply('Usage: /setclassreminder "date [and time]" "class name" "platform info"')
    else:
        await msg.reply("This command is only available to administrators.")

@admin_router.message(Command(commands=['*']))
async def handle_unknown_admin_command(msg: types.Message):
    if await is_admin(msg):
        await msg.reply("Unknown admin command. Please check the available admin commands.")
    else:
        # Let the user router handle it
        await handle_other_messages(msg)

@admin_router.message(Command('sendallreminders'))
async def send_all_reminders(msg: types.Message):
    if await is_admin(msg):
        sent_count = 0
        subscribers = db.get_all_subscribers()
        for user_id in subscribers:
            logging.info(f"Sending reminders to user {user_id}")
            reminders = reminder_scheduler.get_user_reminders(user_id)
            logging.info(f"reminders: {reminders}")
            if reminders:
                header_text = "Upcoming class reminders:\n\n"
                for reminder in reminders:
                    try:
                        await reminder_scheduler.send_reminder(user_id, reminder['time'], reminder['class_name'], header_text=header_text)
                        sent_count += 1
                        header_text = None  # Only send header for the first reminder
                    except Exception as _:
                        continue

        await msg.reply(f"Reminders sent to {sent_count} subscribed users.")
    else:
        await msg.reply("This command is only available to administrators.")


@admin_router.message(Command('cleardatabase'))
async def clear_database(msg: types.Message):
    if await is_admin(msg):
        db.clear_database()
        await msg.reply("Database has been cleared and tables recreated.")
    else:
        await msg.reply("This command is only available to administrators.")


@admin_router.message(Command('getsubscribers'))
async def get_subscribers(msg: types.Message):
    if await is_admin(msg):
        subscribers_id = db.get_all_subscribers()
        if not subscribers_id:
            await msg.reply("No subscribers found.")
            return

        keyboard = []
        for subscriber_id in subscribers_id:
            try:
                chat_member = await msg.bot.get_chat_member(msg.chat.id, subscriber_id)
                user = chat_member.user
                button_text = f"{user.full_name} (@{user.username})" if user.username else user.full_name
                keyboard.append([InlineKeyboardButton(text=button_text, callback_data=f"subscriber_{user.id}")])
            except Exception as e:
                logging.error(f"Error fetching subscriber info: {e}")

        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        await msg.reply(text="Subscribers:", reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        await msg.reply("This command is only available to administrators.")

@admin_router.callback_query(lambda c: c.data.startswith('subscriber_'))
async def subscriber_info(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split('_')[1])
    try:
        chat_member = await callback_query.bot.get_chat_member(callback_query.message.chat.id, user_id)
        user = chat_member.user

        info = f"User ID: {user.id}\n"
        info += f"Name: {user.full_name}\n"
        if user.username:
            info += f"(@{user.username})\n"
        #if user.phone_number:
        #    info += f"Phone: {user.phone_number}\n"

        #await callback_query.answer()
        await callback_query.answer(info)
    except Exception as e:
        logging.error(f"Error fetching subscriber info: {e}")
        await callback_query.answer("Error fetching subscriber information", show_alert=True)
