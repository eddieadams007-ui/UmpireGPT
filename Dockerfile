# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /umpiregpt

# Copy requirements.txt from the project root to the WORKDIR (/umpiregpt)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and the data directory with its structure
COPY src/ .
COPY data data/

# Expose the port (e.g., 8000 for FastAPI)
EXPOSE 8000

# Command to run the application (adjust based on your entry point)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", 8000]
