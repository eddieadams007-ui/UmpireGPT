FROM python:3.11-slim

WORKDIR /umpiregpt

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y build-essential libopenblas-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements-backend.txt .
RUN pip install --no-cache-dir --upgrade pip==25.2 && \
    pip install --no-cache-dir -r requirements-backend.txt

COPY src/ src/
COPY data/ data/

ENV PYTHONPATH=/umpiregpt/src
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
