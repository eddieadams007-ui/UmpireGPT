import faiss
import numpy as np
import json
from typing import Dict, List
from openai import OpenAI
from config import OPENAI_API_KEY

class Retriever:
    def __init__(self, index_path: str, idmap_path: str):
        self.index_path = index_path
        self.idmap_path = idmap_path
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        # Load idmap for mapping IDs to documents
        self.idmap = {}
        with open(idmap_path, 'r') as f:
            for line in f:
                id_val, doc_id = line.strip().split(',')
                self.idmap[int(id_val)] = doc_id
        # Initialize OpenAI for embeddings
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = 'text-embedding-3-large'  # Matches 3072 dimension from meta.json

    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve top-k relevant documents using FAISS index."""
        # Convert query to embedding using OpenAI
        embedding_response = self.client.embeddings.create(input=[query], model=self.model)
        query_vector = np.array(embedding_response.data[0].embedding).reshape(1, -1).astype('float32')
        
        # Search the FAISS index
        distances, indices = self.index.search(query_vector, k)
        
        # Map indices to document IDs and return relevant data
        relevant_docs = []
        with open('data/chunks/rules.chunks.jsonl', 'r') as f:
            for i, line in enumerate(f):
                if i in indices[0]:
                    doc = json.loads(line)
                    doc['distance'] = float(distances[0][list(indices[0]).index(i)])
                    doc['id'] = self.idmap.get(i, f"doc_{i}")
                    relevant_docs.append(doc)
        return relevant_docs
