FROM gcr.io/umpgpt/umpiregpt-base:v1
WORKDIR /umpiregpt
COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt
COPY src/ src/
COPY data/ data/
COPY auto_backup_logs.py .
RUN mkdir -p /umpiregpt/logs
ENV PYTHONPATH=/umpiregpt/src
ENV DB_PATH=/umpiregpt/logs/app_data.db
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
