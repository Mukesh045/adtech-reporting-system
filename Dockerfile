FROM python:3.11-slim

COPY . /app

WORKDIR /app/adreport/backend

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE $PORT

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
