FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY packages ./packages
COPY examples/reference-app ./examples/reference-app

# ARCHETYPE-025 runtime: flagship + data/charts/markdown extras + ASGI server + Redis client.
RUN pip install --no-cache-dir uv \
    && uv sync --locked --no-dev --package hedron \
    && uv pip install --python .venv/bin/python \
        -e "packages/hedron-core" \
        -e "packages/hedron[data,charts,markdown]" \
        -e "packages/hedron-data" \
        -e "packages/hedron-charts" \
        uvicorn redis

ENV PATH="/app/.venv/bin:$PATH"
ENV HEDRON_ENV=production
# Proxy IP(s) allowed to set X-Forwarded-* (Caddy on the compose network). Override via
# FORWARDED_ALLOW_IPS; do not use '*' in shared deploys.
ENV FORWARDED_ALLOW_IPS=proxy
WORKDIR /app/examples/reference-app
EXPOSE 8000
# Multi-worker production archetype (ARCHETYPE-025). Requires HEDRON_REDIS_URL +
# HEDRON_SESSION_SECRET (compose requires both). Explorer is off under HEDRON_ENV=production.
# Demo HTTP Basic auth requires HEDRON_ALLOW_DEMO_AUTH=1 (compose sets it for the sample only).
CMD ["sh", "-c", "exec uvicorn app:app --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers --forwarded-allow-ips \"${FORWARDED_ALLOW_IPS:-proxy}\""]
