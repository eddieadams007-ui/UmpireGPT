FROM python:3.11-slim
WORKDIR /umpiregpt
COPY requirements.txt .
COPY .env .
RUN apt-get update && apt-get install -y build-essential libopenblas-dev
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --force-reinstall openai==2.1.0
COPY src/ .
COPY data data/
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
