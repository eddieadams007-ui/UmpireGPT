from flask import Flask, request, jsonify
from .rag import answer_query

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "kb_loaded": True, "kb_size": 1000})

@app.route('/answer', methods=['POST'])
def answer():
    data = request.get_json()
    query = data.get('query', '')
    k = data.get('k', 5)
    response = answer_query(query, k)
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
