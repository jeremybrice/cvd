# Multi-stage build for CVD application with AI services

# Stage 1: Python base with dependencies
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Application
FROM base as application

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/uploads

# Set permissions
RUN chmod +x app.py

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')" || exit 1

# Run application with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "--timeout", "120", "app:app"]

# Stage 3: AI Worker (for background tasks)
FROM base as ai-worker

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Run as Celery worker (if using task queue)
# CMD ["celery", "-A", "ai_services.tasks", "worker", "--loglevel=info"]

# For now, run a simple worker script
CMD ["python", "-m", "ai_services.worker"]