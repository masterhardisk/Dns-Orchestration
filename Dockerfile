FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS runtime

COPY backend /app/backend
COPY frontend /app/frontend

ENV DATA_DIR=/data
RUN mkdir -p /data

CMD ["python", "-m", "backend.main"]

FROM base AS test

COPY backend/requirements-dev.txt /app/requirements-dev.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY backend /app/backend

CMD ["pytest"]