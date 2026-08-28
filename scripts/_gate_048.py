"""Shared constants and contract helpers for the phase 0.48 gate."""

from __future__ import annotations

from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.48.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "htmx-capability-inventory-048.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_48.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-048.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "HTMX_EXTENSION_INTEGRATION_048.md"
API = ROOT / "docs" / "api" / "HTMX_EXTENSIONS.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0075-HTMX-EXTENSION-INTEGRATION.md"
CATALOG = ROOT / "docs" / "acceptance" / "htmx-extension-catalog-048.toml"
ASSETS = ROOT / "docs" / "acceptance" / "htmx-asset-activation-048.toml"
SSE_HEAD_PRELOAD = ROOT / "docs" / "acceptance" / "htmx-sse-head-preload-048.toml"
MORPH_COMPAT = ROOT / "docs" / "acceptance" / "htmx-morph-compat-048.toml"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

TRACKING_ISSUE = "#373"

PACKET_FILES = (
    GATE,
    INVENTORY,
    PACKET,
    UPGRADE,
    IMPLEMENTATION,
    API,
    RFC,
    CATALOG,
    ASSETS,
    SSE_HEAD_PRELOAD,
    MORPH_COMPAT,
)

EXPECTED_GATES = (
    "EXTENSION-048",
    "ASSET-048",
    "SSE-048",
    "HEAD-048",
    "PRELOAD-048",
    "MORPH-048",
    "SECURITY-048",
    "A11Y-048",
    "BROWSER-048",
    "PERF-048",
    "ADAPTER-048",
    "TOOLING-048",
    "COMPAT-048",
    "DOCS-048",
    "REGRESS-048",
    "PKG-048",
)
EXPECTED_REQUIREMENT_RANGES = (
    "EXT-CAT-001..010",
    "EXT-ASSET-001..012",
    "EXT-SSE-001..012",
    "EXT-HEAD-001..010",
    "EXT-PRELOAD-001..010",
    "EXT-MORPH-001..008",
    "EXT-EXCLUDE-001..010",
)
EXCLUDED_REQUIREMENT_IDS = frozenset({"EXT-MORPH-001..008", "EXT-EXCLUDE-001..010"})

FROZEN_CONTRACT_MARKERS = (
    "HtmxExtension",
    "ExtensionSet",
    "Page.htmx_extensions",
    "SseRegion",
    "SseTrigger",
    "htmx-ext-sse",
)


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-080 | Accepted |" in decisions


def contract_refine_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-083 | Accepted |" in decisions and all(
        marker in combined for marker in FROZEN_CONTRACT_MARKERS
    )


def require_files(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_file():
            errors.append(f"missing required file: {path}")


def gate_state(gate_id: str) -> str | None:
    data = tomllib.loads(GATE.read_text(encoding="utf-8"))
    for row in data.get("evidence") or []:
        if row.get("id") == gate_id:
            return str(row.get("state", "")).strip()
    return None


GATE_TESTS: dict[str, list[str]] = {
    "EXTENSION-048": ["tests/unit/test_htmx_048_spec.py"],
    "ASSET-048": ["tests/unit/test_htmx_048_assets.py"],
    "SSE-048": ["tests/unit/test_htmx_048_sse.py"],
    "HEAD-048": ["tests/unit/test_htmx_048_head.py"],
    "PRELOAD-048": ["tests/unit/test_htmx_048_preload.py"],
    "MORPH-048": ["tests/unit/test_htmx_048_morph.py"],
    "SECURITY-048": ["tests/unit/test_htmx_048_security.py"],
    "A11Y-048": ["tests/browser/test_htmx_048_a11y.py"],
    "BROWSER-048": ["tests/browser/test_htmx_048_browser.py"],
    "PERF-048": ["tests/unit/test_htmx_048_perf.py"],
    "ADAPTER-048": ["tests/unit/test_htmx_048_adapter.py"],
    "TOOLING-048": ["tests/unit/test_htmx_048_tooling.py"],
    "COMPAT-048": ["tests/unit/test_htmx_048_compat.py"],
    "DOCS-048": ["tests/unit/test_htmx_048_docs.py"],
    "REGRESS-048": ["tests/unit/test_htmx_048_compat.py"],
    "PKG-048": ["tests/unit/test_htmx_048_pkg.py"],
}


def run_pytest(paths: list[str]) -> int:
    import subprocess
    import sys

    command = [sys.executable, "-m", "pytest", "-q", "--tb=short", *paths]
    print("+", *command, flush=True)
    return subprocess.call(command, cwd=ROOT)


def check_gate(gate_id: str) -> int:
    errors: list[str] = []
    require_files(list(PACKET_FILES), errors)
    if not accepted_contract_present():
        errors.append("RFC-0075 and D-080 must remain Accepted")
    if not contract_refine_present():
        errors.append("D-083 and the frozen 0.48 contract markers must remain present")
    packet = PACKET.read_text(encoding="utf-8")
    if TRACKING_ISSUE not in packet:
        errors.append(f"{PACKET}: tracking issue {TRACKING_ISSUE} must be bound")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.48.toml")
    elif state not in {"Planned", "Implemented", "Verified", "Deferred", "Excluded"}:
        errors.append(f"{gate_id} unexpected state {state!r}")
    if gate_id == "MORPH-048" and state not in {"Verified", "Deferred", "Excluded", "Planned"}:
        errors.append(f"MORPH-048 must be Verified, Deferred, or Excluded; found {state!r}")
    tests = GATE_TESTS.get(gate_id, [])
    if state in {"Verified", "Deferred", "Excluded"} and not tests:
        errors.append(f"{gate_id} is {state} but has no executable evidence tests bound")
    if errors:
        for message in errors:
            print(f"{gate_id}: {message}", flush=True)
        return 1
    if tests:
        code = run_pytest(tests)
        if code:
            return code
    print(f"ok: {gate_id}")
    return 0
