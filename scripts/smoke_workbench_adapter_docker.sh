#!/usr/bin/env bash
# License-independent Linux smoke for Hedron's Workbench adaptation contract.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONTAINER="hedron-workbench-adapter-smoke-$$"
PORT="${HEDRON_WORKBENCH_ADAPTER_PORT:-8050}"
MOUNT="/s/demo/p/9"

cleanup() {
  docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

if ! command -v docker >/dev/null 2>&1 || ! docker info >/dev/null 2>&1; then
  printf '%s\n' "docker is required and must be reachable" >&2
  exit 1
fi

docker run --rm -d \
  --name "$CONTAINER" \
  -p "127.0.0.1:${PORT}:8050" \
  -v "$ROOT:/src:ro" \
  -w /src/examples/workbench-reference \
  -e HEDRON_SESSION_SECRET=adapter-docker-smoke-not-for-production \
  -e PYTHONPATH=/src/examples/workbench-reference \
  python:3.12-slim \
  sh -lc "pip install -q /src/packages/hedron-core /src/packages/hedron /src/packages/hedron-workbench && python -m hedron_workbench.cli run app_facade:app --mode on --host 0.0.0.0 --allow-external-bind --port 8050 --mount '${MOUNT}' --public-base-url 'https://wb.example${MOUNT}'" \
  >/dev/null

ready=0
for _ in $(seq 1 60); do
  if curl -fsS --max-time 2 "http://127.0.0.1:${PORT}/" >/dev/null 2>&1; then
    ready=1
    break
  fi
  if [[ "$(docker inspect --format '{{.State.Running}}' "$CONTAINER" 2>/dev/null || true)" != "true" ]]; then
    break
  fi
  sleep 2
done
if [[ "$ready" -ne 1 ]]; then
  docker logs --tail 80 "$CONTAINER" >&2 || true
  exit 1
fi

page="$(curl -fsS --max-time 10 "http://127.0.0.1:${PORT}${MOUNT}/")"
grep -Fq 'Hello from Hedron on Workbench' <<<"$page"
grep -Fq "${MOUNT}/hedron-static/hedron-mount.mjs" <<<"$page"
grep -Fq "hx-get=\"${MOUNT}/status\"" <<<"$page"
grep -Fq "action=\"${MOUNT}/ping\"" <<<"$page"

headers="$(curl -fsS -D - -o /dev/null --max-time 10 "http://127.0.0.1:${PORT}${MOUNT}/")"
grep -qi "path=${MOUNT}" <<<"$headers"

fragment="$(curl -fsS --max-time 10 \
  -H 'HX-Request: true' -H 'HX-Target: #service-status' \
  "http://127.0.0.1:${PORT}${MOUNT}/status")"
grep -Fq 'All systems operational' <<<"$fragment"

asset_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 10 \
  "http://127.0.0.1:${PORT}${MOUNT}/hedron-static/hedron-default.css")"
[[ "$asset_code" == "200" ]]

redirect_headers="$(curl -sS -D - -o /dev/null --max-time 10 \
  "http://127.0.0.1:${PORT}${MOUNT}/go")"
grep -qi "^location: ${MOUNT}/login" <<<"$redirect_headers"

encoded="$(curl -fsS --path-as-is --max-time 10 \
  "http://127.0.0.1:${PORT}/https%3A%2F%2Fwb.example%2Fs%2Fdemo%2Fp%2F9%2Fencoded")"
grep -Fq 'Encoded Workbench target normalized' <<<"$encoded"
wrong_origin="$(curl -sS --path-as-is -o /dev/null -w '%{http_code}' --max-time 10 \
  "http://127.0.0.1:${PORT}/https%3A%2F%2Fevil.example%2Fs%2Fdemo%2Fp%2F9%2Fencoded")"
[[ "$wrong_origin" == "400" ]]

diagnostic="$(curl -fsS --max-time 10 \
  "http://127.0.0.1:${PORT}${MOUNT}/workbench-status")"
grep -Fq '"active":true' <<<"$diagnostic"
grep -Fq '"normalizer_count":1' <<<"$diagnostic"

invite="$(curl -fsS --max-time 10 \
  "http://127.0.0.1:${PORT}${MOUNT}/invite-link")"
grep -Fq '"durable_links":false' <<<"$invite"
grep -Fq '"ephemeral_session":true' <<<"$invite"

"$ROOT/.venv/bin/python" "$ROOT/scripts/smoke_workbench_websocket.py" \
  "ws://127.0.0.1:${PORT}${MOUNT}/ws"

printf '%s\n' \
  "WORKBENCH_ADAPTER_DOCKER=pass page=ok fragment=ok cookies=ok assets=ok redirects=ok target_guards=ok diagnostics=ok durable_guard=ok websocket=ok"
