#!/usr/bin/env bash
# Convenience wrapper for docs builds (same env as `uv run --group docs mkdocs …`).
set -euo pipefail
exec mkdocs "$@"
