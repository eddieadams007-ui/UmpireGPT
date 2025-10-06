import os
# Load from environment variables or set defaults
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-secret:latest') # Use Secret Manager in production
USE_OPENAI = os.getenv('USE_OPENAI', 'true').lower() == 'true'
KB_PATH = os.getenv('KB_PATH', 'data/chunks/rules.chunks.jsonl')  # Updated to match /data
# Add more config as needed (e.g., model settings)
