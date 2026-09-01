"""Independent package coverage gate behavior."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts.check_coverage_thresholds import main, package_coverage


def _report() -> dict[str, object]:
    return {
        "files": {
            "packages/hedron/src/hedron/app.py": {
                "summary": {
                    "num_statements": 80,
                    "covered_lines": 60,
                    "num_branches": 20,
                    "covered_branches": 15,
                }
            },
            "packages/hedron-core/src/hedron_core/catalog.py": {
                "summary": {
                    "num_statements": 50,
                    "covered_lines": 45,
                    "num_branches": 10,
                    "covered_branches": 5,
                }
            },
            "packages/hedron-core/src/hedron_core/patches.py": {
                "summary": {
                    "num_statements": 30,
                    "covered_lines": 30,
                    "num_branches": 10,
                    "covered_branches": 10,
                }
            },
        }
    }


def test_package_coverage_weights_statements_and_branches_across_files() -> None:
    result = package_coverage(
        _report(),
        name="hedron-core",
        source_prefix="packages/hedron-core/src/hedron_core",
    )
    assert result.covered == 90
    assert result.total == 100
    assert result.percent == 90.0


def test_coverage_gate_enforces_each_package_independently(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = tmp_path / "coverage.json"
    report.write_text(json.dumps(_report()), encoding="utf-8")

    assert main([str(report), "--hedron", "75", "--hedron-core", "90"]) == 0
    assert "hedron: 75.00%" in capsys.readouterr().out
    assert main([str(report), "--hedron", "76", "--hedron-core", "90"]) == 1
    assert main([str(report), "--hedron", "75", "--hedron-core", "91"]) == 1


@pytest.mark.parametrize(
    "report",
    [
        {},
        {"files": {}},
        {
            "files": {
                "packages/hedron-core/src/hedron_core/x.py": {"summary": {"num_statements": True}}
            }
        },
    ],
)
def test_coverage_gate_rejects_missing_or_malformed_summaries(report: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        package_coverage(
            report,
            name="hedron-core",
            source_prefix="packages/hedron-core/src/hedron_core",
        )
