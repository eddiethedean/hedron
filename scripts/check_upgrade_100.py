#!/usr/bin/env python3
"""Run the canonical Phase 1.0 bridge fixture against an immutable baseline.

This is deliberately a bridge check, not a release verifier: it proves that
the canonical fixture remains usable on the frozen 0.67 source tree and on the
current checkout. A target v1.0 artifact must still be supplied separately.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "upgrade" / "phase_1_0" / "canonical"

_PROBE = r"""
import importlib.util
import json
from pathlib import Path
from fastapi.testclient import TestClient
from hedron_jinja.source import parse_hdj_source

fixture = Path("__FIXTURE__")
app_path = fixture / "app.py"
spec = importlib.util.spec_from_file_location("hedron_phase_1_bridge", app_path)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
response = TestClient(module.app).get("/")
hdj = fixture / "status.hdj"
parsed = parse_hdj_source("status.hdj", hdj.read_text(encoding="utf-8"))
print(json.dumps({
    "http_status": response.status_code,
    "contains_ready": "ready" in response.text,
    "interaction_marker": 'data-hedron-interaction="request"' in response.text,
    "hdj_format_version": parsed.declaration.format_version,
    "hdj_kind": parsed.declaration.kind.value,
}, sort_keys=True))
"""


def _probe(*, fixture: Path, package_root: Path) -> dict[str, object]:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        str(path)
        for path in (
            package_root / "packages" / "hedron" / "src",
            package_root / "packages" / "hedron-core" / "src",
            package_root / "packages" / "hedron-jinja" / "src",
            fixture,
        )
    )
    probe = _PROBE.replace("__FIXTURE__", str(fixture).replace("\\", "\\\\").replace('"', '\\"'))
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=package_root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = (result.stdout + "\n" + result.stderr).strip()
        raise RuntimeError(detail[-4000:])
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("canonical probe produced no JSON output")
    return json.loads(lines[-1])


def _type_check(*, fixture: Path, package_root: Path) -> dict[str, int]:
    """Type-check the canonical fixture against one materialized source tree."""
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        str(path)
        for path in (
            package_root / "packages" / "hedron" / "src",
            package_root / "packages" / "hedron-core" / "src",
            package_root / "packages" / "hedron-jinja" / "src",
            fixture,
        )
    )
    result = subprocess.run(
        [sys.executable, "-m", "pyright", str(fixture / "app.py")],
        cwd=package_root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = (result.stdout + "\n" + result.stderr).strip()
        raise RuntimeError(f"canonical type-check failed for {package_root}: {detail[-4000:]}")
    return {"returncode": result.returncode}


def _materialize(tag: str) -> tuple[Path, str, tempfile.TemporaryDirectory[str]]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-list", "-1", tag], cwd=ROOT, text=True, stderr=subprocess.STDOUT
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(f"immutable baseline tag is unavailable: {tag}") from exc
    temporary = tempfile.TemporaryDirectory(prefix="hedron-100-upgrade-")
    root = Path(temporary.name)
    archive = subprocess.Popen(
        ["git", "archive", tag], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert archive.stdout is not None
    extract = subprocess.run(
        ["tar", "-x", "-f", "-", "-C", str(root)], stdin=archive.stdout, check=False
    )
    archive.stdout.close()
    stderr = archive.stderr.read().decode("utf-8", errors="replace") if archive.stderr else ""
    if archive.wait() or extract.returncode:
        temporary.cleanup()
        raise RuntimeError(f"could not materialize {tag}: {stderr.strip()}")
    return root, commit, temporary


def run(*, baseline: str = "v0.67.0") -> dict[str, object]:
    baseline_root, baseline_commit, temporary = _materialize(baseline)
    try:
        baseline_facts = _probe(fixture=FIXTURE, package_root=baseline_root)
        current_facts = _probe(fixture=FIXTURE, package_root=ROOT)
        baseline_typecheck = _type_check(fixture=FIXTURE, package_root=baseline_root)
        current_typecheck = _type_check(fixture=FIXTURE, package_root=ROOT)
    finally:
        temporary.cleanup()
    expected = {
        "http_status": 200,
        "contains_ready": True,
        "interaction_marker": True,
        "hdj_format_version": 1,
        "hdj_kind": "fragment",
    }
    if baseline_facts != expected:
        raise RuntimeError(f"baseline canonical probe mismatch: {baseline_facts!r}")
    if current_facts != expected:
        raise RuntimeError(f"current canonical probe mismatch: {current_facts!r}")
    return {
        "schema": "hedron.upgrade-bridge/1",
        "baseline": baseline,
        "baseline_commit": baseline_commit,
        "fixture": "tests/upgrade/phase_1_0/canonical",
        "baseline_result": baseline_facts,
        "current_result": current_facts,
        "baseline_typecheck": baseline_typecheck,
        "current_typecheck": current_typecheck,
        "target_artifact": {"available": False},
        "release_claim": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default="v0.67.0")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = run(baseline=args.baseline)
    except (OSError, RuntimeError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"upgrade bridge failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            f"{report['baseline']} -> canonical fixture: baseline and current probes passed; "
            "target artifact unavailable"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
