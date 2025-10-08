from fastapi import FastAPI, HTTPException
from .rag import RAG
from .retriever import Retriever
import pandas as pd
import json
from .config import OPENAI_API_KEY, USE_OPENAI

app = FastAPI()

# Load meta.json for additional context
with open('data/chunks/index/meta.json', 'r') as f:
    meta = json.load(f)

# Initialize RAG and Retriever with file paths
rag = RAG(data_path="data/chunks/rules.chunks.jsonl", index_path="data/chunks/index/rules.faiss", meta=meta)
retriever = Retriever(index_path="data/chunks/index/rules.faiss", idmap_path="data/chunks/rules.idmap.csv")

# Set OpenAI API key from config
import os
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

@app.get("/query")
async def query_rule(question: str):
    if not question:
        raise HTTPException(status_code=400, detail="No question provided")
    idmap = pd.read_csv("data/chunks/rules.idmap.csv")
    context = retriever.retrieve(question)
    answer = rag.generate_answer(question, context, idmap)
    return {"question": question, "answer": answer if answer else "Sorry, I couldn't find a rule matching your query."}

@app.get("/validate_call")
async def validate_call(question: str):
    if not question:
        raise HTTPException(status_code=400, detail="No question provided")
    idmap = pd.read_csv("data/chunks/rules.idmap.csv")
    context = retriever.retrieve(question)
    intent = rag.classify_intent(question)
    if intent != "scenario_based":
        return {
            "question": question,
            "answer": "This endpoint is for validating umpire calls in specific game scenarios. Please describe a game situation (e.g., outs, runners, call made)."
        }
    missing_slots = rag.check_scenario_slots(question)
    if missing_slots:
        return {
            "question": question,
            "answer": f"Hey coach, I need a bit more info to validate this call! Can you tell me about {', '.join(missing_slots)}? For example, how many outs are there, and who's on base?"
        }
    answer = rag.generate_answer(question, context, idmap)
    return {"question": question, "answer": answer}
