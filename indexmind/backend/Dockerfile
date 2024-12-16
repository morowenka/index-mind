# Use Python 3.9 slim image for a smaller footprint
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY src/ src/
COPY tests/ tests/
COPY schemas/ schemas/
COPY config/ config/
COPY app.py .
COPY pytest.ini .
COPY .env .env

# Export environment variables
RUN export $(cat .env | xargs)

# Run tests during build
RUN pip install pytest && pytest

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["uvicorn"]
CMD ["app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]