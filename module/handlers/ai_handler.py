from aiogram import types
from aiogram.enums import ParseMode
import google.generativeai as genai
from module.bot import GEMINI_API_KEY, USE_GEMINI, USE_OLLAMA
from module.llama_interface import LlamaInterface
from module.custom_ai import CustomAI
from module.database import db

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')
llama_model = LlamaInterface("llama3")
custom_ai = CustomAI("llama3")


# Add this at the top of the file
#current_topic = None



def format_response_html(response):
    paragraphs = response.split('\n\n')
    formatted_response = ""
    for paragraph in paragraphs:
        if paragraph.startswith('*'):
            # This is a bullet point
            formatted_response += f"<ul><li>{paragraph[1:].strip()}</li></ul>"
        else:
            formatted_response += f"<p>{paragraph}</p>"
    return formatted_response

async def get_ai_response(prompt, chat_history=None):
    if USE_GEMINI:
        if chat_history:
            chat = gemini_model.start_chat(history=chat_history)
            response = chat.send_message(prompt)
        else:
            response = gemini_model.generate_content(prompt)
        return response.text
    elif USE_OLLAMA:
        return await llama_model.generate_response(prompt)
    else:
        return await custom_ai.get_response(prompt, chat_history)

async def handle_topic_conversation(msg: types.Message):
    discussion_history = db.get_discussion_history()
    current_topic = db.get_discussions()['topic'] if db.get_discussions() else None

    if current_topic:
        user_input = msg.text
        username = msg.from_user.username or msg.from_user.first_name
        db.add_message_to_history(msg.from_user.id, username, user_input)

        discussion_context = "\n".join([f"@{message['username']} said this '{message['message']}'" for message in discussion_history])
        prompt = f"""The current topic is '{current_topic}'. Recent discussions on the topic:\n{discussion_context}\n\nUser {username} said: {user_input}. Provide a relevant response while staying on topic.
        make sure you referense most of the users and their respective responses in from the recent discussions in relation to {current_topic} from {discussion_context}.
        you can tag their names like '@username' said....
        also, make your response as informative and engaging as possible. add emojis to spice up your response.
        and if possible add exmples to it.
        ensure that you build on the responses from the recent discussions and don't create you own answer. correct {user_input} if possible else build on the {user_input} and {discussion_context} provided.
        also, ask a follow up question if necessary."""

        ai_response = await get_ai_response(prompt)
        formatted_response = f"@{username}, {ai_response}"

        db.add_message_to_history(msg.bot.id, "You", ai_response)

        await msg.reply(formatted_response, parse_mode=ParseMode.MARKDOWN)
