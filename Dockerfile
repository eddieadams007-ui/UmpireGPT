FROM python:3.11-slim

WORKDIR /umpiregpt

# Install system dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y build-essential libopenblas-dev && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip==25.2 && \
    pip install --no-cache-dir -r requirements.txt

# Copy source and data
COPY src/ src/
COPY data/ data/

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
