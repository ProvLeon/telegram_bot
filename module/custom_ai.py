#import random
#from difflib import get_close_matches
import re
from collections import defaultdict
from module.llama_interface import LlamaInterface

class CustomAI:
    def __init__(self, llama_model_path):
        self.llama = LlamaInterface(llama_model_path)
        self.conversation_data = defaultdict(list)
        self.user_topics = defaultdict(set)

    async def get_response(self, user_id, message):
        message = message.lower()
        self.conversation_data[user_id].append(message)

        # Extract potential topics from the message
        topics = set(re.findall(r'\b\w+\b', message))
        self.user_topics[user_id].update(topics)

        # Generate context from conversation history
        context = "\n".join(self.conversation_data[user_id][-5:])  # Last 5 messages

        # Generate prompt for LLaMA 3
        prompt = f"Human: {context}\n\nHuman: {message}\n\nAI:"

        # Generate response using LLaMA 3
        response = await self.llama.generate_response(prompt)

        return response

    def add_to_knowledge_base(self, topic, information):
        # This method can be used to fine-tune or update the LLaMA model
        # For now, we'll just acknowledge the addition
        return f"Added information about '{topic}' to my knowledge base."
