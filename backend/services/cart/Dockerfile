FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

COPY libs/ libs/

RUN uv sync --frozen --no-dev

COPY services/cart/ services/cart/

WORKDIR /app/services/cart

CMD ["sh", "-c", "/app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000"]

