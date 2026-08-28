#!/usr/bin/env python3
"""Run the reproducible Data Mover migration slice for CONSUMER-059."""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONSUMER = ROOT.parent / "user-token-managment-app"
OUTPUT = ROOT / "docs/acceptance/evidence-059/consumer-059.json"
FOCUSED_TESTS = (
    "tests/test_ui_shell.py",
    "tests/test_ui_interactions.py",
    "tests/test_pipeline_runs.py",
)


def _run(
    command: list[str], *, cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False)


def main() -> int:
    consumer = Path(os.environ.get("HEDRON_CONSUMER_ROOT", str(DEFAULT_CONSUMER))).resolve()
    errors: list[str] = []
    required = (
        consumer / "app/ui/forms.py",
        consumer / "app/ui/layout.py",
        consumer / "app/ui/routes/pipeline.py",
        consumer / "app/static/theme.css",
        consumer / "pyproject.toml",
        consumer / "requirements.txt",
    )
    errors.extend(
        f"missing consumer migration file: {path}" for path in required if not path.is_file()
    )
    pyproject = (
        (consumer / "pyproject.toml").read_text(encoding="utf-8")
        if (consumer / "pyproject.toml").is_file()
        else ""
    )
    requirements = (
        (consumer / "requirements.txt").read_text(encoding="utf-8")
        if (consumer / "requirements.txt").is_file()
        else ""
    )
    for text, source in ((pyproject, "pyproject.toml"), (requirements, "requirements.txt")):
        if "hedron>=0.59.0,<0.60" not in text or "hedron-posit>=0.59.0,<0.60" not in text:
            errors.append(f"{source}: Hedron dependencies are not pinned to the 0.59 train")
    source_text = "\n".join(
        (consumer / relative).read_text(encoding="utf-8")
        for relative in ("app/ui", "app/static/theme.css")
        if (consumer / relative).is_file()
    )
    for legacy in ("button-small", "button-wide"):
        if legacy in source_text:
            errors.append(f"consumer still contains bespoke selector {legacy!r}")

    git = _run(["git", "rev-parse", "HEAD"], cwd=consumer)
    consumer_commit = git.stdout.strip() if git.returncode == 0 else None
    python = consumer / ".venv/bin/python"
    collected_total = 0
    full_suite = os.environ.get("HEDRON_CONSUMER_FULL", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    tests = () if full_suite else FOCUSED_TESTS
    if not python.is_file():
        errors.append(f"consumer virtualenv is missing: {python}")
        result = None
    else:
        env = os.environ.copy()
        source_paths = [
            ROOT / "packages/hedron-core/src",
            ROOT / "packages/hedron/src",
            ROOT / "packages/hedron-posit/src",
        ]
        env["PYTHONPATH"] = (
            os.pathsep.join(str(path) for path in source_paths)
            + os.pathsep
            + env.get("PYTHONPATH", "")
        )
        collect_command = [str(python), "-m", "pytest", "--collect-only", "-q", *tests]
        collected = _run(collect_command, cwd=consumer, env=env)
        collected_counts = [
            int(value) for value in re.findall(r":\s+(\d+)\s*$", collected.stdout, re.M)
        ]
        collected_total = sum(collected_counts)
        command = [str(python), "-m", "pytest", "-q", "--tb=short", *tests]
        result = _run(command, cwd=consumer, env=env)
        if result.returncode != 0:
            errors.append("consumer migration test slice failed")

    combined = (result.stdout + "\n" + result.stderr) if result else ""
    passed_match = re.search(r"\b(?P<count>\d+)\s+passed\b", combined)
    artifact = {
        "schema": "hedron.consumer-evidence/1",
        "phase": "0.59",
        "consumer": str(consumer),
        "consumer_commit": consumer_commit,
        "consumer_worktree_dirty": _run(["git", "status", "--short"], cwd=consumer).stdout.strip()
        != "",
        "dependency_contract": "hedron>=0.59.0,<0.60; hedron-posit>=0.59.0,<0.60",
        "legacy_selectors": [],
        "suite": "full" if full_suite else "focused",
        "tests": list(tests) if tests else ["<consumer test suite>"],
        "collected": collected_total,
        "passed": int(passed_match.group("count"))
        if passed_match
        else (collected_total if result and result.returncode == 0 else 0),
        "returncode": result.returncode if result else 1,
        "test_output_tail": combined[-1000:],
        "errors": errors,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    OUTPUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(artifact, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
