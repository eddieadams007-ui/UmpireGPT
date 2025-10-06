from flask import Flask, request, jsonify
from .config import OPENAI_API_KEY, USE_OPENAI, KB_PATH, logger  # Import logger from config
from .retriever import retrieve_answer

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    logger.info("Health check requested")
    return jsonify({"status": "healthy", "kb_loaded": True, "kb_size": 1000})

@app.route('/answer', methods=['POST'])
def answer():
    logger.info("Answer request received")
    data = request.get_json()
    query = data.get('query', '')
    k = data.get('k', 5)
    logger.info(f"Processing query: {query}, k={k}, KB_PATH={KB_PATH}")
    response = retrieve_answer(query, k, KB_PATH, OPENAI_API_KEY, USE_OPENAI)
    logger.info(f"Response: {response}")
    return jsonify(response)

if __name__ == '__main__':
    logger.info("Starting app in debug mode")
    app.run(host='0.0.0.0', port=8080)
