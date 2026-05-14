FROM ghcr.io/astral-sh/uv:latest AS uv

# === Builder stage ===
FROM python:3.12-slim AS builder

COPY --from=uv /uv /usr/local/bin/uv

WORKDIR /build

COPY pyproject.toml uv.lock ./
COPY backend/pyproject.toml backend/pyproject.toml
COPY frontend/pyproject.toml frontend/pyproject.toml
COPY ml/pyproject.toml ml/pyproject.toml

RUN uv sync --frozen --no-dev --package backend

# === Runtime stage ===
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /build/.venv .venv

COPY frontend/ frontend/

EXPOSE 8501

WORKDIR /app/frontend

ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV PATH="/app/.venv/bin:$PATH"

CMD ["streamlit", "run", "main.py"]
