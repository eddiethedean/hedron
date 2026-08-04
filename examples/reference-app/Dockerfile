FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY packages ./packages
COPY examples/reference-app ./examples/reference-app

RUN pip install --no-cache-dir uv \
    && uv sync --locked --no-dev --package hedron \
    && uv pip install --python .venv/bin/python -e packages/hedron-core -e packages/hedron

ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app/examples/reference-app
EXPOSE 8000
# Adopter-local path: app module lives in this directory after WORKDIR change.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips", "*"]
