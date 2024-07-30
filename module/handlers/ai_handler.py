import google.generativeai as genai
from module.bot import GEMINI_API_KEY, USE_GEMINI, USE_OLLAMA
from module.llama_interface import LlamaInterface
from module.custom_ai import CustomAI

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')
llama_model = LlamaInterface("llama3")
custom_ai = CustomAI("llama3")

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
