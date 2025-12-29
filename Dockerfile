# Multi-stage Dockerfile for Coolify deployment
# This builds the backend service
FROM python:3.11-slim as backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Create necessary directories
RUN mkdir -p exports data

# Expose port
EXPOSE 8000

# Run the application
# Use PORT from environment variable (Coolify sets this automatically)
# Default to 8000 if PORT is not set
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"

