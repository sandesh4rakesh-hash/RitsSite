FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Ensure the Images folder is included
ENV FLASK_APP=app.py

# Run with Gunicorn (bind to 0.0.0.0:8080 for Cloud Run)
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app", "--workers", "2"]
