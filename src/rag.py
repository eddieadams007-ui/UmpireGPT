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
            return "No relevant context found."
        
        # Validate data_path and index_path existence
        if not os.path.exists(self.data_path) or not os.path.exists(self.index_path):
            return "Data or index file not found."
        
        # Combine context into a prompt
        context_with_ids = []
        for doc in context:
            doc_id = idmap.get(list(idmap.index).index(int(doc['id'].split('_')[-1]) if 'doc_' in doc['id'] else int(doc['id'])), doc['id'])
            context_with_ids.append(f"ID: {doc_id}, Text: {doc['text']}")
        context_text = " ".join(context_with_ids)
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
