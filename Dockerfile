# 1. Use a lightweight Python image
FROM python:3.11-slim

# 2. Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory
WORKDIR /app

# 4. Install system dependencies (needed for psycopg2)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the application
COPY . .

# 7. Run with Gunicorn (Production-grade server)
# Render/Cloud services provide the PORT variable automatically
CMD gunicorn --bind 0.0.0.0:$PORT app:app