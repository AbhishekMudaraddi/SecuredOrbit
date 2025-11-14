FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create reports directory for test outputs
RUN mkdir -p reports

# Expose port (default 5001, can be overridden via PORT env var)
EXPOSE 5001

# Health check (uses default port 5001)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/health')" || exit 1

# Run gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5001} --workers 2 --threads 2 --timeout 120 --access-logfile - --error-logfile - app:app"]

