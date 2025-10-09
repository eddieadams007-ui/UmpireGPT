from src.rag import RAG
from src.retriever import Retriever
import pandas as pd
import json

try:
    with open('data/chunks/index/meta.json', 'r') as f:
        meta = json.load(f)
    print("DEBUG: Loaded meta.json")
    rag = RAG(data_path="data/chunks/rules.chunks.jsonl", index_path="data/chunks/index/rules.faiss", meta=meta)
    print("DEBUG: Initialized RAG")
    retriever = Retriever(index_path="data/chunks/index/rules.faiss", idmap_path="data/chunks/rules.idmap.csv")
    print("DEBUG: Initialized Retriever")
    idmap = pd.read_csv("data/chunks/rules.idmap.csv")
    print("DEBUG: Loaded idmap")
    context = retriever.retrieve("dropped third strike rule")
    print(f"DEBUG: Retrieved {len(context)} docs")
    answer = rag.generate_answer("What is the dropped third strike rule?", context, idmap)
    print("DEBUG: Answer:", answer[:100])
except Exception as e:
    print(f"DEBUG: Error: {e}")
