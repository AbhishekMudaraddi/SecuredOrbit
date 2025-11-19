FROM python:3.11-slim

WORKDIR /app
# env variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# reports of test
RUN mkdir -p reports
EXPOSE 5001

# Health check (uses default port 5001)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/health')" || exit 1

# Run gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5001} --workers 2 --threads 2 --timeout 120 --access-logfile - --error-logfile - app:app"]

