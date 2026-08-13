#!/usr/bin/env bash
# REALCONNECT-033-202506: licensed minimum-floor Connect probe (2025.06.0).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export HEDRON_CONNECT_PROBE_ID=REALCONNECT-033-202506
export HEDRON_CONNECT_RESULT_DIR="$ROOT/docs/acceptance/realconnect-033-202506"
export HEDRON_CONNECT_IMAGE_DIGEST=sha256:d1921d6dd4344f2e0c3066a29338fc13f7f9ea8b6b31330a7cc6d7df4b4fcfa0
export HEDRON_CONNECT_IMAGE="posit/connect@${HEDRON_CONNECT_IMAGE_DIGEST}"
export HEDRON_CONNECT_DOCKER_PLATFORM=linux/amd64
export HEDRON_CONNECT_BUNDLE_PYTHON=3.12.1
export HEDRON_CONNECT_BUNDLE_MODE=wheels
export HEDRON_CONNECT_WRITE_FIXTURES=0
exec bash "$ROOT/scripts/realconnect_033_probe.sh"
