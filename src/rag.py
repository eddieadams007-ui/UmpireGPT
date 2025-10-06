import os
from config import OPENAI_API_KEY, USE_OPENAI
from openai import OpenAI

class RAG:
    def __init__(self, data_path, index_path, meta):
        self.data_path = data_path
        self.index_path = index_path
        self.meta = meta
        self.client = OpenAI(api_key=OPENAI_API_KEY) if USE_OPENAI else None

    def generate_answer(self, query, context, idmap):
        if not context:
            return "No relevant context found."
        
        # Combine context into a prompt
        context_text = " ".join([doc['text'] for doc in context])
        prompt = f"Based on the following context: {context_text}\nQuestion: {query}\nAnswer:"

        if USE_OPENAI and self.client:
            # Use OpenAI to generate answer
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        else:
            # Fallback to simple concatenation
            return f"Answer based on context: {context_text}"
