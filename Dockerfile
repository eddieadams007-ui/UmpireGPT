FROM gcr.io/umpgpt/umpiregpt-base:v1
WORKDIR /umpiregpt
COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt
COPY src/ src/
COPY data/ data/
RUN mkdir -p /umpiregpt/data
ENV PYTHONPATH=/umpiregpt/src
ENV DB_PATH=/umpiregpt/data/app_data.db
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

