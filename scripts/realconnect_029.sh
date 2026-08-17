#!/usr/bin/env bash
# REALCONNECT-029: deploy the local Hedron facade into pinned Posit Connect.
# Never prints CONNECT_API_KEY, PCT_LICENSE, bootstrap secrets, or publishing keys.
set -euo pipefail
umask 077

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RESULT_DIR="$ROOT/docs/acceptance/realconnect-029"
RESULT="$RESULT_DIR/RESULT.log"
IMAGE_DIGEST="sha256:ae5753745ddc576cca06ad7466a370e18bc54580b154f4b5bcbef9390f1c54a9"
IMAGE="${HEDRON_CONNECT_IMAGE:-posit/connect@${IMAGE_DIGEST}}"
CONNECT_PORT="${HEDRON_CONNECT_PORT:-3939}"
LOCAL_PORT="${HEDRON_CONNECT_LOCAL_PORT:-8056}"
CONTAINER="hedron-connect-smoke-$$"
CLIENT_VERSION="1.29.0"
SMOKE_DIR="$(mktemp -d /tmp/hedron-connect-smoke.XXXXXX)"
CLIENT_DIR="$SMOKE_DIR/rsconnect-venv"
APP_PID=""
CONTAINER_STARTED=0
LICENSE_STOP_TIMEOUT="${HEDRON_CONNECT_LICENSE_STOP_TIMEOUT:-120}"
CONNECT_LICENSE_MANAGER="/opt/rstudio-connect/bin/license-manager"

redact_stream() {
  sed -E \
    -e 's/[A-Za-z0-9]{4}(-[A-Za-z0-9]{4}){5,}/***/g' \
    -e 's/[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}/***/g' \
    -e 's/(api[_ -]?key|token|secret)([=:][[:space:]]*)[^[:space:],]+/\1\2***/Ig'
}

log() {
  printf '%s\n' "$*" | redact_stream
}

fail() {
  local code="$1"
  shift
  log "REALCONNECT-029 $code $*"
  log "RESULT=fail"
  exit 1
}

deactivate_connect_license() {
  if [[ "$CONTAINER_STARTED" -ne 1 ]]; then
    return 0
  fi
  if [[ "$(docker inspect --format '{{.State.Running}}' "$CONTAINER" 2>/dev/null || true)" == "true" ]]; then
    log "LICENSE_DEACTIVATE=begin timeout=${LICENSE_STOP_TIMEOUT}s"
    docker exec "$CONTAINER" "$CONNECT_LICENSE_MANAGER" deactivate >/dev/null 2>&1 || \
      log "LICENSE_DEACTIVATE=manager_exit_nonzero"
    log "LICENSE_DEACTIVATE=end"
  else
    log "LICENSE_DEACTIVATE=skipped container_not_running"
  fi
  docker stop --timeout "$LICENSE_STOP_TIMEOUT" "$CONTAINER" >/dev/null 2>&1 || \
    log "LICENSE_DEACTIVATE=stop_exit_nonzero"
  docker rm "$CONTAINER" >/dev/null 2>&1 || true
  CONTAINER_STARTED=0
}

cleanup() {
  local exit_status=$?
  if [[ -n "$APP_PID" ]] && kill -0 "$APP_PID" >/dev/null 2>&1; then
    kill -- -"$APP_PID" >/dev/null 2>&1 || kill "$APP_PID" >/dev/null 2>&1 || true
    wait "$APP_PID" >/dev/null 2>&1 || true
  fi
  if [[ "$CONTAINER_STARTED" -eq 1 ]]; then
    if [[ "$exit_status" -ne 0 ]]; then
      log "failure_container_log_begin"
      docker logs --tail 200 "$CONTAINER" 2>&1 | redact_stream || true
      log "failure_container_log_end"
    fi
    deactivate_connect_license
  fi
  if [[ -d "$SMOKE_DIR" && "$SMOKE_DIR" == /tmp/hedron-connect-smoke.* ]]; then
    rm -r -- "$SMOKE_DIR"
  else
    log "cleanup_refused_unexpected_temp_path=true"
  fi
  return "$exit_status"
}

mkdir -p "$RESULT_DIR"
: > "$RESULT"
exec > >(tee -a "$RESULT") 2>&1
trap cleanup EXIT

log "REALCONNECT-029 start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
log "image=$IMAGE"
log "host_arch=$(uname -m)"

if [[ -z "${CONNECT_API_KEY:-}" && -f "$ROOT/.env" ]]; then
  CONNECT_API_KEY="$("$ROOT/.venv/bin/python" -c '
import shlex, sys
for raw in open(sys.argv[1], encoding="utf-8"):
    line = raw.strip()
    if line.startswith("export "):
        line = line[7:].lstrip()
    if not line.startswith("CONNECT_API_KEY="):
        continue
    value = line.split("=", 1)[1].strip()
    parsed = shlex.split(value, comments=True, posix=True)
    print(parsed[0] if len(parsed) == 1 else "")
    break
' "$ROOT/.env")"
fi

if [[ -z "${CONNECT_API_KEY:-}" ]]; then
  fail "HED-CONNECT-0001" "CONNECT_API_KEY is unset (load .env or export it)"
fi
if [[ ! "$CONNECT_API_KEY" =~ ^[[:alnum:]]{4}(-[[:alnum:]]{4}){5,}$ ]]; then
  fail "HED-CONNECT-0001" "CONNECT_API_KEY is not a product-license-shaped value"
fi
if ! command -v docker >/dev/null 2>&1 || ! docker info >/dev/null 2>&1; then
  fail "HED-CONNECT-0002" "docker is required and must be reachable"
fi
if ! command -v uv >/dev/null 2>&1; then
  fail "HED-CONNECT-0002" "uv is required for the temporary rsconnect client"
fi
for command in curl jq openssl rsync; do
  command -v "$command" >/dev/null 2>&1 || \
    fail "HED-CONNECT-0002" "$command is required for the Connect smoke"
done

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  docker pull "$IMAGE" >/dev/null || \
    fail "HED-CONNECT-0002" "could not pull the pinned Connect image"
fi
resolved_digests="$(docker image inspect "$IMAGE" --format '{{join .RepoDigests ","}}' 2>/dev/null || true)"
if [[ "$IMAGE" == *"@sha256:"* && "$resolved_digests" != *"$IMAGE_DIGEST"* ]]; then
  fail "HED-CONNECT-0002" "cached Connect image did not match the pinned digest"
fi
log "image_digest=$IMAGE_DIGEST"

export PCT_LICENSE="$CONNECT_API_KEY"
unset CONNECT_API_KEY
openssl rand -base64 32 > "$SMOKE_DIR/bootstrap.key"
chmod 600 "$SMOKE_DIR/bootstrap.key"
BOOTSTRAP_SECRET="$(tr -d '\n' < "$SMOKE_DIR/bootstrap.key")"

log "container=start privileged=true"
if ! docker run -d \
  --name "$CONTAINER" \
  --privileged \
  --stop-timeout 120 \
  -p "${CONNECT_PORT}:3939" \
  -e PCT_LICENSE="$PCT_LICENSE" \
  -e CONNECT_BOOTSTRAP_ENABLED=true \
  -e CONNECT_BOOTSTRAP_SECRETKEY="$BOOTSTRAP_SECRET" \
  -e CONNECT_APPLICATIONS_INHERITSYSTEMENVVARS=false \
  "$IMAGE" >/dev/null; then
  fail "HED-CONNECT-0002" "failed to start pinned Posit Connect image"
fi
CONTAINER_STARTED=1
unset PCT_LICENSE BOOTSTRAP_SECRET

healthy=0
for _ in $(seq 1 48); do
  if curl -fsS --max-time 5 "http://127.0.0.1:${CONNECT_PORT}/__ping__" >/dev/null 2>&1; then
    healthy=1
    break
  fi
  sleep 5
done
if [[ "$healthy" -ne 1 ]]; then
  logs="$(docker logs --tail 100 "$CONTAINER" 2>&1 | redact_stream || true)"
  log "connect_log=$logs"
  fail "HED-CONNECT-0003" "Connect did not become healthy"
fi
log "CONNECT_HEALTH=ok"

version_out="$(docker exec "$CONTAINER" /opt/rstudio-connect/bin/connect --version 2>/dev/null || true)"
log "connect_version=$(printf '%s' "$version_out" | tr '\n' ' ')"

UV_CACHE_DIR=/tmp/uv-cache uv venv "$CLIENT_DIR" --python 3.12 >/dev/null 2>&1
if ! UV_CACHE_DIR=/tmp/uv-cache uv pip install \
  --python "$CLIENT_DIR/bin/python" "rsconnect-python==${CLIENT_VERSION}" >/dev/null 2>&1; then
  fail "HED-CONNECT-0004" "could not install the pinned rsconnect-python client"
fi
log "rsconnect_python=$CLIENT_VERSION"

export CONNECT_BOOTSTRAP_SECRETKEY="$(tr -d '\n' < "$SMOKE_DIR/bootstrap.key")"
if ! "$CLIENT_DIR/bin/rsconnect" bootstrap \
  --raw --server "http://127.0.0.1:${CONNECT_PORT}" > "$SMOKE_DIR/api.key"; then
  fail "HED-CONNECT-0004" "one-time Connect API bootstrap failed"
fi
unset CONNECT_BOOTSTRAP_SECRETKEY
chmod 600 "$SMOKE_DIR/api.key"
test -s "$SMOKE_DIR/api.key" || fail "HED-CONNECT-0004" "bootstrap returned an empty key"
rm -- "$SMOKE_DIR/bootstrap.key"
log "CONNECT_BOOTSTRAP=ok"

BUNDLE="$SMOKE_DIR/bundle"
mkdir -p "$BUNDLE"
cp examples/connect-reference/app.py \
  examples/connect-reference/requirements.txt \
  examples/connect-reference/.python-version \
  "$BUNDLE/"
rsync -a --exclude '__pycache__' packages/hedron/src/hedron/ "$BUNDLE/hedron/"
rsync -a --exclude '__pycache__' packages/hedron-core/src/hedron_core/ "$BUNDLE/hedron_core/"
rsync -a --exclude '__pycache__' \
  packages/hedron-workbench/src/hedron_workbench/ "$BUNDLE/hedron_workbench/"
rsync -a --exclude '__pycache__' \
  packages/fastapi-workbench/src/fastapi_workbench/ "$BUNDLE/fastapi_workbench/"

export CONNECT_SERVER="http://127.0.0.1:${CONNECT_PORT}"
export CONNECT_API_KEY="$(tr -d '\n' < "$SMOKE_DIR/api.key")"
if ! "$CLIENT_DIR/bin/rsconnect" deploy fastapi \
  --entrypoint app:app \
  --title hedron-connect-smoke \
  "$BUNDLE" > "$SMOKE_DIR/deploy.log" 2>&1; then
  log "deploy_log=$(redact_stream < "$SMOKE_DIR/deploy.log" | tail -n 100)"
  fail "HED-CONNECT-0005" "FastAPI content deployment failed"
fi
unset CONNECT_SERVER CONNECT_API_KEY
log "CONNECT_DEPLOY=ok runtime=python-3.14.6 vendored_local_source=true"

BUNDLE_RECORD="$BUNDLE/rsconnect-python/bundle.json"
GUID="$($ROOT/.venv/bin/python -c \
  'import json,sys; print(next(iter(json.load(open(sys.argv[1])).values()))["app_guid"])' \
  "$BUNDLE_RECORD")"
if [[ -z "$GUID" ]]; then
  fail "HED-CONNECT-0005" "deployment record did not contain a content GUID"
fi
CONTENT_PATH="/content/${GUID}"
BASE="http://127.0.0.1:${CONNECT_PORT}${CONTENT_PATH}"
AUTH="$(tr -d '\n' < "$SMOKE_DIR/api.key")"

page_headers="$SMOKE_DIR/page.headers"
cookie_jar="$SMOKE_DIR/cookies"
if ! curl -fsS --max-time 15 \
  -H "Authorization: Key ${AUTH}" \
  -c "$cookie_jar" \
  -D "$page_headers" \
  "$BASE/" -o "$SMOKE_DIR/page.html"; then
  fail "HED-CONNECT-0006" "deployed PAGE request failed"
fi
if ! grep -q "Hello from Hedron on Connect" "$SMOKE_DIR/page.html"; then
  fail "HED-CONNECT-0006" "PAGE body missing expected text"
fi
if ! grep -qi "hedron_csrf=.*Path=${CONTENT_PATH}/" "$page_headers"; then
  fail "HED-CONNECT-0006" "Connect did not scope the CSRF cookie to the content path"
fi
if ! grep -qiE "session=.*Path=${CONTENT_PATH}/?([;[:space:]]|$)" "$page_headers"; then
  log "cookie_path_summary_begin"
  awk '
    BEGIN { IGNORECASE=1 }
    tolower($0) ~ /^set-cookie:/ {
      line=$0
      sub(/\r$/, "", line)
      name=line
      sub(/^set-cookie:[[:space:]]*/, "", name)
      sub(/=.*/, "", name)
      lower=tolower(line)
      if (match(lower, /;[[:space:]]*path=[^;]*/)) {
        print name " " substr(line, RSTART + 1, RLENGTH - 1)
      } else {
        print name " Path=<missing>"
      }
    }
  ' "$page_headers" | redact_stream
  log "cookie_path_summary_end"
  fail "HED-CONNECT-0006" "runtime root_path did not repair the session cookie Path"
fi
for suffix in \
  "/hedron-static/hedron-default.css" \
  "/hedron-static/hedron-mount.mjs" \
  "/status" \
  "/ping"; do
  if ! grep -Fq "${CONTENT_PATH}${suffix}" "$SMOKE_DIR/page.html"; then
    fail "HED-CONNECT-0006" "generated PAGE URL omitted the Connect prefix: $suffix"
  fi
done
log "PAGE=ok root_path=ok generated_urls=automatic cookie_path=runtime_repaired"

token="$(awk '$6=="hedron_csrf" {print $7; exit}' "$cookie_jar")"
if [[ -z "$token" ]]; then
  fail "HED-CONNECT-0006" "CSRF token cookie missing"
fi
if ! fragment="$(curl -fsS --max-time 15 \
  -H "Authorization: Key ${AUTH}" \
  -H 'HX-Request: true' \
  -H 'HX-Target: #h-view-status' \
  -b "$cookie_jar" \
  "$BASE/status")"; then
  fail "HED-CONNECT-0006" "FRAGMENT /status request failed"
fi
if ! printf '%s' "$fragment" | grep -q "All systems operational"; then
  fail "HED-CONNECT-0006" "FRAGMENT /status missing expected text"
fi
log "FRAGMENT=ok"

csrf_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 \
  -H "Authorization: Key ${AUTH}" \
  -H "X-CSRF-Token: ${token}" \
  -b "$cookie_jar" \
  -X POST "$BASE/ping")"
if [[ "$csrf_code" != "200" ]]; then
  fail "HED-CONNECT-0006" "CSRF POST /ping status=$csrf_code"
fi
log "CSRF=ok"

asset_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 \
  -H "Authorization: Key ${AUTH}" \
  "$BASE/hedron-static/hedron-default.css")"
if [[ "$asset_code" != "200" ]]; then
  fail "HED-CONNECT-0006" "mounted static asset status=$asset_code"
fi
log "ASSETS=ok"

docs_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 \
  -H "Authorization: Key ${AUTH}" "$BASE/docs")"
spec_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 \
  -H "Authorization: Key ${AUTH}" "$BASE/openapi.json")"
if [[ "$docs_code" != "200" || "$spec_code" != "200" ]]; then
  fail "HED-CONNECT-0006" "OpenAPI routes failed docs=$docs_code spec=$spec_code"
fi
log "OPENAPI=ok docs=$docs_code spec=$spec_code"

redirect_headers="$SMOKE_DIR/redirect.headers"
redirect_code="$(curl -sS -o /dev/null -D "$redirect_headers" -w '%{http_code}' --max-time 15 \
  -H "Authorization: Key ${AUTH}" "$BASE/go")"
redirect_location="$(awk 'tolower($1)=="location:" {gsub(/\r/, ""); print $2; exit}' \
  "$redirect_headers")"
if [[ "$redirect_code" != "303" || "$redirect_location" != "${CONTENT_PATH}/login" ]]; then
  fail "HED-CONNECT-0006" \
    "mounted redirect failed status=$redirect_code location=$redirect_location"
fi
if [[ "${redirect_location#"$CONTENT_PATH"}" == *"$CONTENT_PATH"* ]]; then
  fail "HED-CONNECT-0006" "mounted redirect duplicated the content prefix"
fi
log "REDIRECT=ok mount_once=ok"

scope_file="$SMOKE_DIR/scope.json"
scope_code="$(curl -sS -o "$scope_file" -w '%{http_code}' --max-time 15 \
  -H "Authorization: Key ${AUTH}" "$BASE/connect-scope")"
if [[ "$scope_code" != "200" ]]; then
  fail "HED-CONNECT-0006" "Connect diagnostic request status=$scope_code"
fi
scope_json="$(<"$scope_file")"
if [[ "$(printf '%s' "$scope_json" | jq -r '.posit_product')" != "CONNECT" ]] || \
   [[ "$(printf '%s' "$scope_json" | jq -r '.header_present')" != "true" ]] || \
   [[ "$(printf '%s' "$scope_json" | jq -r '.root_path')" != "$CONTENT_PATH" ]] || \
   [[ "$(printf '%s' "$scope_json" | jq -r '.header_path')" != "$CONTENT_PATH" ]] || \
   [[ "$(printf '%s' "$scope_json" | jq -r '.workbench_active')" != "false" ]] || \
   [[ "$(printf '%s' "$scope_json" | jq -r '.normalizer_count')" != "1" ]]; then
  fail "HED-CONNECT-0006" "Connect scope or inactive-facade diagnostic was unexpected"
fi

scope_public_base="$(printf '%s' "$scope_json" | jq -r '.public_base_valid')"
scope_secret_env="$(printf '%s' "$scope_json" | jq -r '.server_secret_env_present')"
scope_header_count="$(printf '%s' "$scope_json" | jq -r '.header_count')"
scope_client_host="$(printf '%s' "$scope_json" | jq -r '.client_host')"
if [[ "$scope_public_base" != "true" ]] || \
   [[ "$scope_secret_env" != "false" ]] || \
   [[ "$scope_header_count" != "1" ]] || \
   [[ -z "$scope_client_host" ]]; then
  fail "HED-CONNECT-0006" \
    "public base trust or secret isolation failed public_base=$scope_public_base secrets=$scope_secret_env headers=$scope_header_count client=$scope_client_host"
fi

invite_file="$SMOKE_DIR/invite.json"
invite_code="$(curl -sS -o "$invite_file" -w '%{http_code}' --max-time 15 \
  -H "Authorization: Key ${AUTH}" "$BASE/invite-link")"
if [[ "$invite_code" != "200" ]]; then
  fail "HED-CONNECT-0006" "request-aware external invite URL status=$invite_code"
fi
invite_json="$(<"$invite_file")"
invite_url="$(printf '%s' "$invite_json" | jq -r '.url')"
if ! INVITE_URL="$invite_url" CONTENT_PATH="$CONTENT_PATH" \
  "$ROOT/.venv/bin/python" -c '
import os
from urllib.parse import parse_qs, urlsplit
url = urlsplit(os.environ["INVITE_URL"])
mount = os.environ["CONTENT_PATH"]
assert url.scheme in {"http", "https"} and url.netloc
assert url.path == mount + "/invites/accept"
assert parse_qs(url.query) == {"token": ["smoke token +"]}
'; then
  fail "HED-CONNECT-0006" "request-aware external invite URL was invalid"
fi
log "DIAGNOSTICS=ok posit_product=CONNECT root_path=ok header=ok workbench_active=false"
log "EXTERNAL_URL=ok invite_query=encoded connect_runtime=verified secrets_isolated=ok"

encoded_headers="$SMOKE_DIR/encoded.headers"
encoded_code="$(curl -sS --path-as-is -o /dev/null -D "$encoded_headers" \
  -w '%{http_code}' --max-time 15 \
  -H "Authorization: Key ${AUTH}" \
  "$BASE/https%3A%2F%2Fwb.example%2Fs%2Fdemo%2Fp%2F9%2Fencoded")"
if [[ "$encoded_code" == "307" ]]; then
  encoded_location="$(awk 'tolower($1)=="location:" {gsub(/\r/, ""); print $2; exit}' \
    "$encoded_headers")"
  if ! encoded_follow_url="$("$ROOT/.venv/bin/python" scripts/check_same_origin_redirect.py \
    --origin "http://127.0.0.1:${CONNECT_PORT}" \
    --mount "$CONTENT_PATH" \
    --location "$encoded_location" 2>/dev/null)"; then
    fail "HED-CONNECT-0006" "encoded target redirect escaped origin or content path"
  fi
  encoded_follow_code="$(curl -sS --path-as-is -o /dev/null -w '%{http_code}' --max-time 15 \
    -H "Authorization: Key ${AUTH}" \
    "$encoded_follow_url")"
  if [[ "$encoded_follow_code" =~ ^2 ]]; then
    fail "HED-CONNECT-0006" "encoded Workbench target unexpectedly routed on Connect"
  fi
elif [[ "$encoded_code" != "404" ]]; then
  fail "HED-CONNECT-0006" \
    "inactive Workbench normalization changed Connect encoded target status=$encoded_code"
fi
log "WORKBENCH_ISOLATION=ok encoded_target=$encoded_code external_escape=blocked"

if ! "$ROOT/.venv/bin/python" scripts/smoke_workbench_websocket.py \
  "ws://127.0.0.1:${CONNECT_PORT}${CONTENT_PATH}/ws" \
  --authorization-key-file "$SMOKE_DIR/api.key"; then
  fail "HED-CONNECT-0006" "mounted WebSocket probe failed"
fi
log "WEBSOCKET=ok"

APP_LOG="$SMOKE_DIR/local-app.log"
(
  cd "$ROOT/examples/connect-reference"
  env \
    -u CONNECT_API_KEY \
    -u CONNECT_SERVER \
    -u CONNECT_CONTENT_GUID \
    -u POSIT_PRODUCT \
    -u RS_SERVER_URL \
    -u HEDRON_ROOT_PATH \
    -u HEDRON_WORKBENCH_RESOLVED_MOUNT \
    -u HEDRON_WORKBENCH_RESOLVED_PUBLIC_BASE \
    -u HEDRON_WORKBENCH_RESOLVED_MODE \
    -u HEDRON_WORKBENCH_RESOLVED_SOURCE \
    HOST=public.example PORT=99999 BASE_PATH=/generic-platform \
    PYTHONPATH="$ROOT/examples/connect-reference" \
      "$ROOT/.venv/bin/python" -m uvicorn app:app --host 127.0.0.1 --port "$LOCAL_PORT"
) > "$APP_LOG" 2>&1 &
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
  fail "HED-CONNECT-0007" "reference app did not start outside Connect"
fi
if ! local_body="$(curl -fsS --max-time 5 "http://127.0.0.1:${LOCAL_PORT}/")"; then
  fail "HED-CONNECT-0007" "ordinary local PAGE request failed"
fi
if ! printf '%s' "$local_body" | grep -q "Hello from Hedron on Connect"; then
  fail "HED-CONNECT-0007" "ordinary local Hedron behavior changed"
fi
if ! local_scope="$(curl -fsS --max-time 5 \
  "http://127.0.0.1:${LOCAL_PORT}/connect-scope")"; then
  fail "HED-CONNECT-0007" "ordinary local diagnostic request failed"
fi
if [[ "$(printf '%s' "$local_scope" | jq -r '.workbench_active')" != "false" ]] || \
   [[ "$(printf '%s' "$local_scope" | jq -r '.root_path')" != "" ]] || \
   [[ "$(printf '%s' "$local_scope" | jq -r '.app_cookie_path')" != "/" ]] || \
   [[ "$(printf '%s' "$local_scope" | jq -r '.public_base_valid')" != "false" ]]; then
  fail "HED-CONNECT-0007" "outside-Connect facade parity diagnostic failed"
fi
if printf '%s' "$local_scope" | grep -q 'generic-platform'; then
  fail "HED-CONNECT-0007" "generic BASE_PATH alias changed the ordinary app"
fi
log "OUTSIDE_CONNECT=ok hedron_parity=ok generic_aliases_ignored=ok"

log "RESULT=pass"
log "REALCONNECT-029 end $(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit 0
