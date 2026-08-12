#!/usr/bin/env bash
# Backward-compatible entrypoint — REALWB-030 dual-package smoke lives in realwb_smoke.sh.
exec "$(cd "$(dirname "$0")" && pwd)/realwb_smoke.sh" "$@"
