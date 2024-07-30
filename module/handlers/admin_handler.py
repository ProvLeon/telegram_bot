#import logging
from aiogram.filters import Command
from aiogram import Router, types

admin_router = Router()
ADMIN_ID = 123456789  # Replace with your admin ID

@admin_router.message(Command(commands=['ban']))
async def ban_user(msg: types.Message):
    if msg.from_user.id == ADMIN_ID:
        parts = msg.text.split()
        if len(parts) == 2:
            user_id = int(parts[1])
            await msg.bot.kick_chat_member(chat_id=msg.chat.id, user_id=user_id)
            await msg.reply(f"User {user_id} has been banned.")
        else:
            await msg.reply("Usage: /ban <user_id>")
    else:
        await msg.reply("You don't have permission to use this command.")

@admin_router.message(Command(commands=['delete']))
async def delete_message(msg: types.Message):
    if msg.from_user.id == ADMIN_ID:
        parts = msg.text.split()
        if len(parts) == 2:
            message_id = int(parts[1])
            await msg.bot.delete_message(chat_id=msg.chat.id, message_id=message_id)
            await msg.reply(f"Message {message_id} has been deleted.")
        else:
            await msg.reply("Usage: /delete <message_id>")
    else:
        await msg.reply("You don't have permission to use this command.")
