#!/usr/bin/env bash
# Install one browser and its OS dependencies; bound a stalled apt/download.
set -euo pipefail

browser="${1:?browser name required}"
python_version="${2:-3.12}"
export DEBIAN_FRONTEND=noninteractive

timeout --kill-after=30 600 uv run --python "$python_version" \
  playwright install --with-deps "$browser"
