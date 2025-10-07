import faiss
import numpy as np
import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv

class Retriever:
    def __init__(self, index_path="data/chunks/index/rules.faiss", idmap_path="data/chunks/rules.idmap.csv"):
        """Initialize the retriever with FAISS index and ID mapping."""
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.index = faiss.read_index(index_path)
        self.id_map = {}
        with open(idmap_path, 'r') as f:
            for line in f:
                fields = line.strip().split(',')
                source_file, doc_id = fields[0], fields[-1]  # Use first (source_file) and last (new_id) columns
                self.id_map[int(source_file.split('.')[0])] = doc_id

    def get_embedding(self, text):
        """Generate embedding for the input text using OpenAI's API."""
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-large"
        )
        return np.array(response.data[0].embedding, dtype=np.float32)

    def retrieve(self, query, k=5):
        """Retrieve top-k relevant documents for the given query."""
        query_embedding = self.get_embedding(query)
        query_embedding = query_embedding.reshape(1, -1)  # Reshape for FAISS
        distances, indices = self.index.search(query_embedding, k)
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            doc_id = self.id_map.get(idx, "Unknown")
            results.append({"doc_id": doc_id, "distance": float(dist)})
        return results

