import os
from config import OPENAI_API_KEY, USE_OPENAI
from openai import OpenAI
import json

class RAG:
    def __init__(self, data_path, index_path, meta):
        self.data_path = data_path
        self.index_path = index_path
        self.meta = meta
        self.client = OpenAI(api_key=OPENAI_API_KEY) if USE_OPENAI else None

    def generate_answer(self, query, context, idmap):
        if not context:
            return "Sorry, I couldn't find any relevant rules for your question."
       
        # Validate data_path and index_path existence
        if not os.path.exists(self.data_path) or not os.path.exists(self.index_path):
            return "Oops, something went wrong—couldn't find the rulebook data."
       
        # Combine context into a prompt
        context_with_ids = []
        for doc in context:
            doc_id = idmap.get(list(idmap.index).index(int(doc['id'].split('_')[-1]) if 'doc_' in doc['id'] else int(doc['id'])), doc['id'])
            context_with_ids.append(f"ID: {doc_id}, Text: {doc['text']}")
        context_text = " ".join(context_with_ids)
        
        # Use a conversational prompt
        prompt = f"You're a friendly Little League coach answering questions based on the Official Little League Rulebook. Use a clear, conversational tone, as if explaining to a player or parent. Here's the context: {context_text}\nQuestion: {query}\nAnswer:"
       
        if USE_OPENAI and self.client:
            # Use OpenAI gpt-4o-mini for better tone
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You're a friendly Little League coach answering questions based on the Official Little League Rulebook. Use a clear, conversational tone, as if explaining to a player or parent."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        else:
            # Fallback to simple concatenation
            return f"Hey there! Based on the rulebook, here's what I found: {context_text}"
