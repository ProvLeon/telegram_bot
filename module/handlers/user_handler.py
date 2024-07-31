import logging
import asyncio
import aiohttp
from aiogram.filters import Command
from aiogram import Router, types
from aiogram.enums import ParseMode, ChatType
from module.handlers.ai_handler import get_ai_response
#from module.reminders import reminder_scheduler
from module.user_profiles import UserProfileManager
from module.gamification import GamificationManager
from module.database import db

user_router = Router()
profile_manager = UserProfileManager()
gamification_manager = GamificationManager()


async def validate_url(session, url):
    try:
        async with session.head(url, allow_redirects=True, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        logging.error(f"Error validating URL: {e}")
        return False

def escape_markdown_v2(text):
    escape_chars = r"_~`>#+-=|{}.!"
    return ''.join(['\\' + char if char in escape_chars else char for char in text])


@user_router.message(Command('help'))
async def cmd_help(msg: types.Message) -> None:
    help_text = (
        "/start - Start the bot and get basic instructions.\n"
        "/help - Display a list of available commands and how to use them.\n"
        "/subscribe - Subscribe to updates or notifications from the coding class.\n"
        "/unsubscribe - Unsubscribe from updates or notifications.\n"
        "/schedule - Display the schedule of upcoming classes or events.\n"
        "/materials - Provide access to class materials.\n"
        "/assignment - Post or retrieve current assignments.\n"
        "/ask - Ask questions related to the coding topics discussed in the channel.\n"
        "/feedback - Provide feedback to the administrators or teachers.\n"
        "/about - Display information about the bot and its purpose.\n"
        "/poll - Create a poll to gather feedback from class members.\n"
        "/profile - Create or view your profile.\n"
        "/setprofile - Set your profile information.\n"
        "/points - View your points and badges.\n"
        "/snippet - Share and discuss code snippets.\n"
        "/quiz - Participate in an interactive quiz."
    )
    await msg.answer(help_text)

@user_router.message(Command('start'))
async def cmd_start(msg: types.Message) -> None:
    logging.info(f"Received /start command from user {msg.from_user.id}")
    response = await get_ai_response("Hello! I'm a new user.")
    await msg.bot.send_message(chat_id=msg.chat.id, text=response, parse_mode=ParseMode.MARKDOWN)
    logging.info(f"Sent AI-generated greeting to user {msg.from_user.id}")

@user_router.message(Command('subscribe'))
async def subscribe_user(msg: types.Message) -> None:
    user_id = msg.from_user.id
    if not db.is_subscribed(user_id):
        db.subscribe(user_id)
        gamification_manager.add_points(user_id, 10)
        await msg.reply("You have been subscribed to the coding class updates. You'll now receive class reminders!")
    else:
        await msg.reply("You are already subscribed.")

@user_router.message(Command('unsubscribe'))
async def unsubscribe_user(msg: types.Message) -> None:
    user_id = msg.from_user.id
    if db.is_subscribed(user_id):
        db.unsubscribe(user_id)
        await msg.reply("You have been unsubscribed from the coding class updates and reminders.")
    else:
        await msg.reply("You are not subscribed.")


@user_router.message(Command('schedule'))
async def send_schedule(msg: types.Message) -> None:
    schedule_text = "Upcoming classes:\n1. Introduction to Python - July 31\n2. Advanced JavaScript - August 7"
    await msg.reply(schedule_text)

@user_router.message(Command('materials'))
async def send_materials(msg: types.Message) -> None:
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.answer("Please specify a topic. \nUsage: /materials [topic]")
        return

    topic = parts[1]
    sites = ["codecademy.com", "freecodecamp.org", "w3schools.com", "programiz.com"]

    prompt = f"""Provide learning materials for {topic} from {', '.join(sites)}.
    Ensure each link is a direct, valid, and publicly accessible URL to a specific page about {topic}.
    Format the response as a numbered list with the format: [Title](URL)
    Provide at least one result for each site, in the order specified."""

    max_retries = 3
    valid_materials = []

    for attempt in range(max_retries):
        materials = await get_ai_response(prompt)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for line in materials.split('\n'):
                if line.strip() and '](' in line:
                    url = line.split('](')[1].split(')')[0]
                    tasks.append(validate_url(session, url))

            results = await asyncio.gather(*tasks)

        valid_materials = [line for line, is_valid in zip(materials.split('\n'), results) if is_valid]

        if valid_materials:
            break
        else:
            logging.warning(f"No valid materials found on attempt {attempt + 1}. Retrying...")

    if valid_materials:
        response = f"Learning materials for *{topic.capitalize()}*:\n\n"
        sorted_materials = sorted(valid_materials, key=lambda x: next((i for i, site in enumerate(sites) if site in x.lower()), len(sites)))
        current_site = ""
        for material in sorted_materials:
            site = next((site for site in sites if site in material.lower()), "Other")
            if site != current_site:
                response += f"\n*{' '.join(site.capitalize().split('.')[:-1])}*\n\n"
                current_site = site
            response += f"{material}\n"
    else:
        response = f"I couldn't find valid, accessible materials for '{topic.capitalize()}' at this time. \nThis might be due to temporary network issues or content availability. \n\nPlease try again later or consider a different, related topic."

    await msg.answer(response, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

@user_router.message(Command('assignment'))
async def send_assignment(msg: types.Message) -> None:
    assignment_text = "Current assignment:\n1. Complete the Python Basics exercises by August 1."
    await msg.answer(assignment_text)

@user_router.message(Command('ask'))
async def handle_question(msg: types.Message) -> None:
    parts = msg.text.split(maxsplit=1)
    if len(parts) == 2:
        question = parts[1]
        response = await get_ai_response(question)
        await msg.reply(response, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    else:
        await msg.reply("Please provide a question after the /ask command. Example:\n\n/ask What is matter?")

@user_router.message(Command('feedback'))
async def handle_feedback(msg: types.Message) -> None:
    await msg.reply("Please provide your feedback. We appreciate your input!")

@user_router.message(Command('about'))
async def send_about(msg: types.Message) -> None:
    about_text = "This bot is designed to help manage the coding class channel and provide a better user experience with Gemini AI embedded."
    await msg.reply(about_text)

@user_router.message(Command('poll'))
async def create_poll(msg: types.Message):
    question = "What topic do you want to cover next?"
    options = ["Python", "JavaScript", "GoLang", "Rust"]
    await msg.bot.send_poll(chat_id=msg.chat.id, question=question, options=options, type='regular')

@user_router.message(Command('profile'))
async def handle_profile(msg: types.Message):
    user_id = msg.from_user.id
    profile = profile_manager.get_profile(user_id)
    if profile:
        profile_text = f"Profile for {msg.from_user.first_name}:\n"
        for key, value in profile.items():
            profile_text += f"{key.capitalize()}: {value}\n"
    else:
        profile_text = "You don't have a profile yet. Use /setprofile to create one."
    await msg.bot.send_message(chat_id=msg.chat.id, text=profile_text, reply_to_message_id=msg.message_id)

@user_router.message(Command('setprofile'))
async def set_profile(msg: types.Message):
    user_id = msg.from_user.id
    parts = msg.text.split(maxsplit=1)
    if len(parts) == 2:
        profile_data = {}
        for item in parts[1].split(","):
            key, value = item.split(":")
            profile_data[key.strip()] = value.strip()
        profile_manager.set_profile(user_id, profile_data)
        await msg.reply("Your profile has been updated.")
    else:
        await msg.reply("Usage: \n\n/setprofile \t\"key:value, key:value, ...\"")

@user_router.message(Command('points'))
async def handle_points(msg: types.Message):
    user_id = msg.from_user.id
    points = gamification_manager.get_points(user_id)
    badges = gamification_manager.get_badges(user_id)
    #level = gamification_manager.get_level(user_id)
    response = f"You have {points} points. \nYour badges: {', '.join(badges)}."
    await msg.reply(response)

@user_router.message(Command('snippet'))
async def handle_snippet(msg: types.Message):
    parts = msg.text.split(maxsplit=1)
    if len(parts) == 2:
        snippet = parts[1]
        await msg.reply(f"Here's the code snippet you shared:\n\n```{snippet}```", parse_mode=ParseMode.MARKDOWN)
    else:
        await msg.reply("Usage: /snippet [code]")

@user_router.message(Command('quiz'))
async def handle_quiz(msg: types.Message):
    question = "What is the output of the following code?\n\n```python\nprint('Hello, World!')\n```"
    options = ["Hello, World!", "Error", "None"]
    correct_option_id = 0
    await msg.bot.send_poll(chat_id=msg.chat.id, question=question, options=options, type='quiz', correct_option_id=correct_option_id)

@user_router.message()
async def handle_other_messages(msg: types.Message) -> None:
    if msg.chat.type == ChatType.PRIVATE:
        if msg.text.lower().startswith('/ask'):
            await handle_question(msg)
        elif msg.text.startswith('/'):
            await msg.reply("This command is not recognized. Type /help for a list of available commands.")
        else:
            # Handle conversation in private chat
            response = await get_ai_response(msg.text)
            await msg.reply(response, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    else:
        if msg.text.lower().startswith('/ask'):
            await handle_question(msg)
        elif msg.text.startswith('/'):
            await msg.reply("This command is not recognized. Type /help for a list of available commands.")
        else:
            await msg.reply("Sorry, I didn't understand that command. Type /help for a list of available commands.")

#async def generate_conversation_response(user_message: str) -> str:
#    # Implement your conversation logic here
#    # This could involve natural language processing, intent recognition, etc.
#    # For now, we'll just echo the user's message
#    return f"You said: {user_message}"
