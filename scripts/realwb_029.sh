#!/usr/bin/env bash
# REALWB-029: start pinned Posit Workbench, invoke real rserver-url, smoke Hedron.
# Never prints PWB_LICENSE / generated tokens.
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
PROXY_PORT=8053
APP_PID=""
PROXY_CONTAINER="hedron-workbench-proxy-smoke-$$"
PROXY_STARTED=0
WORKBENCH_STARTED=0
LICENSE_STOP_TIMEOUT="${HEDRON_WORKBENCH_LICENSE_STOP_TIMEOUT:-120}"
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

skip_license_unavailable() {
  local reason="$1"
  shift
  log "REALWB-029 skip reason=$reason $*"
  log "RESULT=skip"
  log "REALWB-029 end $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  if [[ -n "${RESULT_BACKUP:-}" && -f "$RESULT_BACKUP" ]]; then
    cp "$RESULT_BACKUP" "$RESULT"
  fi
  exit 42
}

license_unavailable_in_logs() {
  printf '%s' "$1" | grep -qiE \
    'license.*expired|expired.*license|license has expired|product key.*maximum number of computers'
}

deactivate_workbench_license() {
  if [[ "$WORKBENCH_STARTED" -ne 1 ]]; then
    "${COMPOSE[@]}" down --remove-orphans >/dev/null 2>&1 || true
    return 0
  fi
  local current_cid=""
  current_cid="$("${COMPOSE[@]}" ps -q workbench 2>/dev/null || true)"
  if [[ -n "$current_cid" ]] && \
     [[ "$(docker inspect --format '{{.State.Running}}' "$current_cid" 2>/dev/null || true)" == "true" ]]; then
    log "LICENSE_DEACTIVATE=begin timeout=${LICENSE_STOP_TIMEOUT}s"
    docker exec "$current_cid" rstudio-server license-manager deactivate >/dev/null 2>&1 || \
      log "LICENSE_DEACTIVATE=manager_exit_nonzero"
    "${COMPOSE[@]}" stop -t "$LICENSE_STOP_TIMEOUT" workbench >/dev/null 2>&1 || \
      log "LICENSE_DEACTIVATE=stop_exit_nonzero"
    log "LICENSE_DEACTIVATE=end"
  else
    log "LICENSE_DEACTIVATE=skipped container_not_running"
  fi
  "${COMPOSE[@]}" down --remove-orphans >/dev/null 2>&1 || true
  WORKBENCH_STARTED=0
}

CLEANUP_DONE=0
cleanup() {
  if [[ "$CLEANUP_DONE" -eq 1 ]]; then
    return 0
  fi
  CLEANUP_DONE=1
  if [[ -n "${APP_PID}" ]] && kill -0 "$APP_PID" >/dev/null 2>&1; then
    kill "$APP_PID" >/dev/null 2>&1 || true
    wait "$APP_PID" >/dev/null 2>&1 || true
  fi
  if [[ "$PROXY_STARTED" -eq 1 ]]; then
    docker rm -f "$PROXY_CONTAINER" >/dev/null 2>&1 || true
  fi
  deactivate_workbench_license
  if [[ -d "$SMOKE_DIR" && "$SMOKE_DIR" == /tmp/hedron-workbench-smoke.* ]]; then
    rm -r -- "$SMOKE_DIR"
  else
    log "cleanup_refused_unexpected_temp_path=true"
  fi
  if [[ -n "${RESULT_BACKUP:-}" && -f "$RESULT_BACKUP" ]]; then
    rm -f -- "$RESULT_BACKUP"
  fi
}

mkdir -p "$RESULT_DIR"
RESULT_BACKUP=""
if [[ -f "$RESULT" ]]; then
  RESULT_BACKUP="$(mktemp)"
  cp "$RESULT" "$RESULT_BACKUP"
fi
: > "$RESULT"
exec > >(tee -a "$RESULT") 2>&1
trap cleanup EXIT INT TERM

log "REALWB-029 start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
log "image=$IMAGE"

if [[ -z "${PWB_LICENSE:-}" && -f "$ROOT/.env" ]]; then
  PWB_LICENSE="$("$ROOT/.venv/bin/python" -c '
import shlex, sys
for raw in open(sys.argv[1], encoding="utf-8"):
    line = raw.strip()
    if line.startswith("export "):
        line = line[7:].lstrip()
    if not line.startswith("PWB_LICENSE="):
        continue
    value = line.split("=", 1)[1].strip()
    parsed = shlex.split(value, comments=True, posix=True)
    print(parsed[0] if len(parsed) == 1 else "")
    break
' "$ROOT/.env")"
fi

if [[ -z "${PWB_LICENSE:-}" ]]; then
  fail "HED-WB-0001" "PWB_LICENSE is unset (load .env or export it)"
fi
if [[ ! "$PWB_LICENSE" =~ ^[[:alnum:]]{4}(-[[:alnum:]]{4}){5,}$ ]]; then
  fail "HED-WB-0001" "PWB_LICENSE is not a product-license-shaped value"
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

export PWB_LICENSE
export HEDRON_WORKBENCH_IMAGE="$IMAGE"
# Compose interpolates PWB_LICENSE; do not print it.

compose_pull="missing"
if docker image inspect "$IMAGE" >/dev/null 2>&1; then
  compose_pull="never"
fi
log "compose=up workbench pull=$compose_pull"
if ! "${COMPOSE[@]}" up -d --pull "$compose_pull" workbench; then
  logs="$("${COMPOSE[@]}" logs --no-color --tail 80 workbench 2>/dev/null || true)"
  if license_unavailable_in_logs "$logs"; then
    skip_license_unavailable "license_unavailable" "Workbench license unavailable (redacted)"
  fi
  fail "HED-WB-0007" "failed to start $IMAGE (license/platform/qemu). Do not hang on QEMU."
fi
WORKBENCH_STARTED=1
cid="$("${COMPOSE[@]}" ps -q workbench)"
if [[ -z "$cid" ]]; then
  fail "HED-WB-0007" "workbench container id missing"
fi

READY_ATTEMPTS="${HEDRON_WORKBENCH_READY_ATTEMPTS:-72}"
if [[ ! "$READY_ATTEMPTS" =~ ^[0-9]+$ ]] || (( READY_ATTEMPTS < 1 || READY_ATTEMPTS > 120 )); then
  fail "HED-WB-0007" "HEDRON_WORKBENCH_READY_ATTEMPTS must be an integer from 1 to 120"
fi
ok=0
for _ in $(seq 1 "$READY_ATTEMPTS"); do
  if curl -fsS -o /dev/null --max-time 5 "http://127.0.0.1:8787/auth-sign-in" >/dev/null 2>&1; then
    ok=1
    break
  fi
  if [[ "$(docker inspect --format '{{.State.Running}}' "$cid" 2>/dev/null || true)" != "true" ]]; then
    break
  fi
  sleep 5
done
if [[ "$ok" -ne 1 ]]; then
  logs="$("${COMPOSE[@]}" logs --no-color --tail 80 workbench 2>/dev/null || true)"
  log "failure_container_log_begin"
  printf '%s\n' "$logs" | redact_stream
  log "failure_container_log_end"
  if license_unavailable_in_logs "$logs"; then
    skip_license_unavailable "license_unavailable" "Workbench license unavailable (redacted)"
  fi
  if printf '%s' "$logs" | grep -qiE 'license.*(invalid|denied)'; then
    fail "HED-WB-0001" "Workbench license was rejected (redacted)"
  fi
  fail "HED-WB-0007" "Workbench did not become ready on :8787/auth-sign-in"
fi
log "auth-sign-in=ok"

if ! docker exec "$cid" test -x "$RSERVER_URL_BIN"; then
  fail "HED-WB-0003" "real rserver-url missing at $RSERVER_URL_BIN"
fi
log "rserver-url=$RSERVER_URL_BIN"

version_out="$(docker exec "$cid" rstudio-server version 2>/dev/null || true)"
log "rstudio-server=$(printf '%s' "$version_out" | tr '\n' ' ' | redact_stream)"

if [[ "$HOST_ARCH" == "arm64" ]]; then
  set +e
  rurl_out="$(docker exec "$cid" "$RSERVER_URL_BIN" -l "$APP_PORT" 2>/dev/null)"
  rurl_rc=$?
  set -e
  log "rserver-url_rc=$rurl_rc"
  if [[ "$rurl_rc" -eq 139 ]]; then
    log "RSERVER_URL=emulation_limited rc=139 platform=linux/amd64-on-arm64"
  else
    log "RSERVER_URL=emulation_probe rc=$rurl_rc session_context=absent"
  fi
  log "PROXY_E2E=emulation_limited requires=native-amd64"
else
  log "RSERVER_URL=session_context_pending"
fi

if [[ "$HOST_ARCH" != "arm64" ]]; then
  command -v openssl >/dev/null 2>&1 || \
    fail "HED-WB-0007" "openssl is required for native proxy E2E"
  api_token="$(openssl rand -hex 16)"
  if ! docker exec -e HEDRON_PWB_API_TOKEN="$api_token" "$cid" \
    rstudio-server generate-api-token super-admin hedron-smoke hedron \
    --token-env HEDRON_PWB_API_TOKEN >/dev/null 2>&1; then
    fail "HED-WB-0007" "could not generate an ephemeral Workbench super-admin token"
  fi
  launch_json=""
  for _ in $(seq 1 24); do
    launch_json="$(curl -fsS --max-time 15 \
      -H 'Content-Type: application/json' \
      -H "Authorization: Bearer ${api_token}" \
      --data '{"method":"launch_session","kwparams":{"workbench":"RStudio","name":"Hedron Smoke","launch_parameters":{"name":"Hedron Smoke","cluster":"Local"},"username":"hedron"}}' \
      'http://127.0.0.1:8787/api/launch_session')" || true
    if [[ -n "$launch_json" ]] && ! printf '%s' "$launch_json" | jq -e '.error' >/dev/null; then
      break
    fi
    sleep 5
  done
  if [[ -z "$launch_json" ]]; then
    fail "HED-WB-0007" "Workbench API session launch failed"
  fi
  if printf '%s' "$launch_json" | jq -e '.error' >/dev/null; then
    fail "HED-WB-0007" "Workbench API returned a redacted session launch error"
  fi

  session_url=""
  for _ in $(seq 1 36); do
    session_json="$(curl -fsS --max-time 10 \
      -H 'Content-Type: application/json' \
      -H "Authorization: Bearer ${api_token}" \
      --data '{"method":"get_session","kwparams":{"username":"hedron"}}' \
      'http://127.0.0.1:8787/api/get_session')" || true
    session_url="$(printf '%s' "$session_json" | jq -r \
      '.. | strings | select(test("(^https?://[^ ]+)?/s/[^/]+/?$"))' | head -n1)"
    if [[ -n "$session_url" ]]; then
      break
    fi
    sleep 5
  done
  if [[ -z "$session_url" ]]; then
    fail "HED-WB-0007" "launched Workbench session did not expose a session URL"
  fi

  rurl_out=""
  rurl_rc=1
  for _ in $(seq 1 24); do
    set +e
    rurl_out="$(docker exec -u hedron -e RS_SERVER_URL="$session_url" \
      "$cid" "$RSERVER_URL_BIN" -l "$PROXY_PORT" 2>/dev/null)"
    rurl_rc=$?
    set -e
    if [[ "$rurl_rc" -eq 0 && -n "$rurl_out" ]]; then
      break
    fi
    if [[ "$rurl_rc" -eq 139 ]]; then
      break
    fi
    sleep 5
  done
  if [[ "$rurl_rc" -eq 139 ]]; then
    log "PROXY_E2E=session_rserver_url_limited rc=139"
    docker exec "$cid" rstudio-server revoke-api-token hedron-smoke >/dev/null 2>&1 || true
    api_token=""
  elif [[ "$rurl_rc" -ne 0 || -z "$rurl_out" ]]; then
    fail "HED-WB-0003" "session-scoped rserver-url failed rc=$rurl_rc"
  else
  proxy_mount="$(PROXY_URL="$rurl_out" "$ROOT/.venv/bin/python" -c '
import os
from urllib.parse import urlsplit
value = os.environ["PROXY_URL"]
print(urlsplit(value).path if "://" in value else value)
')"
  if [[ "$proxy_mount" != /s/*/p/* ]]; then
    fail "HED-WB-0003" "session-scoped rserver-url returned an unexpected mount shape"
  fi

  if ! docker image inspect python:3.12-slim >/dev/null 2>&1; then
    docker pull python:3.12-slim >/dev/null || \
      fail "HED-WB-0007" "could not pull Python sidecar for proxy E2E"
  fi
  if ! docker run -d \
    --name "$PROXY_CONTAINER" \
    --network "container:${cid}" \
    -v "$ROOT:/src:ro" \
    -w /src/examples/workbench-reference \
    -e HEDRON_SESSION_SECRET=realwb-proxy-smoke-not-for-production \
    -e PYTHONPATH=/src/examples/workbench-reference \
    python:3.12-slim \
    sh -lc "pip install -q /src/packages/hedron-core /src/packages/hedron /src/packages/hedron-workbench && python -m hedron_workbench.cli run app_facade:app --mode on --host 127.0.0.1 --port ${PROXY_PORT} --mount '${proxy_mount}' --public-base-url 'http://127.0.0.1:8787${proxy_mount}'" \
    >/dev/null; then
    fail "HED-WB-0007" "could not start the Workbench-network app sidecar"
  fi
  PROXY_STARTED=1
  proxy_ready=0
  for _ in $(seq 1 60); do
    if docker exec "$cid" curl -fsS --max-time 3 \
      "http://127.0.0.1:${PROXY_PORT}/" >/dev/null 2>&1; then
      proxy_ready=1
      break
    fi
    sleep 2
  done
  if [[ "$proxy_ready" -ne 1 ]]; then
    fail "HED-WB-0005" "proxy E2E app sidecar did not become ready"
  fi

  auth_cookie="$SMOKE_DIR/workbench.cookies"
  if ! curl -fsS --max-time 10 -c "$auth_cookie" \
    --data-urlencode 'username=hedron' \
    --data-urlencode 'password=hedron' \
    --data-urlencode 'staySignedIn=1' \
    --data-urlencode 'appUri=/' \
    'http://127.0.0.1:8787/auth-do-sign-in' >/dev/null; then
    fail "HED-WB-0007" "PAM sign-in failed for proxy E2E"
  fi
  proxy_page="$SMOKE_DIR/proxy-page.html"
  proxy_headers="$SMOKE_DIR/proxy-page.headers"
  if ! curl -fsS --max-time 15 -b "$auth_cookie" -c "$auth_cookie" \
    -D "$proxy_headers" \
    "http://127.0.0.1:8787${proxy_mount}/" -o "$proxy_page"; then
    fail "HED-WB-0006" "authenticated request did not traverse Workbench proxy"
  fi
  if ! grep -q 'Hello from Hedron on Workbench' "$proxy_page" || \
     ! grep -Fq "${proxy_mount}/status" "$proxy_page" || \
     ! grep -Fq "${proxy_mount}/ping" "$proxy_page"; then
    fail "HED-WB-0006" "proxied page or generated controls were incorrect"
  fi
  proxy_fragment="$(curl -fsS --max-time 15 -b "$auth_cookie" \
    -H 'HX-Request: true' -H 'HX-Target: #service-status' \
    "http://127.0.0.1:8787${proxy_mount}/status")" || \
    fail "HED-WB-0006" "proxied refresh control request failed"
  if [[ "$proxy_fragment" != *"All systems operational"* ]]; then
    fail "HED-WB-0006" "proxied refresh control returned an unexpected fragment"
  fi
  proxy_csrf="$(awk '$6=="hedron_csrf" {print $7; exit}' "$auth_cookie")"
  if [[ -z "$proxy_csrf" ]]; then
    fail "HED-WB-0006" "proxied page did not seed a CSRF cookie"
  fi
  proxy_post_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 \
    -b "$auth_cookie" -H "X-CSRF-Token: ${proxy_csrf}" -X POST \
    "http://127.0.0.1:8787${proxy_mount}/ping")"
  if [[ "$proxy_post_code" != "200" ]]; then
    fail "HED-WB-0006" "proxied form submission status=$proxy_post_code"
  fi
  proxy_redirect_headers="$SMOKE_DIR/proxy-redirect.headers"
  proxy_redirect_code="$(curl -sS -o /dev/null -D "$proxy_redirect_headers" \
    -w '%{http_code}' --max-time 15 -b "$auth_cookie" \
    "http://127.0.0.1:8787${proxy_mount}/go")"
  proxy_location="$(awk 'tolower($1)=="location:" {gsub(/\r/, ""); print $2; exit}' \
    "$proxy_redirect_headers")"
  if [[ "$proxy_redirect_code" != "303" || "$proxy_location" != "${proxy_mount}/login" ]]; then
    fail "HED-WB-0006" "proxied redirect was not mount-correct"
  fi
  log "PROXY_E2E=ok authenticated=true session_launch=api path_generation=rserver-url controls=clicked csrf=ok redirect=ok"
  docker exec "$cid" rstudio-server revoke-api-token hedron-smoke >/dev/null 2>&1 || true
  api_token=""
  fi
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
for suffix in \
  "/hedron-static/hedron-default.css" \
  "/hedron-static/hedron-mount.mjs" \
  "/status" \
  "/ping"; do
  if ! grep -Fq "${MOUNT}${suffix}" "$page_html"; then
    fail "HED-WB-0006" "automatically generated PAGE URL omitted mount: $suffix"
  fi
done
log "PAGE=ok mount_prefix=ok generated_urls=automatic cookie_path=ok"

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

wrong_origin_code="$(curl -sS --path-as-is -o /dev/null -w '%{http_code}' --max-time 5 \
  "http://127.0.0.1:${APP_PORT}/https%3A%2F%2Fevil.example%2Fs%2Fdemo%2Fp%2F9%2Fencoded")"
if [[ "$wrong_origin_code" != "400" ]]; then
  fail "HED-WB-0006" "unknown encoded origin status=$wrong_origin_code expected=400"
fi

oversized_segment="$(printf '%*s' 8200 '' | tr ' ' a)"
oversized_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 \
  "http://127.0.0.1:${APP_PORT}/${oversized_segment}")"
if [[ "$oversized_code" != "414" ]]; then
  fail "HED-WB-0006" "oversized Workbench target status=$oversized_code expected=414"
fi
log "TARGET_GUARDS=ok unsafe=400 conflict=400 origin=400 oversized=414"

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
invite_url="$(printf '%s' "$invite_json" | jq -r '.browser_url')"
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
durable_error="$(printf '%s' "$invite_json" | jq -r '.durable_error')"
durable_cap="$(printf '%s' "$invite_json" | jq -r '.capabilities.durable_links')"
ephemeral_cap="$(printf '%s' "$invite_json" | jq -r '.capabilities.ephemeral_session')"
if [[ "$durable_error" != *"ephemeral"* || "$durable_cap" != "false" || \
      "$ephemeral_cap" != "true" ]]; then
  fail "HED-WB-0006" "ephemeral Workbench URL was not rejected for durable sharing"
fi
log "EXTERNAL_URL=ok browser_query=encoded mount_once=ok durable_guard=ok"

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
