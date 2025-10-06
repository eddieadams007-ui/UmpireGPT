import os
from config import KB_PATH
from retriever import retrieve_answer

class RAG:
    def __init__(self, data_path, index_path, meta):
        self.data_path = data_path
        self.index_path = index_path
        self.meta = meta

    def generate_answer(self, query, context, idmap):
        # Use retriever's logic with config and meta
        api_key = os.getenv('OPENAI_API_KEY', 'your-secret:latest')
        use_openai = os.getenv('USE_OPENAI', 'true').lower() == 'true'
        return retrieve_answer(query, len(context), self.data_path, api_key, use_openai)
