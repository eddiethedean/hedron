"""Exercise publication and required-check failures without external services."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("conclusion", ["success", "failure", "cancelled", "null", ""])
def test_release_requires_success_for_exact_checked_out_commit(
    tmp_path: Path, conclusion: str
) -> None:
    gh = tmp_path / "gh"
    gh.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$ARGUMENTS"\nprintf "%s" "$CONCLUSION"\n')
    gh.chmod(0o755)
    arguments = tmp_path / "arguments"
    env = {
        **os.environ,
        "PATH": f"{tmp_path}:{os.environ['PATH']}",
        "ARGUMENTS": str(arguments),
        "CONCLUSION": conclusion,
    }
    result = subprocess.run(
        ["bash", str(ROOT / "scripts/check_release_ci.sh")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert (result.returncode == 0) == (conclusion == "success")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    args = arguments.read_text().splitlines()
    assert args[args.index("--commit") + 1] == commit
    assert args[args.index("--workflow") + 1] == "ci.yml"
    assert args[args.index("--event") + 1] == "push"


@pytest.mark.parametrize(
    ("event", "docs_only", "failed_job", "expected_success"),
    [
        ("pull_request", False, None, True),
        ("pull_request", False, "coverage", False),
        ("pull_request", False, "packaging", False),
        ("pull_request", False, "quality", False),
        ("pull_request", True, None, True),
        ("pull_request", True, "quality", False),
        ("pull_request", True, "changes", False),
        ("push", False, None, True),
        ("push", False, "test", False),
        ("push", False, "browser", False),
        ("push", False, "dependency-bounds", False),
        ("workflow_dispatch", False, "browser", False),
        ("schedule", False, "dependency-bounds", False),
    ],
)
def test_required_gate_handles_pr_docs_and_full_matrix(
    event: str, docs_only: bool, failed_job: str | None, expected_success: bool
) -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text()
    required_job = workflow.split("  required:\n", 1)[1]
    body = textwrap.dedent(required_job.split("        run: |\n", 1)[1])
    code = body.split("<<'PYTHON'\n", 1)[1].rsplit("PYTHON", 1)[0]
    results = {
        name: {"result": "success"}
        for name in (
            "changes",
            "coverage",
            "test",
            "dependency-bounds",
            "quality",
            "browser",
            "packaging",
        )
    }
    if event == "pull_request":
        for name in ("test", "dependency-bounds", "browser"):
            results[name]["result"] = "skipped"
    if docs_only:
        for name in ("coverage", "packaging"):
            results[name]["result"] = "skipped"
    if failed_job:
        results[failed_job]["result"] = "failure"
    result = subprocess.run(
        [sys.executable, "-c", code],
        env={
            **os.environ,
            "RESULTS": json.dumps(results),
            "DOCS_ONLY": str(docs_only).lower(),
            "EVENT_NAME": event,
        },
        capture_output=True,
        text=True,
        check=False,
    )
    assert (result.returncode == 0) == expected_success, result.stderr


@pytest.mark.parametrize("fail_package", ["", "hedron-core", "hedron"])
def test_publish_stops_before_dependents_and_never_uploads_native(
    tmp_path: Path, fail_package: str
) -> None:
    workflow = (ROOT / ".github/workflows/release.yml").read_text()
    step = workflow.split("      - name: Publish to PyPI\n", 1)[1]
    body = textwrap.dedent(step.split("        run: |\n", 1)[1].split("      - name:", 1)[0])
    (tmp_path / "dist").mkdir()
    for name in ("hedron_core", "hedron", "edron"):
        for suffix in ("-py3-none-any.whl", ".tar.gz"):
            (tmp_path / "dist" / f"{name}-1.3.0{suffix}").touch()
    uv = tmp_path / "uv"
    uv.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = run ]; then\n'
        '  printf "hedron-core\\nhedron\\nhedron-native\\nedron\\n"\n'
        "else\n"
        '  printf "%s\\n" "$*" >> "$UPLOADS"\n'
        '  case "$*" in *"$FAIL_STEM-1.3.0"*) exit 1;; esac\n'
        "fi\n"
    )
    uv.chmod(0o755)
    timeout = tmp_path / "timeout"
    timeout.write_text('#!/bin/sh\nshift\nexec "$@"\n')
    timeout.chmod(0o755)
    uploads = tmp_path / "uploads"
    result = subprocess.run(
        ["bash", "-c", body],
        cwd=tmp_path,
        env={
            **os.environ,
            "PATH": f"{tmp_path}:{os.environ['PATH']}",
            "UV_PUBLISH_TOKEN": "test",
            "UPLOADS": str(uploads),
            "FAIL_STEM": fail_package.replace("-", "_") or "never",
        },
        capture_output=True,
        text=True,
        check=False,
    )
    log = uploads.read_text()
    assert (result.returncode == 0) == (not fail_package), result.stderr
    assert "hedron_native" not in log
    assert "--check-url https://pypi.org/simple/" in log
    if fail_package:
        assert "dist/edron-1.3.0" not in log
    else:
        assert "dist/edron-1.3.0" in log
