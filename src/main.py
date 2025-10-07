from fastapi import FastAPI, HTTPException
from rag import RAG
from retriever import Retriever
import pandas as pd
import json
from config import OPENAI_API_KEY, USE_OPENAI

app = FastAPI()

# Load meta.json for additional context
with open('data/chunks/index/meta.json', 'r') as f:
    meta = json.load(f)

# Initialize RAG and Retriever with file paths
rag = RAG(data_path="data/chunks/rules.chunks.jsonl", index_path="data/chunks/index/rules.faiss", meta=meta)
retriever = Retriever(index_path="data/chunks/index/rules.faiss", idmap_path="data/chunks/rules.idmap.csv")

# Set OpenAI API key from config (for production, use Secret Manager)
import os
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

@app.get("/query")
async def query_rule(question: str):
    if not question:
        raise HTTPException(status_code=400, detail="No question provided")

    # Load idmap for mapping
    idmap = pd.read_csv("data/chunks/rules.idmap.csv")

    # Retrieve context using FAISS index
    context = retriever.retrieve(question)

    # Generate answer using RAG with meta data
    answer = rag.generate_answer(question, context, idmap)
    return {"question": question, "answer": answer if answer else "Sorry, I couldn't find a rule matching your query."}
