# Use an official Python 3.11 runtime as the base image
FROM python:3.11-slim

# Set the working directory inside the container to /umpiregpt
WORKDIR /umpiregpt

# Copy requirements.txt and env file from the project root to /umpiregpt
COPY requirements.txt .
COPY .env .

# Install system dependencies for sentence-transformers and faiss-cpu
RUN apt-get update && apt-get install -y build-essential libopenblas-dev

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and data
COPY src/ .
COPY data data/

# Expose port 8000 for FastAPI with Uvicorn
EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", 8000]
