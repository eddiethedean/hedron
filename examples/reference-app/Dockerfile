FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY packages ./packages
COPY examples/reference-app ./examples/reference-app

RUN pip install --no-cache-dir uv \
    && uv sync --locked --no-dev --package hedron \
    && uv pip install --python .venv/bin/python -e packages/hedron-core -e packages/hedron

RUN uv pip install --python .venv/bin/python redis

ENV PATH="/app/.venv/bin:$PATH"
ENV HEDRON_ENV=production
WORKDIR /app/examples/reference-app
EXPOSE 8000
# Multi-worker production archetype (ARCHETYPE-025). Requires HEDRON_REDIS_URL +
# HEDRON_SESSION_SECRET (compose sets both). Explorer is off under HEDRON_ENV=production.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "*"]
