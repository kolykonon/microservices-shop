FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

COPY libs/ libs/

RUN uv sync --frozen --no-dev

COPY services/notifications/ services/notifications/

WORKDIR /app/services/notifications

CMD ["sh", "-c", "python -m app.main"]

