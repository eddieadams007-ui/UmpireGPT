from fastapi import FastAPI, HTTPException
from .rag import RAG
from .retriever import Retriever
from .db_logger import DBLogger
import pandas as pd
import json
from .config import OPENAI_API_KEY, USE_OPENAI
import time
import uuid

app = FastAPI()
logger = DBLogger()

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
    
    start_time = time.time()
    idmap = pd.read_csv("data/chunks/rules.idmap.csv")
    context = retriever.retrieve(question)
    answer = rag.generate_answer(question, context, idmap)
    response_time = time.time() - start_time
    
    # Extract division and session_id from question (Streamlit formats as "Division: X\n...")
    division = "All"
    session_id = str(uuid.uuid4())
    query_text = question
    if "Division:" in question:
        parts = question.split("\n")
        for part in parts:
            if part.startswith("Division:"):
                division = part.replace("Division:", "").strip()
                query_text = "\n".join([p for p in parts if not p.startswith("Division:")]).strip()
    
    # Get query_type, api_used, and tokens_used
    query_type = rag.classify_intent(query_text)
    api_used = "OpenAI" if USE_OPENAI and context else "Cached"
    tokens_used = 0  # Placeholder; update with actual OpenAI token count if available
    
    # Log interaction
    logger.log_interaction(
        query_text=query_text,
        division=division,
        response=answer,
        session_id=session_id,
        response_time=response_time,
        query_type=query_type,
        api_used=api_used,
        tokens_used=tokens_used,
        rule_reference=None  # Extract from answer if needed
    )
    
    return {"question": question, "answer": answer if answer else "Sorry, I couldn't find a rule matching your query."}

@app.get("/validate_call")
async def validate_call(question: str):
    if not question:
        raise HTTPException(status_code=400, detail="No question provided")
    
    start_time = time.time()
    idmap = pd.read_csv("data/chunks/rules.idmap.csv")
    context = retriever.retrieve(question)
    intent = rag.classify_intent(question)
    
    # Extract division and session_id from question
    division = "All"
    session_id = str(uuid.uuid4())
    query_text = question
    if "Division:" in question:
        parts = question.split("\n")
        for part in parts:
            if part.startswith("Division:"):
                division = part.replace("Division:", "").strip()
                query_text = "\n".join([p for p in parts if not p.startswith("Division:")]).strip()
    
    if intent != "scenario_based":
        answer = "This endpoint is for validating umpire calls in specific game scenarios. Please describe a game situation (e.g., outs, runners, call made)."
        response_time = time.time() - start_time
        logger.log_interaction(
            query_text=query_text,
            division=division,
            response=answer,
            session_id=session_id,
            response_time=response_time,
            query_type=intent,
            api_used="Cached",
            tokens_used=0,
            rule_reference=None
        )
        return {"question": question, "answer": answer}
    
    missing_slots = rag.check_scenario_slots(question)
    if missing_slots:
        answer = f"Hey coach, I need a bit more info to validate this call! Can you tell me about {', '.join(missing_slots)}? For example, how many outs are there, and who's on base?"
        response_time = time.time() - start_time
        logger.log_interaction(
            query_text=query_text,
            division=division,
            response=answer,
            session_id=session_id,
            response_time=response_time,
            query_type=intent,
            api_used="Cached",
            tokens_used=0,
            rule_reference=None
        )
        return {"question": question, "answer": answer}
    
    answer = rag.generate_answer(question, context, idmap)
    response_time = time.time() - start_time
    query_type = intent
    api_used = "OpenAI" if USE_OPENAI and context else "Cached"
    tokens_used = 0  # Placeholder; update with actual OpenAI token count if available
    
    logger.log_interaction(
        query_text=query_text,
        division=division,
        response=answer,
        session_id=session_id,
        response_time=response_time,
        query_type=query_type,
        api_used=api_used,
        tokens_used=tokens_used,
        rule_reference=None  # Extract from answer if needed
    )
    
    return {"question": question, "answer": answer}
