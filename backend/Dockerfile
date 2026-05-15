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

COPY backend/ backend/

EXPOSE 8000

WORKDIR /app/backend

ENV PATH="/app/.venv/bin:$PATH"

CMD ["fastapi", "run", "app/main.py"]
