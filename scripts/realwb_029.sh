#!/usr/bin/env bash
# REALWB-029: start pinned Posit Workbench, invoke real rserver-url, smoke Hedron.
# Never prints WORKBENCH_API_KEY / PWB_LICENSE / generated tokens.
set -euo pipefail
umask 077

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMPOSE_DIR="$ROOT/examples/workbench-reference"
COMPOSE=(docker compose -f "$COMPOSE_DIR/docker-compose.yml" --project-directory "$COMPOSE_DIR")
RESULT_DIR="$ROOT/docs/acceptance/realwb-029"
RESULT="$RESULT_DIR/RESULT.log"
IMAGE_DIGEST="sha256:d10ee76a840e8af054d54506ed4b54bc27ee7344ee09d8c99541cd23f39b8c32"
IMAGE="${HEDRON_WORKBENCH_IMAGE:-posit/workbench@${IMAGE_DIGEST}}"
RSERVER_URL_BIN="/usr/lib/rstudio-server/bin/rserver-url"
MOUNT="/s/demo/p/9"
PUBLIC_BASE="https://wb.example${MOUNT}"
APP_PORT=8050
LOCAL_PORT=8051
APP_PID=""
SMOKE_DIR="$(mktemp -d /tmp/hedron-workbench-smoke.XXXXXX)"
APP_LOG="$SMOKE_DIR/app.log"

redact_stream() {
  sed -E \
    -e 's/[A-Za-z0-9]{4}(-[A-Za-z0-9]{4}){5,}/***/g' \
    -e 's#[a-fA-F0-9]{16,}#***#g'
}

log() {
  printf '%s\n' "$*" | redact_stream
}

fail() {
  local code="$1"
  shift
  log "REALWB-029 $code $*"
  log "RESULT=fail"
  exit 1
}

cleanup() {
  if [[ -n "${APP_PID}" ]] && kill -0 "$APP_PID" >/dev/null 2>&1; then
    kill "$APP_PID" >/dev/null 2>&1 || true
    wait "$APP_PID" >/dev/null 2>&1 || true
  fi
  "${COMPOSE[@]}" down --remove-orphans >/dev/null 2>&1 || true
  if [[ -d "$SMOKE_DIR" && "$SMOKE_DIR" == /tmp/hedron-workbench-smoke.* ]]; then
    rm -r -- "$SMOKE_DIR"
  else
    log "cleanup_refused_unexpected_temp_path=true"
  fi
}

mkdir -p "$RESULT_DIR"
: > "$RESULT"
exec > >(tee -a "$RESULT") 2>&1
trap cleanup EXIT

log "REALWB-029 start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
log "image=$IMAGE"

if [[ -z "${WORKBENCH_API_KEY:-}" && -f "$ROOT/.env" ]]; then
  WORKBENCH_API_KEY="$("$ROOT/.venv/bin/python" -c '
import shlex, sys
for raw in open(sys.argv[1], encoding="utf-8"):
    line = raw.strip()
    if line.startswith("export "):
        line = line[7:].lstrip()
    if not line.startswith("WORKBENCH_API_KEY="):
        continue
    value = line.split("=", 1)[1].strip()
    parsed = shlex.split(value, comments=True, posix=True)
    print(parsed[0] if len(parsed) == 1 else "")
    break
' "$ROOT/.env")"
fi

if [[ -z "${WORKBENCH_API_KEY:-}" ]]; then
  fail "HED-WB-0001" "WORKBENCH_API_KEY is unset (load .env or export it)"
fi
if [[ ! "$WORKBENCH_API_KEY" =~ ^[[:alnum:]]{4}(-[[:alnum:]]{4}){5,}$ ]]; then
  fail "HED-WB-0001" "WORKBENCH_API_KEY is not a product-license-shaped value"
fi

if ! command -v docker >/dev/null 2>&1; then
  fail "HED-WB-0007" "docker is required for REALWB-029"
fi
if ! docker info >/dev/null 2>&1; then
  fail "HED-WB-0007" "docker daemon is not reachable"
fi
for command in curl jq; do
  command -v "$command" >/dev/null 2>&1 || \
    fail "HED-WB-0007" "$command is required for REALWB-029"
done
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  docker pull "$IMAGE" >/dev/null || \
    fail "HED-WB-0007" "could not pull the pinned Workbench image"
fi
resolved_digests="$(docker image inspect "$IMAGE" --format '{{join .RepoDigests ","}}' 2>/dev/null || true)"
if [[ "$IMAGE" == *"@sha256:"* && "$resolved_digests" != *"$IMAGE_DIGEST"* ]]; then
  fail "HED-WB-0007" "cached Workbench image did not match the pinned digest"
fi
log "image_digest=$IMAGE_DIGEST"

HOST_ARCH="$(uname -m)"
log "host_arch=$HOST_ARCH"

export PWB_LICENSE="$WORKBENCH_API_KEY"
unset WORKBENCH_API_KEY
export HEDRON_WORKBENCH_IMAGE="$IMAGE"
# Compose interpolates PWB_LICENSE; do not print it.

compose_pull="missing"
if docker image inspect "$IMAGE" >/dev/null 2>&1; then
  compose_pull="never"
fi
log "compose=up workbench pull=$compose_pull"
if ! "${COMPOSE[@]}" up -d --pull "$compose_pull" workbench; then
  fail "HED-WB-0007" "failed to start $IMAGE (license/platform/qemu). Do not hang on QEMU."
fi

ok=0
for _ in $(seq 1 36); do
  if curl -fsS -o /dev/null --max-time 5 "http://127.0.0.1:8787/auth-sign-in" >/dev/null 2>&1; then
    ok=1
    break
  fi
  sleep 5
done
if [[ "$ok" -ne 1 ]]; then
  logs="$("${COMPOSE[@]}" logs --no-color --tail 80 workbench 2>/dev/null || true)"
  if printf '%s' "$logs" | grep -qiE 'license.*(invalid|expired|denied)'; then
    fail "HED-WB-0001" "Workbench license was rejected (redacted)"
  fi
  fail "HED-WB-0007" "Workbench did not become ready on :8787/auth-sign-in"
fi
log "auth-sign-in=ok"

cid="$("${COMPOSE[@]}" ps -q workbench)"
if [[ -z "$cid" ]]; then
  fail "HED-WB-0007" "workbench container id missing"
fi
if ! docker exec "$cid" test -x "$RSERVER_URL_BIN"; then
  fail "HED-WB-0003" "real rserver-url missing at $RSERVER_URL_BIN"
fi
log "rserver-url=$RSERVER_URL_BIN"

version_out="$(docker exec "$cid" rstudio-server version 2>/dev/null || true)"
log "rstudio-server=$(printf '%s' "$version_out" | tr '\n' ' ' | redact_stream)"

set +e
rurl_out="$(docker exec "$cid" "$RSERVER_URL_BIN" -l "$APP_PORT" 2>/dev/null)"
rurl_rc=$?
set -e
log "rserver-url_rc=$rurl_rc"
if [[ -n "$rurl_out" ]]; then
  log "rserver-url_stdout=$(printf '%s' "$rurl_out" | redact_stream)"
fi
if [[ "$rurl_rc" -eq 0 ]]; then
  log "RSERVER_URL=ok"
elif [[ "$HOST_ARCH" == "arm64" && "$rurl_rc" -eq 139 ]]; then
  log "RSERVER_URL=emulation_limited rc=139 platform=linux/amd64-on-arm64"
else
  fail "HED-WB-0003" "real rserver-url execution failed rc=$rurl_rc"
fi

(
  cd "$COMPOSE_DIR"
  PYTHONPATH="$COMPOSE_DIR" uv run --python 3.12 --directory "$ROOT" \
    python -m hedron_workbench.cli run app_facade:app \
    --mode on --host 127.0.0.1 --port "$APP_PORT" --mount "$MOUNT" \
    --public-base-url "$PUBLIC_BASE"
) >"$APP_LOG" 2>&1 &
APP_PID=$!

ready=0
for _ in $(seq 1 40); do
  if curl -fsS -o /dev/null --max-time 2 "http://127.0.0.1:${APP_PORT}/" >/dev/null 2>&1; then
    ready=1
    break
  fi
  if ! kill -0 "$APP_PID" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
if [[ "$ready" -ne 1 ]]; then
  log "app_log=$(redact_stream < "$APP_LOG" | tail -n 50)"
  fail "HED-WB-0005" "Hedron app did not become ready on :$APP_PORT"
fi

launcher_body="$(curl -fsS --max-time 5 "http://127.0.0.1:${APP_PORT}/")"
if ! printf '%s' "$launcher_body" | grep -q "Hello from Hedron on Workbench"; then
  fail "HED-WB-0006" "launcher-stripped request path did not route"
fi
log "LAUNCHER_PATH=ok stripped_prefix=ok"

page_headers="$SMOKE_DIR/page.headers"
page_html="$SMOKE_DIR/page.html"
csrf_html="$SMOKE_DIR/csrf.html"
curl -fsS --max-time 5 -D "$page_headers" "http://127.0.0.1:${APP_PORT}${MOUNT}/" -o "$page_html"
if ! grep -q "Hello from Hedron on Workbench" "$page_html"; then
  fail "HED-WB-0006" "PAGE body missing expected text"
fi
if ! grep -qi "Path=${MOUNT}" "$page_headers" && ! grep -qi "path=${MOUNT}" "$page_headers"; then
  fail "HED-WB-0006" "CSRF/session cookie Path was not mount-scoped"
fi
log "PAGE=ok mount_prefix=ok cookie_path=ok"

token="$(awk 'BEGIN{IGNORECASE=1} /set-cookie:.*hedron_csrf=/{print; exit}' "$page_headers" | sed -E 's/.*hedron_csrf=([^;]+).*/\1/')"
if [[ -z "$token" ]]; then
  token="$(grep -oE 'name="csrf_token"[^>]*value="[^"]+"' "$page_html" | head -n1 | sed -E 's/.*value="([^"]+)".*/\1/' || true)"
fi

frag="$(curl -fsS --max-time 5 \
  -H 'HX-Request: true' \
  -H 'HX-Target: #service-status' \
  -H "X-CSRF-Token: ${token}" \
  -H "Cookie: hedron_csrf=${token}" \
  "http://127.0.0.1:${APP_PORT}${MOUNT}/status")"
if ! printf '%s' "$frag" | grep -q "All systems operational"; then
  fail "HED-WB-0006" "FRAGMENT /status missing expected text"
fi
log "FRAGMENT=ok"

csrf_code="$(curl -sS -o "$csrf_html" -w '%{http_code}' --max-time 5 \
  -H "X-CSRF-Token: ${token}" \
  -H "Cookie: hedron_csrf=${token}" \
  -X POST "http://127.0.0.1:${APP_PORT}${MOUNT}/ping")"
if [[ "$csrf_code" != "200" && "$csrf_code" != "303" && "$csrf_code" != "204" ]]; then
  fail "HED-WB-0006" "CSRF POST /ping failed status=$csrf_code"
fi
log "CSRF=ok"

asset_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 \
  "http://127.0.0.1:${APP_PORT}${MOUNT}/hedron-static/hedron-default.css")"
if [[ "$asset_code" != "200" ]]; then
  fail "HED-WB-0006" "ASSETS /hedron-static/hedron-default.css status=$asset_code"
fi
log "ASSETS=ok"

docs_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 "http://127.0.0.1:${APP_PORT}${MOUNT}/docs")"
spec_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 "http://127.0.0.1:${APP_PORT}${MOUNT}/openapi.json")"
if [[ "$docs_code" != "200" || "$spec_code" != "200" ]]; then
  fail "HED-WB-0006" "OpenAPI routes failed docs=$docs_code spec=$spec_code"
fi
log "OPENAPI=ok docs=$docs_code spec=$spec_code"
log "explorer=off"

redirect_headers="$SMOKE_DIR/redirect.headers"
redirect_code="$(curl -sS -o /dev/null -D "$redirect_headers" -w '%{http_code}' --max-time 5 \
  "http://127.0.0.1:${APP_PORT}${MOUNT}/go")"
redirect_location="$(awk 'tolower($1)=="location:" {gsub(/\r/, ""); print $2; exit}' "$redirect_headers")"
if [[ "$redirect_code" != "303" || "$redirect_location" != "${MOUNT}/login" ]]; then
  fail "HED-WB-0006" "mounted redirect failed status=$redirect_code location=$redirect_location"
fi
if [[ "${redirect_location#"$MOUNT"}" == *"$MOUNT"* ]]; then
  fail "HED-WB-0006" "mounted redirect duplicated the Workbench prefix"
fi
log "REDIRECT=ok mount_once=ok"

encoded_target="/https%3A%2F%2Fwb.example%2Fs%2Fdemo%2Fp%2F9%2Fencoded"
encoded_body="$(curl -fsS --path-as-is --max-time 5 \
  "http://127.0.0.1:${APP_PORT}${encoded_target}")"
if ! printf '%s' "$encoded_body" | grep -q "Encoded Workbench target normalized"; then
  fail "HED-WB-0006" "encoded absolute Workbench target was not normalized"
fi
log "ENCODED_TARGET=ok"

unsafe_code="$(curl -sS --path-as-is -o /dev/null -w '%{http_code}' --max-time 5 \
  "http://127.0.0.1:${APP_PORT}/https%3A%2F%2Fwb.example%2F%252e%252e%2Fadmin")"
if [[ "$unsafe_code" != "400" ]]; then
  fail "HED-WB-0006" "unsafe encoded Workbench target status=$unsafe_code expected=400"
fi

conflict_code="$(curl -sS --path-as-is -o /dev/null -w '%{http_code}' --max-time 5 \
  "http://127.0.0.1:${APP_PORT}/https%3A%2F%2Fwb.example%2Fs%2Fdemo%2Fp%2F9%2Fencoded%3Finside%3D1?outside=2")"
if [[ "$conflict_code" != "400" ]]; then
  fail "HED-WB-0006" "conflicting encoded Workbench query status=$conflict_code expected=400"
fi

oversized_segment="$(printf '%*s' 8200 '' | tr ' ' a)"
oversized_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 \
  "http://127.0.0.1:${APP_PORT}/${oversized_segment}")"
if [[ "$oversized_code" != "414" ]]; then
  fail "HED-WB-0006" "oversized Workbench target status=$oversized_code expected=414"
fi
log "TARGET_GUARDS=ok unsafe=400 conflict=400 oversized=414"

status_json="$(curl -fsS --max-time 5 \
  "http://127.0.0.1:${APP_PORT}${MOUNT}/workbench-status")"
if ! printf '%s' "$status_json" | grep -q '"active":true'; then
  fail "HED-WB-0006" "active Workbench diagnostic missing"
fi
if ! printf '%s' "$status_json" | grep -q '"normalizer_count":1'; then
  fail "HED-WB-0006" "facade normalizer count was not exactly one"
fi
if ! printf '%s' "$status_json" | grep -q '"browser_mount":"/s/demo/p/9"'; then
  fail "HED-WB-0006" "launcher mount handoff missing from facade diagnostic"
fi
if ! printf '%s' "$status_json" | grep -q '"cookie_mount":"/s/demo/p/9"'; then
  fail "HED-WB-0006" "launcher cookie handoff missing from facade diagnostic"
fi
if ! printf '%s' "$status_json" | grep -q '"external_origin":"https://wb.example"'; then
  fail "HED-WB-0006" "public-base origin handoff missing from facade diagnostic"
fi
if printf '%s' "$status_json" | grep -qiE '(license|secret|token)[^,}]*:[^,}]*[^*\"]'; then
  fail "HED-WB-0006" "diagnostic contained an unredacted sensitive-looking value"
fi
log "DIAGNOSTICS=ok active=true normalizer_count=1 handoff=ok redacted=ok"

invite_json="$(curl -fsS --max-time 5 \
  "http://127.0.0.1:${APP_PORT}${MOUNT}/invite-link")"
invite_url="$(printf '%s' "$invite_json" | jq -r '.url')"
if ! INVITE_URL="$invite_url" EXPECTED_MOUNT="$MOUNT" \
  "$ROOT/.venv/bin/python" -c '
import os
from urllib.parse import parse_qs, urlsplit
url = urlsplit(os.environ["INVITE_URL"])
mount = os.environ["EXPECTED_MOUNT"]
assert (url.scheme, url.netloc) == ("https", "wb.example")
assert url.path == mount + "/invites/accept"
assert parse_qs(url.query) == {"token": ["smoke token +"]}
'; then
  fail "HED-WB-0006" "Workbench external invite URL was invalid"
fi
log "EXTERNAL_URL=ok invite_query=encoded mount_once=ok"

if ! uv run --python 3.12 --directory "$ROOT" python scripts/smoke_workbench_websocket.py \
  "ws://127.0.0.1:${APP_PORT}${MOUNT}/ws"; then
  fail "HED-WB-0006" "mounted WebSocket probe failed"
fi
log "WEBSOCKET=ok"

# Stop the active launcher and import the same facade with no Workbench state.
kill "$APP_PID" >/dev/null 2>&1 || true
wait "$APP_PID" >/dev/null 2>&1 || true
APP_PID=""
(
  cd "$COMPOSE_DIR"
  env \
    -u RS_SERVER_URL \
    -u HEDRON_ROOT_PATH \
    -u HEDRON_WORKBENCH_RESOLVED_MOUNT \
    -u HEDRON_WORKBENCH_RESOLVED_PUBLIC_BASE \
    -u HEDRON_WORKBENCH_RESOLVED_MODE \
    -u HEDRON_WORKBENCH_RESOLVED_SOURCE \
    -u HEDRON_WORKBENCH_MOUNT \
    -u HEDRON_WORKBENCH_MODE \
    -u HEDRON_WORKBENCH_FORCE \
    HOST=public.example PORT=99999 BASE_PATH=/generic-platform \
    PYTHONPATH="$COMPOSE_DIR" uv run --python 3.12 --directory "$ROOT" \
      python -m uvicorn app_facade:app --host 127.0.0.1 --port "$LOCAL_PORT"
) >"$APP_LOG" 2>&1 &
APP_PID=$!

local_ready=0
for _ in $(seq 1 40); do
  if curl -fsS -o /dev/null --max-time 2 "http://127.0.0.1:${LOCAL_PORT}/" >/dev/null 2>&1; then
    local_ready=1
    break
  fi
  if ! kill -0 "$APP_PID" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
if [[ "$local_ready" -ne 1 ]]; then
  log "app_log=$(redact_stream < "$APP_LOG" | tail -n 50)"
  fail "HED-WB-0005" "facade did not start as an ordinary Hedron app"
fi

local_headers="$SMOKE_DIR/local.headers"
local_body="$(curl -fsS -D "$local_headers" --max-time 5 "http://127.0.0.1:${LOCAL_PORT}/")"
if ! printf '%s' "$local_body" | grep -q "Hello from Hedron on Workbench"; then
  fail "HED-WB-0006" "ordinary Hedron page behavior changed"
fi
if ! grep -qi 'Path=/' "$local_headers"; then
  fail "HED-WB-0006" "ordinary Hedron cookie Path was not root-scoped"
fi
local_status="$(curl -fsS --max-time 5 "http://127.0.0.1:${LOCAL_PORT}/workbench-status")"
if ! printf '%s' "$local_status" | grep -q '"active":false'; then
  fail "HED-WB-0006" "facade unexpectedly activated outside Workbench"
fi
if ! printf '%s' "$local_status" | grep -q '"app_cookie_path":"/"'; then
  fail "HED-WB-0006" "ordinary Hedron diagnostic did not retain root cookie scope"
fi
if printf '%s' "$local_status" | grep -q 'generic-platform'; then
  fail "HED-WB-0006" "generic BASE_PATH alias changed the ordinary Hedron app"
fi
log "OUTSIDE_WORKBENCH=ok active=false hedron_parity=ok generic_aliases_ignored=ok"

log "RESULT=pass"
log "REALWB-029 end $(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit 0
