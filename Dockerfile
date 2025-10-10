FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY adreport/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY adreport/backend/ .

# Expose the port (Railway sets $PORT)
EXPOSE $PORT

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
