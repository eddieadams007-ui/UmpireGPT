from fastapi import FastAPI, HTTPException
from .rag import RAG
from .retriever import Retriever
from .db_logger import DBLogger
import pandas as pd
import json
from .config import OPENAI_API_KEY, USE_OPENAI
import time
import uuid
import os

app = FastAPI()
logger = DBLogger()

# Load meta.json for additional context
print("DEBUG: Loading meta.json")
try:
    with open('data/chunks/index/meta.json', 'r') as f:
        meta = json.load(f)
except Exception as e:
    print(f"DEBUG: Failed to load meta.json: {e}")
    raise Exception(f"Failed to load meta.json: {e}")

# Initialize RAG and Retriever with file paths
print("DEBUG: Initializing RAG")
try:
    rag = RAG(data_path="data/chunks/rules.chunks.jsonl", index_path="data/chunks/index/rules.faiss", meta=meta)
except Exception as e:
    print(f"DEBUG: Failed to initialize RAG: {e}")
    raise Exception(f"Failed to initialize RAG: {e}")

print("DEBUG: Initializing Retriever")
try:
    retriever = Retriever(index_path="data/chunks/index/rules.faiss", idmap_path="data/chunks/rules.idmap.csv")
except Exception as e:
    print(f"DEBUG: Failed to initialize Retriever: {e}")
    raise Exception(f"Failed to initialize Retriever: {e}")

# Set OpenAI API key from config
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

@app.get("/query")
async def query_rule(question: str):
    print(f"DEBUG: Received question: {question}")
    if not question:
        raise HTTPException(status_code=400, detail="No question provided")
   
    start_time = time.time()
    print("DEBUG: Loading idmap")
    try:
        idmap = pd.read_csv("data/chunks/rules.idmap.csv")
    except Exception as e:
        print(f"DEBUG: Failed to load idmap: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load idmap: {e}")
   
    print("DEBUG: Retrieving context")
    try:
        context = retriever.retrieve(question)
        print(f"DEBUG: Retrieved {len(context)} docs")
    except Exception as e:
        print(f"DEBUG: Failed to retrieve context: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve context: {e}")
   
    print("DEBUG: Generating answer")
    try:
        answer, tokens_used = rag.generate_answer(question, context, idmap)
    except Exception as e:
        print(f"DEBUG: Failed to generate answer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {e}")
   
    response_time = time.time() - start_time
   
    # Extract division and session_id
    division = "All"
    session_id = str(uuid.uuid4())
    query_text = question
    if "Division:" in question:
        parts = question.split("\n")
        for part in parts:
            if part.startswith("Division:"):
                division = part.replace("Division:", "").strip()
                query_text = "\n".join([p for p in parts if not p.startswith("Division:")]).strip()
   
    print("DEBUG: Classifying intent")
    try:
        query_type = rag.classify_intent(query_text)
    except Exception as e:
        print(f"DEBUG: Failed to classify intent: {e}")
        query_type = "Other"
   
    api_used = "OpenAI" if USE_OPENAI and context else "Cached"
    print(f"DEBUG: Logging interaction: query_type={query_type}, api_used={api_used}, tokens_used={tokens_used}")
    try:
        logger.log_interaction(
            query_text=query_text,
            division=division,
            response=answer,
            session_id=session_id,
            response_time=response_time,
            query_type=query_type,
            api_used=api_used,
            tokens_used=tokens_used,
            rule_reference=None
        )
        print("DEBUG: Interaction logged")
    except Exception as e:
        print(f"DEBUG: Failed to log interaction: {e}")
   
    return {"question": question, "answer": answer if answer else "Sorry, I couldn't find a rule matching your query."}

@app.get("/validate_call")
async def validate_call(question: str):
    print(f"DEBUG: Received validate_call question: {question}")
    if not question:
        raise HTTPException(status_code=400, detail="No question provided")
   
    start_time = time.time()
    print("DEBUG: Loading idmap")
    try:
        idmap = pd.read_csv("data/chunks/rules.idmap.csv")
    except Exception as e:
        print(f"DEBUG: Failed to load idmap: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load idmap: {e}")
   
    print("DEBUG: Retrieving context")
    try:
        context = retriever.retrieve(question)
        print(f"DEBUG: Retrieved {len(context)} docs")
    except Exception as e:
        print(f"DEBUG: Failed to retrieve context: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve context: {e}")
   
    print("DEBUG: Classifying intent")
    try:
        intent = rag.classify_intent(question)
        print(f"DEBUG: Intent classified: {intent}")
    except Exception as e:
        print(f"DEBUG: Failed to classify intent: {e}")
        intent = "Other"
   
    # Extract division and session_id
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
        print(f"DEBUG: Logging interaction: query_type={intent}, api_used=Cached")
        try:
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
            print("DEBUG: Interaction logged")
        except Exception as e:
            print(f"DEBUG: Failed to log interaction: {e}")
        return {"question": question, "answer": answer}
   
    print("DEBUG: Checking scenario slots")
    try:
        missing_slots = rag.check_scenario_slots(question)
    except Exception as e:
        print(f"DEBUG: Failed to check scenario slots: {e}")
        missing_slots = []
   
    if missing_slots:
        answer = f"Hey coach, I need a bit more info to validate this call! Can you tell me about {', '.join(missing_slots)}? For example, how many outs are there, and who's on base?"
        response_time = time.time() - start_time
        print(f"DEBUG: Logging interaction: query_type={intent}, api_used=Cached")
        try:
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
            print("DEBUG: Interaction logged")
        except Exception as e:
            print(f"DEBUG: Failed to log interaction: {e}")
        return {"question": question, "answer": answer}
   
    print("DEBUG: Generating answer")
    try:
        answer, tokens_used = rag.generate_answer(question, context, idmap)
    except Exception as e:
        print(f"DEBUG: Failed to generate answer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {e}")
   
    response_time = time.time() - start_time
    query_type = intent
    api_used = "OpenAI" if USE_OPENAI and context else "Cached"
    print(f"DEBUG: Logging interaction: query_type={query_type}, api_used={api_used}, tokens_used={tokens_used}")
    try:
        logger.log_interaction(
            query_text=query_text,
            division=division,
            response=answer,
            session_id=session_id,
            response_time=response_time,
            query_type=query_type,
            api_used=api_used,
            tokens_used=tokens_used,
            rule_reference=None
        )
        print("DEBUG: Interaction logged")
    except Exception as e:
        print(f"DEBUG: Failed to log interaction: {e}")
   
    return {"question": question, "answer": answer}
