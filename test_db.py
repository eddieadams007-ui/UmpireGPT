from src.db_logger import DBLogger

logger = DBLogger()
logger.log_interaction(
    query_text="Test query",
    division="Majors A",
    response="Test response",
    session_id="test-123",
    response_time=0.5,
    query_type="Rule Clarification",
    api_used="Cached",
    tokens_used=0
)
print("Logged test interaction")
