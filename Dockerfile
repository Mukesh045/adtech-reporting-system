FROM python:3.11-slim

COPY backend /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE $PORT

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
