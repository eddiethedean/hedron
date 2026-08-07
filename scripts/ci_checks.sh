#!/usr/bin/env bash
# Shared CI check suites for commit CI and release CI.
#
# Workflows own checkout / uv / toolchain / sync / Playwright browser install.
# This script owns the actual check commands so there is one place to edit them.
#
# Usage:
#   scripts/ci_checks.sh test [--python 3.12]
#   scripts/ci_checks.sh quality [--python 3.12]
#   scripts/ci_checks.sh browser [--python 3.12]
#   scripts/ci_checks.sh evidence [--python 3.12] [--gate-version 0.20.0]
#   scripts/ci_checks.sh packaging [--python 3.12]
#   scripts/ci_checks.sh all [--python 3.12] [--gate-version 0.20.0] [--with-browser]
#
# Env:
#   HEDRON_BROWSER / HEDRON_BROWSER_ENGINE — browser suite (default engine: chromium)
#   HEDRON_GATE_VERSION — default for --gate-version
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-3.12}"
GATE_VERSION="${HEDRON_GATE_VERSION:-0.20.0}"
WITH_BROWSER=0

usage() {
  awk '
    NR == 1 { next }
    /^#/ {
      sub(/^# ?/, "")
      print
      next
    }
    { exit }
  ' "$0"
  exit "${1:-0}"
}

log() {
  printf '+ %s\n' "$*"
}

run() {
  log "$*"
  "$@"
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --python)
        PYTHON="${2:?--python requires a version}"
        shift 2
        ;;
      --gate-version)
        GATE_VERSION="${2:?--gate-version requires a version}"
        shift 2
        ;;
      --with-browser)
        WITH_BROWSER=1
        shift
        ;;
      -h | --help)
        usage 0
        ;;
      *)
        echo "Unknown argument: $1" >&2
        usage 1
        ;;
    esac
  done
}

# --- suites (edit checks here) -------------------------------------------------

cmd_test() {
  run uv run --python "$PYTHON" pytest -q
}

cmd_quality() {
  run uv run --python "$PYTHON" ruff format --check packages tests examples
  run uv run --python "$PYTHON" ruff check packages tests examples
  run uv run --python "$PYTHON" pyright

  # Fresh dist avoids conflicting train wheels on local re-runs.
  rm -rf dist/*.whl dist/*.tar.gz
  mkdir -p dist
  local pyproject package
  for pyproject in packages/*/pyproject.toml; do
    package="$(basename "$(dirname "$pyproject")")"
    echo "Building $package"
    # Pin interpreter so maturin/native wheels match the smoke venv.
    UV_PYTHON="$PYTHON" uv build --package "$package"
  done

  rm -rf /tmp/hedron-smoke
  uv venv /tmp/hedron-smoke --python "$PYTHON"
  uv pip install --python /tmp/hedron-smoke dist/*.whl
  /tmp/hedron-smoke/bin/python - <<'PY'
from hedron_core import Page, RenderMode, Text, render

html = render(Page(Text("smoke"), title="Smoke"), mode=RenderMode.PAGE).html
assert html.startswith("<!DOCTYPE html>")
assert "smoke" in html

from hedron import Hedron
from hedron.build import load_build_manifest
from hedron_data import DataTable
from hedron_explorer import explorer_router
from hedron_sample_kit import __version__ as sample_kit_version

assert callable(load_build_manifest)
table = DataTable([{"id": "1", "name": "Ada"}])
assert "Ada" in render(table).html

app = Hedron(
    title="smoke",
    security="standard",
    explorer="off",
    session_secret="smoke-secret",
)

@app.page("/")
def home():
    return Page(Text("ok"), title="Ok")

assert explorer_router is not None
assert sample_kit_version

# Adapter wheels must import without requiring FastAPI in the smoke path.
import hedron_flask
import hedron_django
from hedron_core import SecurityPolicy

assert hedron_flask.HedronFlask is not None
assert hedron_django.HedronSecurityHeadersMiddleware is not None
assert "Content-Security-Policy" in SecurityPolicy.from_name("standard").response_headers()
print("ok: all workspace wheels install and import cleanly")
PY

  uv run --python "$PYTHON" python - <<'PY'
import ast
import tomllib
from pathlib import Path

forbidden = {"fastapi", "flask", "django", "starlette", "asgiref"}
project = tomllib.loads(Path("packages/hedron-core/pyproject.toml").read_text())["project"]
deps = " ".join(project.get("dependencies", [])).lower()
assert not any(name in deps for name in forbidden)
for path in Path("packages/hedron-core/src/hedron_core").rglob("*.py"):
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".", 1)[0] not in forbidden
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert node.module.split(".", 1)[0] not in forbidden
print("ok: hedron-core remains framework-neutral")
PY
  test ! -f package.json
  test ! -d node_modules
  echo "ok: no Node package tooling in repo"

  run uv run --python "$PYTHON" python scripts/sync_status_roadmap.py --check
  run uv run --python "$PYTHON" python scripts/generate_sim_demos.py --check
  run uv run --python "$PYTHON" python scripts/check_docs_train_ssot.py

  uv run --python "$PYTHON" python - <<'PY'
import re
from pathlib import Path

roots = [Path("docs"), Path("README.md"), Path("ROADMAP.md")]
missing = []
files = []
for root in roots:
    if root.is_file():
        files.append(root)
    else:
        files.extend(root.rglob("*.md"))
for path in files:
    if path.is_symlink():
        continue
    text = path.read_text(encoding="utf-8")
    # Ignore fenced code so Python generics like TemplateSpec[T]( do not
    # look like markdown links.
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    for match in re.finditer(r"\]\(([^)#\n]+)(?:#[^)]*)?\)", text):
        target = match.group(1).strip()
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            missing.append(f"{path}: {target}")
if missing:
    raise SystemExit("\n".join(missing[:50]))
print("ok: relative doc links resolve")
PY

  run uv run --python "$PYTHON" --group docs mkdocs build --strict
}

cmd_browser() {
  export HEDRON_BROWSER="${HEDRON_BROWSER:-1}"
  export HEDRON_BROWSER_ENGINE="${HEDRON_BROWSER_ENGINE:-chromium}"
  run uv run --python "$PYTHON" pytest -q -m browser --tb=short
}

cmd_evidence() {
  run uv run --python "$PYTHON" python scripts/build_evidence_bundle.py
  run uv run --python "$PYTHON" --with pip-audit python scripts/dep_audit.py
  run uv run --python "$PYTHON" python scripts/check_release_gate.py "$GATE_VERSION"
  run uv run --python "$PYTHON" python scripts/check_hed_codes.py
  run uv run --python "$PYTHON" python scripts/verify_pkg_20.py
}

cmd_packaging() {
  # PKG packaging rehearsal (same verify helper as the evidence suite).
  run uv run --python "$PYTHON" python scripts/verify_pkg_20.py
}

cmd_all() {
  cmd_test
  cmd_quality
  cmd_evidence
  cmd_packaging
  if [[ "$WITH_BROWSER" -eq 1 ]]; then
    cmd_browser
  else
    echo "skip: browser (pass --with-browser to include)"
  fi
}

# --- dispatch ------------------------------------------------------------------

if [[ $# -lt 1 ]]; then
  usage 1
fi

SUITE="$1"
shift
parse_args "$@"

case "$SUITE" in
  test) cmd_test ;;
  quality) cmd_quality ;;
  browser) cmd_browser ;;
  evidence) cmd_evidence ;;
  packaging) cmd_packaging ;;
  all) cmd_all ;;
  -h | --help) usage 0 ;;
  *)
    echo "Unknown suite: $SUITE" >&2
    usage 1
    ;;
esac
