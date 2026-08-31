#!/usr/bin/env bash
# Shared CI check suites for commit CI and release CI.
#
# Workflows own checkout / uv / toolchain / sync / Playwright browser install.
# This script owns the actual check commands so there is one place to edit them.
#
# Usage:
#   scripts/ci_checks.sh test [--python 3.12]
#   scripts/ci_checks.sh workbench [--python 3.12]
#   scripts/ci_checks.sh docs [--python 3.12]
#   scripts/ci_checks.sh typing [--python 3.12]
#   scripts/ci_checks.sh quality [--python 3.12] [--skip-wheels]
#   scripts/ci_checks.sh browser [--python 3.12]
#   scripts/ci_checks.sh evidence [--python 3.12] [--gate-version 0.37.0]
#   scripts/ci_checks.sh realwb [--python 3.12]
#   scripts/ci_checks.sh realconnect [--python 3.12]
#   scripts/ci_checks.sh packaging [--python 3.12]
#   scripts/ci_checks.sh all [--python 3.12] [--gate-version 0.37.0] [options]
#
# Full local CI (`all`) mirrors `.github/workflows/ci.yml` job order:
#   test (Python 3.10–3.14 by default) → stable dependency bounds → quality →
#   browser (Chromium; pass --all-browsers for main-branch matrix) → realwb →
#   realconnect → evidence → packaging
#
# Independent checks inside a suite run concurrently (ruff / pyright / strict package types / docs;
# workbench bounds; evidence bundle vs verifiers). Wheel smoke and verify-pkgs
# stay sequential after those jobs so `uv build` / `uv run` cannot race the
# project .venv. Suite order in `all` stays sequential for the same reason.
#
# `all` options (opt out of slow or credential-gated jobs):
#   --python 3.12       Single Python for test (default matrix: 3.10–3.14)
#   --all-pythons       Force full test matrix even after --python
#   --jobs N            Max concurrent jobs (default: CPUs, or HEDRON_CHECK_JOBS)
#   --skip-browser      Skip Playwright HTMX suite
#   --skip-workbench    Skip stable dependency bounds matrix
#   --skip-realwb       Skip REALWB-030 Docker smoke
#   --skip-realconnect  Skip REALCONNECT-033 Docker smoke
#   --skip-wheels       Skip `uv build --all-packages` wheel smoke (`quality` only)
#   --all-browsers      Run Chromium + Firefox + WebKit (main / release CI)
#   --release-gate      Treat skipped browser/adapter/backend gates as failures
#   --with-browser      Deprecated alias (browser runs by default in `all`)
#
# Env:
#   HEDRON_BROWSER / HEDRON_BROWSER_ENGINE — browser suite (default engine: chromium)
#   HEDRON_BROWSER_REUSE — optional shared Playwright process for local runs
#   HEDRON_GATE_VERSION — default for --gate-version
#   HEDRON_CHECK_JOBS — default concurrency for --jobs
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

export UV_NO_PROGRESS="${UV_NO_PROGRESS:-1}"
# Keep wheel/sdist metadata and native linker identities stable across clean
# packaging rehearsals. ZIP/DOS timestamps cannot represent dates before 1980;
# clamp the historical Unix-epoch default so Python 3.14's zipfile remains
# portable across time zones while preserving deterministic artifacts.
SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-315619200}"
if [[ "$SOURCE_DATE_EPOCH" -lt 315619200 ]]; then
  SOURCE_DATE_EPOCH=315619200
fi
export SOURCE_DATE_EPOCH
# Do not let interpreter startup create package-local bytecode that can be
# picked up by native wheel builds and make otherwise identical artifacts
# differ based on build order.
export PYTHONDONTWRITEBYTECODE="${PYTHONDONTWRITEBYTECODE:-1}"

PYTHON="${PYTHON:-3.12}"
GATE_VERSION="${HEDRON_GATE_VERSION:-}"
if [[ -z "$GATE_VERSION" ]]; then
  GATE_VERSION="$(awk -F'"' '/^version = "/ { print $2; exit }' pyproject.toml)"
fi
CI_PYTHONS=(3.10 3.11 3.12 3.13 3.14)
PYTHON_EXPLICIT=0
ALL_PYTHONS=0
ALL_BROWSERS=0
SKIP_BROWSER=0
SKIP_WORKBENCH=0
SKIP_REALWB=0
SKIP_REALCONNECT=0
SKIP_WHEELS=0
RELEASE_GATE=0
UNSUPPORTED_GATES=()
JOBS="${HEDRON_CHECK_JOBS:-}"
HEDRON_PYTHON_EXE=""

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

default_jobs() {
  local n
  n="$(getconf _NPROCESSORS_ONLN 2>/dev/null || true)"
  if [[ -z "$n" || "$n" -lt 1 ]]; then
    n="$(sysctl -n hw.ncpu 2>/dev/null || true)"
  fi
  if [[ -z "$n" || "$n" -lt 1 ]]; then
    n=4
  fi
  printf '%s\n' "$n"
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
      --jobs)
        JOBS="${2:?--jobs requires a positive integer}"
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
      --skip-wheels)
        SKIP_WHEELS=1
        shift
        ;;
      --release-gate)
        RELEASE_GATE=1
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

record_unsupported() {
  UNSUPPORTED_GATES+=("$1")
  echo "unsupported evidence: $1"
}

report_unsupported() {
  if [[ "${#UNSUPPORTED_GATES[@]}" -eq 0 ]]; then
    return 0
  fi
  echo
  echo "Unsupported evidence gates:"
  local gate
  for gate in "${UNSUPPORTED_GATES[@]}"; do
    echo "- $gate"
  done
  if [[ "$RELEASE_GATE" -eq 1 ]]; then
    echo "release gate failed: required evidence was skipped" >&2
    return 1
  fi
  return 0
}

resolve_python() {
  if [[ -n "$HEDRON_PYTHON_EXE" ]]; then
    return 0
  fi
  local venv_py=".venv/bin/python" ver
  if [[ -x "$venv_py" ]]; then
    ver="$("$venv_py" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
    if [[ "$ver" == "$PYTHON" ]]; then
      HEDRON_PYTHON_EXE="$("$venv_py" -c 'import sys; print(sys.executable)')"
      return 0
    fi
  fi
  HEDRON_PYTHON_EXE="$(uv run --python "$PYTHON" python -c 'import sys; print(sys.executable)')"
}

secret_available() {
  # Match the live probes' non-exporting .env lookup without sourcing secrets
  # into this shell or printing their values.
  local name="$1"
  if [[ -n "${!name:-}" ]]; then
    return 0
  fi
  if [[ ! -f "$ROOT/.env" ]]; then
    return 1
  fi
  resolve_python
  HEDRON_SECRET_NAME="$name" "$HEDRON_PYTHON_EXE" - "$ROOT/.env" <<'PY'
import os
import shlex
import sys

name = os.environ["HEDRON_SECRET_NAME"]
prefix = f"{name}="
for raw in open(sys.argv[1], encoding="utf-8"):
    line = raw.strip()
    if line.startswith("export "):
        line = line[7:].lstrip()
    if not line.startswith(prefix):
        continue
    parsed = shlex.split(line.split("=", 1)[1].strip(), comments=True, posix=True)
    raise SystemExit(0 if len(parsed) == 1 and parsed[0] else 1)
raise SystemExit(1)
PY
}

run_py() {
  resolve_python
  run "$HEDRON_PYTHON_EXE" "$@"
}

run_uv() {
  run uv run --python "$PYTHON" "$@"
}

run_venv_tool() {
  resolve_python
  local tool="$1" bin
  shift
  bin="$(dirname "$HEDRON_PYTHON_EXE")"
  if [[ -x "$bin/$tool" ]]; then
    run "$bin/$tool" "$@"
  else
    run_uv "$tool" "$@"
  fi
}

# --- parallel job pool (bash 3.2-compatible) ----------------------------------

_job_dir=""
_job_names=()
_job_pids=()

job_pool_init() {
  if [[ -n "$_job_dir" && -d "$_job_dir" ]]; then
    rm -rf "$_job_dir"
  fi
  _job_dir="$(mktemp -d "${TMPDIR:-/tmp}/hedron-ci.XXXXXX")"
  _job_names=()
  _job_pids=()
}

job_pool_cleanup() {
  if [[ -n "$_job_dir" && -d "$_job_dir" ]]; then
    rm -rf "$_job_dir"
  fi
  _job_dir=""
  _job_names=()
  _job_pids=()
}

_running_job_count() {
  local pid count=0
  for pid in "${_job_pids[@]+"${_job_pids[@]}"}"; do
    if kill -0 "$pid" 2>/dev/null; then
      count=$((count + 1))
    fi
  done
  printf '%s\n' "$count"
}

start_job() {
  local name="$1"
  shift
  if [[ -z "$_job_dir" ]]; then
    job_pool_init
  fi
  while [[ "$(_running_job_count)" -ge "$JOBS" ]]; do
    sleep 0.25
  done
  log "[$name] $*"
  (
    set +e
    (
      set -euo pipefail
      "$@"
    ) >"$_job_dir/$name.out" 2>&1
    echo $? >"$_job_dir/$name.rc"
  ) &
  _job_pids+=("$!")
  _job_names+=("$name")
}

wait_jobs() {
  local i pid name rc remaining anyfail=0
  local -a done_flags
  if [[ ${#_job_pids[@]} -eq 0 ]]; then
    return 0
  fi
  for i in "${!_job_pids[@]}"; do
    done_flags[$i]=0
  done
  while true; do
    remaining=0
    for i in "${!_job_pids[@]}"; do
      if [[ "${done_flags[$i]}" -eq 1 ]]; then
        continue
      fi
      pid="${_job_pids[$i]}"
      if kill -0 "$pid" 2>/dev/null; then
        remaining=1
        continue
      fi
      wait "$pid" || true
      name="${_job_names[$i]}"
      rc="$(cat "$_job_dir/$name.rc" 2>/dev/null || echo 1)"
      printf '\n======== %s (exit %s) ========\n' "$name" "$rc"
      cat "$_job_dir/$name.out"
      if [[ "$rc" != "0" ]]; then
        anyfail=1
      fi
      done_flags[$i]=1
    done
    if [[ "$remaining" -eq 0 ]]; then
      break
    fi
    sleep 0.2
  done
  _job_names=()
  _job_pids=()
  if [[ "$anyfail" -ne 0 ]]; then
    return 1
  fi
  return 0
}

# --- suites (edit checks here) -------------------------------------------------

cmd_test() {
  # Treat unknown markers and invalid pytest configuration as CI failures.
  # Parallel workers come from pyproject addopts (`-n auto --dist=loadfile`).
  run_uv pytest -q --strict-config --strict-markers
}

quality_ruff() {
  run_venv_tool ruff format --check packages tests examples
  run_venv_tool ruff check packages tests examples
}

quality_pyright() {
  # Always `uv run` so pyright uses the same interpreter as the rest of CI.
  # Bare `$venv/bin/pyright` follows `[tool.pyright] venv` / auto-detected `.venv`,
  # which can disagree with UV_PROJECT_ENVIRONMENT.
  run_uv pyright
}

quality_strict_package_types() {
  # Every shipped Python package must remain warning-free under the workspace's
  # strict Pyright configuration. Keep paths explicit for reviewability, and
  # verify the list stays in sync with the uv workspace before running Pyright.
  run_py scripts/check_package_typing_inventory.py
  if rg -n '# pyright:.*reportUnknown[A-Za-z]*Type=false' packages --glob '*.py'; then
    echo "Package-wide unknown-type suppressions are forbidden; type or cast the boundary instead." >&2
    return 1
  fi
  run_uv pyright --warnings \
    packages/hedron-core/src/hedron_core \
    packages/hedron/src/hedron \
    packages/hedron-data/src/hedron_data \
    packages/hedron-charts/src/hedron_charts \
    packages/hedron-maps/src/hedron_maps \
    packages/edron/src/edron \
    packages/hedron-explorer/src/hedron_explorer \
    packages/hedron-sample-kit/src/hedron_sample_kit \
    packages/hedron-flask/src/hedron_flask \
    packages/hedron-django/src/hedron_django \
    packages/hedron-jinja/src/hedron_jinja \
    packages/hedron-conformance/src/hedron_conformance \
    packages/hedron-native/src/hedron_native \
    packages/hedron-extras/src/hedron_extras \
    packages/hedron-notebook/src/hedron_notebook \
    packages/hedron-mcp/src/hedron_mcp \
    packages/hedron-gradio/src/hedron_gradio \
    packages/hedron-sim/src/hedron_sim \
    packages/hedron-posit/src/hedron_posit \
    packages/hedron-elements/src/hedron_elements \
    packages/edron-sim/src/edron_sim \
    packages/fastapi-workbench/src/fastapi_workbench
}

quality_wheels_smoke() {
  # Fresh dist avoids conflicting train wheels on local re-runs.
  # Wheel-only: the smoke venv installs `dist/*.whl`; sdists are unused.
  rm -rf dist/*.whl dist/*.tar.gz
  mkdir -p dist
  run env UV_NO_SYNC=1 UV_PYTHON="$PYTHON" uv build --all-packages --wheel --out-dir dist

  rm -rf /tmp/hedron-smoke
  uv venv /tmp/hedron-smoke --python "$PYTHON"
  # Edron releases independently, so install its wheel after the rest of the
  # prospective workspace train. This validates the dependency graph that the
  # tag is about to publish without depending on older PyPI satellite metadata.
  local train_wheels=()
  local wheel
  for wheel in dist/*.whl; do
    if [[ "$(basename "$wheel")" != edron-*.whl && "$(basename "$wheel")" != edron_sim-*.whl ]]; then
      train_wheels+=("$wheel")
    fi
  done
  uv pip install --python /tmp/hedron-smoke "${train_wheels[@]}"
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
import hedron_posit
from hedron_core import SecurityPolicy

assert hedron_flask.HedronFlask is not None
assert hedron_django.HedronSecurityHeadersMiddleware is not None
assert hedron_posit.workbenchify is not None
assert issubclass(hedron_posit.HedronPosit, Hedron)
assert "Content-Security-Policy" in SecurityPolicy.from_name("standard").response_headers()
print("ok: prospective Hedron workspace wheels install and import cleanly")
PY

  local edron_wheel=(dist/edron-*.whl)
  if [[ ! -f "${edron_wheel[0]}" || "${edron_wheel[0]}" == 'dist/edron-*.whl' ]]; then
    echo "missing Edron wheel for stable-train smoke" >&2
    return 1
  fi
  uv pip install --python /tmp/hedron-smoke/bin/python "${edron_wheel[0]}"
  local edron_sim_wheel=(dist/edron_sim-*.whl)
  if [[ ! -f "${edron_sim_wheel[0]}" || "${edron_sim_wheel[0]}" == 'dist/edron_sim-*.whl' ]]; then
    echo "missing Edron Sim wheel for stable-train smoke" >&2
    return 1
  fi
  uv pip install --python /tmp/hedron-smoke/bin/python "${edron_sim_wheel[0]}"
  /tmp/hedron-smoke/bin/python - <<'PY'
import importlib.metadata as metadata
import tomllib
from pathlib import Path

workspace_version = tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]
assert metadata.version("edron") == workspace_version
assert metadata.version("edron-sim") == "0.1.0"
assert metadata.version("hedron") == workspace_version
assert metadata.version("hedron-data") == workspace_version
print(f"ok: Edron {workspace_version} installs against the Hedron train")
PY

  # Exercise the exact standalone-wheel scaffold contract on ordinary main/PR
  # CI. Release CI repeats this against its independently built artifacts before
  # the first immutable upload.
  local workspace_version
  workspace_version="$($HEDRON_PYTHON_EXE -c \
    'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])')"
  run_py scripts/check_published_quickstart.py \
    "$workspace_version" --dist-dir dist --attempts 1
}

quality_core_neutral() {
  run_py - <<'PY'
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
  run_py scripts/check_satellite_imports.py
  run_py scripts/check_htmx_alpine_refinement.py
  run_py scripts/check_symbol_tiers.py
}

quality_release_contract() {
  run_py scripts/check_release_contract.py
}

quality_verify_pkgs() {
  # PR quality: tip train + two predecessors only. Older packets run on evidence.
  run_py scripts/verify_pkg_56.py
  run_py scripts/verify_pkg_57.py
  run_py scripts/verify_pkg_58.py
  run_py scripts/verify_pkg_59.py
  run_py scripts/verify_pkg_60.py
  run_py scripts/verify_pkg_61.py
}

quality_docs() {
  # Sim --check copies JS/CSS assets; keep MkDocs after that so they cannot race.
  run_py scripts/sync_status_roadmap.py --check
  run_py scripts/generate_sim_demos.py --check
  run_py scripts/generate_component_docs.py --check
  run_py scripts/generate_htmx_alpine_component_counts.py --check
  run_py scripts/generate_edron_api_index.py --check
  run_py scripts/generate_example_catalog.py --check
  run_py scripts/check_docs_train_ssot.py
  run_py scripts/check_package_docs_inventory.py
  run_py scripts/check_documentation_ownership.py
  run_py scripts/check_api_docs_coverage.py
  run_py scripts/check_edron_docs.py
  run_py scripts/check_package_readme_links.py
  run_py scripts/check_public_doc_links.py
  run_py scripts/check_changelog_structure.py
  run_py scripts/check_recipe_code_sync.py
  run_py scripts/check_docs_file_tabs.py
  run_py scripts/check_docs_examples.py
  run_py - <<'PY'
import re
from pathlib import Path

roots = [Path("docs"), Path("README.md")]
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
  if [[ -x "$(dirname "$HEDRON_PYTHON_EXE")/mkdocs" ]]; then
    run "$(dirname "$HEDRON_PYTHON_EXE")/mkdocs" build --strict
  else
    run uv run --python "$PYTHON" --group docs mkdocs build --strict
  fi
}

cmd_docs() {
  resolve_python
  quality_docs
}

cmd_typing() {
  resolve_python
  quality_strict_package_types
}

cmd_quality() {
  job_pool_init
  resolve_python
  # Keep `.venv` mutations off this pool: `uv run` without a pinned interpreter
  # (verify_pkg_*.py) and `uv build` can recreate the project venv and race
  # with pyright / docs.
  start_job ruff quality_ruff
  start_job pyright quality_pyright
  start_job strict-package-types quality_strict_package_types
  start_job core-neutral quality_core_neutral
  start_job release-contract quality_release_contract
  start_job docs quality_docs
  wait_jobs
  printf '\n======== verify-pkgs ========\n'
  quality_verify_pkgs
  if [[ "$SKIP_WHEELS" -eq 0 ]]; then
    quality_wheels_smoke
  else
    echo "skip: quality_wheels_smoke (--skip-wheels)"
  fi
}

cmd_browser() {
  export HEDRON_BROWSER="${HEDRON_BROWSER:-1}"
  export HEDRON_BROWSER_ENGINE="${HEDRON_BROWSER_ENGINE:-chromium}"
  # Keep Playwright serial: xdist contention on browser processes flakes.
  run_uv pytest -q -m browser --tb=short -n 0
}

cmd_workbench_bounds() {
  # Matches ci.yml dependency-bounds (minimum + latest Starlette/Uvicorn bounds).
  local bounds="$1"
  local venv=".bounds-venv-${bounds}"
  echo "== workbench dependencies ($bounds) =="
  uv venv "$venv" --python "$PYTHON" --clear
  if [[ "$bounds" == minimum ]]; then
    uv pip install --python "$venv/bin/python" --resolution lowest-direct \
      -e packages/hedron-core -e packages/hedron -e packages/hedron-explorer \
      -e packages/hedron-data -e packages/hedron-flask -e packages/hedron-django \
      -e packages/hedron-jinja -e packages/hedron-conformance -e packages/hedron-extras \
      -e packages/hedron-elements -e packages/hedron-posit -e packages/fastapi-workbench \
      -e packages/hedron-charts -e packages/hedron-maps -e packages/edron \
      -r release/stable-dependencies.txt \
      "pytest>=8.3" "pytest-xdist>=3.6" "httpx>=0.28" \
      "django>=5.2,<6" "matplotlib>=3.8,<4"
  else
    uv pip install --python "$venv/bin/python" --resolution highest \
      -e packages/hedron-core -e packages/hedron -e packages/hedron-explorer \
      -e packages/hedron-data -e packages/hedron-flask -e packages/hedron-django \
      -e packages/hedron-jinja -e packages/hedron-conformance -e packages/hedron-extras \
      -e packages/hedron-elements -e packages/hedron-posit -e packages/fastapi-workbench \
      -e packages/hedron-charts -e packages/hedron-maps -e packages/edron \
      -r release/stable-dependencies.txt \
      "pytest>=8.3" "pytest-xdist>=3.6" "httpx>=0.28" \
      "django>=5.2,<6" "matplotlib>=3.8,<4"
  fi
  run "$venv/bin/python" scripts/check_stable_dependency_bounds.py --verify-installed "$bounds"
  run "$venv/bin/pytest" -q \
    tests/adapters/workbench \
    tests/adapters/flask \
    tests/adapters/django \
    tests/integration/test_workbench_urls.py \
    tests/integration/test_workbench_runner.py \
    tests/security/test_workbench_adversarial.py \
    tests/unit/test_maps_047_pkg.py \
    tests/unit/test_charts_028_static_matrix.py \
    tests/unit/test_edron_100_packet.py
}

cmd_workbench() {
  job_pool_init
  start_job workbench-minimum cmd_workbench_bounds minimum
  start_job workbench-latest cmd_workbench_bounds latest
  wait_jobs
}

evidence_bundle() {
  run_py scripts/build_evidence_bundle.py
}

evidence_audit() {
  run uv run --python "$PYTHON" --with pip-audit python scripts/dep_audit.py
}

evidence_gates() {
  # Living tip capability gates are Verified for the configured train.
  run_py scripts/check_release_gate.py "$GATE_VERSION"
  run_py scripts/check_human_at_packet.py
  run_py scripts/check_hed_codes.py
}

evidence_verify_pkgs() {
  if [[ "$GATE_VERSION" == 1.0.* ]]; then
    # 1.0 has a consolidated release packet; predecessor verifiers encode
    # their historical package versions and are covered by their own release
    # workflows rather than the current 1.0 evidence job.
    run_py scripts/check_100.py --check-plan
    return 0
  fi
  run_py scripts/verify_pkg_34.py --allow-planned
  run_py scripts/verify_pkg_35.py --allow-planned
  # `all` already ran 36–47 during quality; skip the second verification pass.
  if [[ "${HEDRON_CI_ALL:-0}" == 1 ]]; then
    echo "skip: verify_pkg_36–49 (already covered by quality)"
    return 0
  fi
  run_py scripts/verify_pkg_36.py --allow-planned
  run_py scripts/verify_pkg_37.py --allow-planned
  run_py scripts/verify_pkg_38.py --allow-planned
  run_py scripts/verify_pkg_39.py --allow-planned
  run_py scripts/verify_pkg_40.py --allow-planned
  run_py scripts/verify_pkg_41.py
  run_py scripts/verify_pkg_42.py
  run_py scripts/verify_pkg_43.py
  run_py scripts/verify_pkg_44.py
  run_py scripts/verify_pkg_45.py
  run_py scripts/verify_pkg_46.py
  run_py scripts/verify_pkg_47.py
  run_py scripts/verify_pkg_48.py
  run_py scripts/verify_pkg_49.py
  run_py scripts/verify_pkg_50.py
  run_py scripts/verify_pkg_51.py
  run_py scripts/verify_pkg_52.py
  run_py scripts/verify_pkg_53.py
  run_py scripts/verify_pkg_54.py
  run_py scripts/verify_pkg_55.py
  run_py scripts/verify_pkg_56.py
  run_py scripts/verify_pkg_57.py
  run_py scripts/verify_pkg_58.py
  run_py scripts/verify_pkg_59.py
  run_py scripts/verify_pkg_60.py
  run_py scripts/verify_pkg_61.py
}

cmd_evidence() {
  job_pool_init
  resolve_python
  start_job evidence-bundle evidence_bundle
  start_job dep-audit evidence_audit
  start_job evidence-gates evidence_gates
  start_job evidence-verify evidence_verify_pkgs
  wait_jobs
}

cmd_realconnect() {
  # Live Posit Connect Docker smoke (REALCONNECT-033). Requires Docker and CONNECT_LICENSE.
  # Skips successfully when CONNECT_LICENSE is unavailable (see check_realconnect_033.py).
  run_py scripts/check_realconnect_033.py --live
}

cmd_realwb() {
  # Live Posit Workbench Docker smoke (REALWB-030). Requires Docker and PWB_LICENSE.
  # Skips successfully when PWB_LICENSE is unavailable (see check_realwb_smoke.py).
  run_py scripts/check_realwb_smoke.py --live
}

cmd_packaging() {
  # PKG packaging rehearsal (same verify helper as the evidence suite).
  if [[ "$GATE_VERSION" == 1.0.* ]]; then
    run_py scripts/check_100.py --gate PKG-100 --verify
    return 0
  fi
  if [[ "${HEDRON_CI_ALL:-0}" == 1 ]]; then
    echo "skip: packaging (verify_pkg_35–49 already covered by quality + evidence)"
    return 0
  fi
  resolve_python
  run_py scripts/verify_pkg_35.py --allow-planned
  run_py scripts/verify_pkg_36.py --allow-planned
  run_py scripts/verify_pkg_37.py --allow-planned
  run_py scripts/verify_pkg_38.py --allow-planned
  run_py scripts/verify_pkg_39.py --allow-planned
  run_py scripts/verify_pkg_40.py --allow-planned
  run_py scripts/verify_pkg_41.py
  run_py scripts/verify_pkg_42.py
  run_py scripts/verify_pkg_43.py
  run_py scripts/verify_pkg_44.py
  run_py scripts/verify_pkg_45.py
  run_py scripts/verify_pkg_46.py
  run_py scripts/verify_pkg_47.py
  run_py scripts/verify_pkg_48.py
  run_py scripts/verify_pkg_49.py
  run_py scripts/verify_pkg_50.py
  run_py scripts/verify_pkg_51.py
  run_py scripts/verify_pkg_52.py
  run_py scripts/verify_pkg_53.py
  run_py scripts/verify_pkg_54.py
  run_py scripts/verify_pkg_55.py
  run_py scripts/verify_pkg_56.py
  run_py scripts/verify_pkg_57.py
  run_py scripts/verify_pkg_58.py
}

cmd_all() {
  local py browser saved_python="$PYTHON"
  local -a browsers

  HEDRON_CI_ALL=1
  export HEDRON_CI_ALL
  if [[ "$RELEASE_GATE" -eq 1 ]]; then
    HEDRON_REQUIRED_LIVE_GATES=1
    export HEDRON_REQUIRED_LIVE_GATES
  fi

  if [[ "$ALL_PYTHONS" -eq 0 && "$PYTHON_EXPLICIT" -eq 0 ]]; then
    ALL_PYTHONS=1
  fi

  section "CI full check (mirrors .github/workflows/ci.yml)"
  cat <<NOTE
Prerequisites (same as GitHub Actions setup steps):
  uv sync --locked --all-groups --python 3.12
  uv sync --locked --python 3.12 --group docs
  Rust, Java 17, Node 20, Playwright — see script header
Concurrency: ${JOBS} jobs (--jobs / HEDRON_CHECK_JOBS)
NOTE

  if [[ "$ALL_PYTHONS" -eq 1 ]]; then
    for py in "${CI_PYTHONS[@]}"; do
      section "test (Python $py)"
      PYTHON="$py"
      HEDRON_PYTHON_EXE=""
      cmd_test
    done
  else
    section "test (Python $PYTHON)"
    cmd_test
  fi

  if [[ "$PYTHON_EXPLICIT" -eq 0 ]]; then
    PYTHON="3.12"
    HEDRON_PYTHON_EXE=""
  else
    PYTHON="$saved_python"
  fi

  if [[ "$SKIP_WORKBENCH" -eq 0 ]]; then
    section "workbench-dependencies"
    cmd_workbench
  else
    record_unsupported "workbench dependency/adaptor matrix (--skip-workbench)"
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
    if [[ "$ALL_BROWSERS" -eq 0 ]]; then
      record_unsupported "Firefox/WebKit browser matrix (--all-browsers not set)"
    fi
  else
    record_unsupported "browser matrix (--skip-browser)"
  fi

  if [[ "$SKIP_REALWB" -eq 0 ]]; then
    section "realwb"
    if ! secret_available PWB_LICENSE; then
      record_unsupported "REALWB-030 live backend (PWB_LICENSE unavailable)"
    fi
    cmd_realwb
  else
    record_unsupported "REALWB-030 live backend (--skip-realwb)"
  fi

  if [[ "$SKIP_REALCONNECT" -eq 0 ]]; then
    section "realconnect"
    if ! secret_available CONNECT_LICENSE && ! secret_available CONNECT_API_KEY; then
      record_unsupported "REALCONNECT-033 live backend (CONNECT_LICENSE unavailable)"
    fi
    cmd_realconnect
  else
    record_unsupported "REALCONNECT-033 live backend (--skip-realconnect)"
  fi

  section "evidence"
  cmd_evidence

  section "packaging"
  cmd_packaging
  report_unsupported
}

# --- dispatch ------------------------------------------------------------------

if [[ $# -lt 1 ]]; then
  usage 1
fi

SUITE="$1"
shift
parse_args "$@"

# Pin child `uv run` (verify_pkg_*.py pytest) to this interpreter so they cannot
# recreate `.venv` with another CPython while pyright is using it.
export UV_PYTHON="${UV_PYTHON:-$PYTHON}"

if [[ -z "$JOBS" ]]; then
  JOBS="$(default_jobs)"
fi
if [[ "$JOBS" -lt 1 ]]; then
  echo "--jobs must be a positive integer" >&2
  exit 1
fi

trap job_pool_cleanup EXIT

case "$SUITE" in
  test) cmd_test ;;
  workbench) cmd_workbench ;;
  docs) cmd_docs ;;
  typing) cmd_typing ;;
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
