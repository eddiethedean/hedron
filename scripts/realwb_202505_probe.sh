#!/usr/bin/env bash
# REALWB-030-202505: licensed minimum-floor Workbench probe (2025.05.1).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export HEDRON_REALWB_PROBE_ID=REALWB-030-202505
export HEDRON_REALWB_RESULT_DIR="$ROOT/docs/acceptance/realwb-030-202505"
export HEDRON_REALWB_IMAGE_DIGEST=sha256:2b017722bef663940d345178d14d196d8716b37d9cf8a52d3da7caba477e7d23
export HEDRON_WORKBENCH_IMAGE="posit/workbench@${HEDRON_REALWB_IMAGE_DIGEST}"
export HEDRON_WORKBENCH_DOCKER_PLATFORM=linux/amd64
exec bash "$ROOT/scripts/realwb_smoke.sh"
