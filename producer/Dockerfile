FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install websocket-client==1.4.0 && \
    pip install finnhub-python==2.4.17

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    netcat-traditional procps && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN useradd -m appuser
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD ps aux | grep "[p]ython.*producer.py" || exit 1

CMD ["python", "-OO", "producer.py"] 