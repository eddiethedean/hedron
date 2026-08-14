#!/usr/bin/env bash
# Shared CI check suites for commit CI and release CI.
#
# Workflows own checkout / uv / toolchain / sync / Playwright browser install.
# This script owns the actual check commands so there is one place to edit them.
#
# Usage:
#   scripts/ci_checks.sh test [--python 3.12]
#   scripts/ci_checks.sh workbench [--python 3.12]
#   scripts/ci_checks.sh quality [--python 3.12]
#   scripts/ci_checks.sh browser [--python 3.12]
#   scripts/ci_checks.sh evidence [--python 3.12] [--gate-version 0.37.0]
#   scripts/ci_checks.sh realwb [--python 3.12]
#   scripts/ci_checks.sh realconnect [--python 3.12]
#   scripts/ci_checks.sh packaging [--python 3.12]
#   scripts/ci_checks.sh all [--python 3.12] [--gate-version 0.37.0] [options]
#
# Full local CI (`all`) mirrors `.github/workflows/ci.yml` job order:
#   test (Python 3.11–3.14 by default) → workbench-dependencies → quality →
#   browser (Chromium; pass --all-browsers for main-branch matrix) → realwb →
#   realconnect → evidence → packaging
#
# `all` options (opt out of slow or credential-gated jobs):
#   --python 3.12       Single Python for test (default matrix: 3.11–3.14)
#   --all-pythons       Force full test matrix even after --python
#   --skip-browser      Skip Playwright HTMX suite
#   --skip-workbench    Skip Workbench dependency bounds matrix
#   --skip-realwb       Skip REALWB-030 Docker smoke
#   --skip-realconnect  Skip REALCONNECT-033 Docker smoke
#   --all-browsers      Run Chromium + Firefox + WebKit (main / release CI)
#   --with-browser      Deprecated alias (browser runs by default in `all`)
#
# Env:
#   HEDRON_BROWSER / HEDRON_BROWSER_ENGINE — browser suite (default engine: chromium)
#   HEDRON_GATE_VERSION — default for --gate-version
#   PWB_LICENSE / CONNECT_LICENSE — optional; realwb/realconnect skip when unset
#
# Prerequisites for `all` (match workflow setup steps):
#   uv sync --locked --all-groups --python 3.12
#   uv sync --locked --python 3.12 --group docs   # evidence / packaging
#   Rust toolchain — quality + evidence (hedron-native wheels)
#   Java 17 + Node 20 — evidence / packaging verify scripts
#   Playwright — browser job (see ci.yml browser install step)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-3.12}"
GATE_VERSION="${HEDRON_GATE_VERSION:-0.38.0}"
CI_PYTHONS=(3.11 3.12 3.13 3.14)
PYTHON_EXPLICIT=0
ALL_PYTHONS=0
ALL_BROWSERS=0
SKIP_BROWSER=0
SKIP_WORKBENCH=0
SKIP_REALWB=0
SKIP_REALCONNECT=0

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

section() {
  printf '\n======== %s ========\n' "$*"
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --python)
        PYTHON="${2:?--python requires a version}"
        PYTHON_EXPLICIT=1
        shift 2
        ;;
      --gate-version)
        GATE_VERSION="${2:?--gate-version requires a version}"
        shift 2
        ;;
      --all-pythons)
        ALL_PYTHONS=1
        shift
        ;;
      --all-browsers)
        ALL_BROWSERS=1
        shift
        ;;
      --skip-browser)
        SKIP_BROWSER=1
        shift
        ;;
      --skip-workbench)
        SKIP_WORKBENCH=1
        shift
        ;;
      --skip-realwb)
        SKIP_REALWB=1
        shift
        ;;
      --skip-realconnect)
        SKIP_REALCONNECT=1
        shift
        ;;
      --with-browser)
        SKIP_BROWSER=0
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
  # Treat unknown markers and invalid pytest configuration as CI failures.
  run uv run --python "$PYTHON" pytest -q --strict-config --strict-markers
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
import hedron_workbench
from hedron_core import SecurityPolicy

assert hedron_flask.HedronFlask is not None
assert hedron_django.HedronSecurityHeadersMiddleware is not None
assert hedron_workbench.workbenchify is not None
assert issubclass(hedron_workbench.HedronWorkbench, Hedron)
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
  run uv run --python "$PYTHON" python scripts/generate_component_docs.py --check
  run uv run --python "$PYTHON" python scripts/check_docs_train_ssot.py
  run uv run --python "$PYTHON" python scripts/check_package_docs_inventory.py
  run uv run --python "$PYTHON" python scripts/check_documentation_ownership.py
  run uv run --python "$PYTHON" python scripts/check_api_docs_coverage.py
  run uv run --python "$PYTHON" python scripts/check_package_readme_links.py
  run uv run --python "$PYTHON" python scripts/check_public_doc_links.py
  run uv run --python "$PYTHON" python scripts/check_changelog_structure.py
  run uv run --python "$PYTHON" python scripts/check_recipe_code_sync.py
  run uv run --python "$PYTHON" python scripts/verify_pkg_36.py --allow-planned
  run uv run --python "$PYTHON" python scripts/verify_pkg_37.py --allow-planned
  run uv run --python "$PYTHON" python scripts/verify_pkg_38.py

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

cmd_workbench() {
  # Matches ci.yml workbench-dependencies (minimum + latest Starlette/Uvicorn bounds).
  local bounds venv=".bounds-venv"
  for bounds in minimum latest; do
    echo "== workbench dependencies ($bounds) =="
    uv venv "$venv" --python "$PYTHON" --clear
    if [[ "$bounds" == minimum ]]; then
      uv pip install --python "$venv/bin/python" \
        -e packages/hedron-core -e packages/hedron -e packages/hedron-workbench \
        -e packages/hedron-django \
        pytest httpx "django>=5.2,<6" "starlette==1.3.1" "uvicorn==0.32.0"
    else
      uv pip install --python "$venv/bin/python" \
        -e packages/hedron-core -e packages/hedron -e packages/hedron-workbench \
        -e packages/hedron-django \
        pytest httpx "django>=5.2,<6" "starlette>=1.3.1" "uvicorn>=0.32"
    fi
    run "$venv/bin/pytest" -q \
      tests/adapters/workbench \
      tests/integration/test_workbench_urls.py \
      tests/integration/test_workbench_runner.py \
      tests/security/test_workbench_adversarial.py
  done
}

cmd_evidence() {
  run uv run --python "$PYTHON" python scripts/build_evidence_bundle.py
  run uv run --python "$PYTHON" --with pip-audit python scripts/dep_audit.py
  # Living tip capability gates are Verified for the configured train.
  run uv run --python "$PYTHON" python scripts/check_release_gate.py "$GATE_VERSION"
  run uv run --python "$PYTHON" python scripts/check_human_at_packet.py
  run uv run --python "$PYTHON" python scripts/check_hed_codes.py
  run uv run --python "$PYTHON" python scripts/verify_pkg_34.py --allow-planned
  run uv run --python "$PYTHON" python scripts/verify_pkg_35.py --allow-planned
  run uv run --python "$PYTHON" python scripts/verify_pkg_36.py --allow-planned
  run uv run --python "$PYTHON" python scripts/verify_pkg_37.py --allow-planned
  run uv run --python "$PYTHON" python scripts/verify_pkg_38.py
}

cmd_realconnect() {
  # Live Posit Connect Docker smoke (REALCONNECT-033). Requires Docker and CONNECT_LICENSE.
  # Skips successfully when CONNECT_LICENSE is unavailable (see check_realconnect_033.py).
  run uv run --python "$PYTHON" python scripts/check_realconnect_033.py --live
}

cmd_realwb() {
  # Live Posit Workbench Docker smoke (REALWB-030). Requires Docker and PWB_LICENSE.
  # Skips successfully when PWB_LICENSE is unavailable (see check_realwb_smoke.py).
  run uv run --python "$PYTHON" python scripts/check_realwb_smoke.py --live
}

cmd_packaging() {
  # PKG packaging rehearsal (same verify helper as the evidence suite).
  run uv run --python "$PYTHON" python scripts/verify_pkg_35.py --allow-planned
  run uv run --python "$PYTHON" python scripts/verify_pkg_36.py --allow-planned
  run uv run --python "$PYTHON" python scripts/verify_pkg_37.py --allow-planned
  run uv run --python "$PYTHON" python scripts/verify_pkg_38.py
}

cmd_all() {
  local py browser saved_python="$PYTHON"
  local -a browsers

  if [[ "$ALL_PYTHONS" -eq 0 && "$PYTHON_EXPLICIT" -eq 0 ]]; then
    ALL_PYTHONS=1
  fi

  section "CI full check (mirrors .github/workflows/ci.yml)"
  cat <<'NOTE'
Prerequisites (same as GitHub Actions setup steps):
  uv sync --locked --all-groups --python 3.12
  uv sync --locked --python 3.12 --group docs
  Rust, Java 17, Node 20, Playwright — see script header
NOTE

  if [[ "$ALL_PYTHONS" -eq 1 ]]; then
    for py in "${CI_PYTHONS[@]}"; do
      section "test (Python $py)"
      PYTHON="$py"
      cmd_test
    done
  else
    section "test (Python $PYTHON)"
    cmd_test
  fi

  if [[ "$PYTHON_EXPLICIT" -eq 0 ]]; then
    PYTHON="3.12"
  else
    PYTHON="$saved_python"
  fi

  if [[ "$SKIP_WORKBENCH" -eq 0 ]]; then
    section "workbench-dependencies"
    cmd_workbench
  else
    echo "skip: workbench (--skip-workbench)"
  fi

  section "quality"
  cmd_quality

  if [[ "$SKIP_BROWSER" -eq 0 ]]; then
    browsers=(chromium)
    if [[ "$ALL_BROWSERS" -eq 1 ]]; then
      browsers=(chromium firefox webkit)
    fi
    for browser in "${browsers[@]}"; do
      section "browser ($browser)"
      export HEDRON_BROWSER_ENGINE="$browser"
      cmd_browser
    done
  else
    echo "skip: browser (--skip-browser)"
  fi

  if [[ "$SKIP_REALWB" -eq 0 ]]; then
    section "realwb"
    cmd_realwb
  else
    echo "skip: realwb (--skip-realwb)"
  fi

  if [[ "$SKIP_REALCONNECT" -eq 0 ]]; then
    section "realconnect"
    cmd_realconnect
  else
    echo "skip: realconnect (--skip-realconnect)"
  fi

  section "evidence"
  cmd_evidence

  section "packaging"
  cmd_packaging
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
  workbench) cmd_workbench ;;
  quality) cmd_quality ;;
  browser) cmd_browser ;;
  evidence) cmd_evidence ;;
  realwb) cmd_realwb ;;
  realconnect) cmd_realconnect ;;
  packaging) cmd_packaging ;;
  all) cmd_all ;;
  -h | --help) usage 0 ;;
  *)
    echo "Unknown suite: $SUITE" >&2
    usage 1
    ;;
esac
