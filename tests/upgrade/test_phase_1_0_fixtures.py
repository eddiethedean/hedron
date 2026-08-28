"""Executable fixture checks for the Hedron 0.67-to-1.0 bridge."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

from hedron.migrate.api import scan_api

ROOT = Path(__file__).parent / "phase_1_0"


def test_canonical_fixture_has_no_transitional_findings() -> None:
    report = scan_api(ROOT / "canonical")
    assert report.findings == ()
    assert report.files_seen == 3  # app.py, config.toml, and README.md


def test_transitional_fixture_corpus_covers_warning_floor() -> None:
    expected = {
        "app_component.py": "app.component",
        "app_fragment.py": "app.fragment",
        "app_include_feature.py": "app.include_feature",
        "router_component.py": "router.component",
        "app_screen.py": "app.screen",
        "app_refreshable.py": "app.refreshable",
        "app_command.py": "app.command",
        "app_form_command.py": "app.form_command",
    }
    observed = {}
    for filename, _old_path in expected.items():
        findings = scan_api(ROOT / "transitional" / filename).findings
        assert findings, filename
        observed[filename] = findings[0].old_path
        assert findings[0].fixture == "tests/upgrade/shared.py"
        assert findings[0].removal_version == "1.0"
    assert observed == expected


def test_negative_dynamic_fixture_is_manual_unknown() -> None:
    findings = scan_api(ROOT / "negative" / "undeclared_dynamic.py").findings
    assert len(findings) == 1
    assert findings[0].confidence == "unknown"
    assert findings[0].automation_status == "manual-review"


def test_canonical_fixture_imports_and_serves_page() -> None:
    path = ROOT / "canonical" / "app.py"
    spec = importlib.util.spec_from_file_location("hedron_phase_1_canonical", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    response = TestClient(module.app).get("/")
    assert response.status_code == 200
    assert "ready" in response.text
    assert 'data-hedron-interaction="request"' in response.text
