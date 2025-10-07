import faiss
import numpy as np
import json
from typing import Dict, List
from openai import OpenAI
import os
from dotenv import load_dotenv

class Retriever:
    def __init__(self, index_path: str, idmap_path: str):
        """Initialize the retriever with FAISS index and ID mapping."""
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.data_path = os.getenv("KB_PATH", "data/chunks/rules.chunks.jsonl")
        self.index_path = index_path
        self.idmap_path = idmap_path
        self.index = faiss.read_index(index_path)
        if self.index.d != 3072:  # Matches text-embedding-3-large
            raise ValueError(f"FAISS index dimension {self.index.d} does not match expected 3072")
        self.idmap = {}
        with open(idmap_path, 'r') as f:
            for line in f:
                fields = line.strip().split(',')
                id_val, doc_id = fields[0], fields[-1]  # Use first (source_file) and last (new_id) columns
                self.idmap[id_val] = doc_id  # Store source_file as key
        self.model = 'text-embedding-3-large'

    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve top-k relevant documents using FAISS index."""
        embedding_response = self.client.embeddings.create(input=[query], model=self.model)
        query_vector = np.array(embedding_response.data[0].embedding).reshape(1, -1).astype('float32')
        if query_vector.shape[1] != self.index.d:
            raise ValueError(f"Query vector dimension {query_vector.shape[1]} does not match index dimension {self.index.d}")
        distances, indices = self.index.search(query_vector, k)
        relevant_docs = []
        with open(self.data_path, 'r') as f:
            for i, line in enumerate(f):
                if i in indices[0]:
                    doc = json.loads(line)
                    doc['distance'] = float(distances[0][list(indices[0]).index(i)])
                    doc['id'] = self.idmap.get(i, f"doc_{i}")
                    relevant_docs.append(doc)
        return relevant_docs
