# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /src

# Copy requirements.txt from the project root to the WORKDIR (/src)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code from the src directory to the WORKDIR (/src)
COPY src/ .

# Expose the port (e.g., 8000 for FastAPI)
EXPOSE 8000

# Command to run the application (adjust based on your entry point)
CMD ["python", "main.py"]
