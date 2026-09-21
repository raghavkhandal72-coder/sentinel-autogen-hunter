# ==============================================================================
# Production Hardened Dockerfile: Sentinel-AutoGen-Hunter Orchestrator
# ==============================================================================
FROM python:3.11-slim AS runtime

# Prevents Python from buffering stdout/stderr and writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Create dedicated non-root user and group (Least Privilege Principle)
RUN groupadd -g 10001 threat_ai && \
    useradd -u 10001 -g threat_ai -s /bin/bash -m ai_user

# Install dependencies using layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create actions directory and set permissions
RUN mkdir -p /app/actions && \
    chown -R ai_user:threat_ai /app

# Drop root privileges
USER ai_user

# Container Healthcheck for Kubernetes / Docker Swarm
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "agents.orchestrator:app", "--host", "0.0.0.0", "--port", "8000"]
