import faiss
import numpy as np
import json
from typing import Dict, List

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

    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve top-k relevant documents using FAISS index."""
        # Placeholder: Convert query to embedding (replace with actual embedding model)
        # For now, simulate with a random vector (replace with real embedding logic)
        query_vector = np.random.rand(1, self.index.d).astype('float32')
       
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
