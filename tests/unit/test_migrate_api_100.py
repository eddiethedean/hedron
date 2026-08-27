"""MIGRATE-100: deterministic, non-executing Hedron 1.0 API migration."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hedron.migrate.api import scan_api, transform_api, unified_diff
from hedron_core.migration import PUBLIC_FUTURE_WARNINGS


def test_scan_flags_only_registered_legacy_paths(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text(
        "\n".join(
            (
                "@app.page('/')",
                "def home(): pass",
                "@app.refreshable",
                "def status(): pass",
                "@app.command(fallback='/')",
                "def save(): pass",
                "@app.component('/legacy')",
                "def old(): pass",
                "app.include_feature(bundle)",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    report = scan_api(source)
    assert [(item.old_path, item.confidence) for item in report.findings] == [
        ("app.refreshable", "partial"),
        ("app.command", "partial"),
        ("app.component", "complete"),
        ("app.include_feature", "complete"),
    ]
    assert "refreshable" not in {item.old_path for item in report.findings}
    assert "command" not in {item.old_path for item in report.findings}
    assert report.findings[0].removal_version == "1.0"
    assert report.findings[0].fixture == "tests/upgrade/shared.py"


def test_scan_does_not_treat_simapp_fragment_as_hedron_legacy_api(tmp_path: Path) -> None:
    source = tmp_path / "sim.py"
    source.write_text(
        "from hedron_sim import SimApp\n"
        "app = SimApp(demo_id='offline')\n"
        "@app.fragment('/status', region='panel')\n"
        "def status(): pass\n",
        encoding="utf-8",
    )

    assert scan_api(source).findings == ()


def test_scan_keeps_same_line_calls_as_separate_call_sites(tmp_path: Path) -> None:
    source = tmp_path / "same_line.py"
    source.write_text("app.component('/a'); app.component('/b')\n", encoding="utf-8")
    assert len(scan_api(source).findings) == 2


def test_scan_and_transform_direct_legacy_helper_imports(tmp_path: Path) -> None:
    source = tmp_path / "imports.py"
    source.write_text(
        "from hedron import include_feature, refreshable\n"
        "include_feature(bundle)\n",
        encoding="utf-8",
    )

    report = scan_api(source)

    assert [(item.kind, item.old_path, item.confidence) for item in report.findings] == [
        ("import", "app.include_feature", "unknown"),
        ("import", "app.refreshable", "unknown"),
    ]
    output = tmp_path / "migrated.py"
    transform_api(source, output=output)
    assert output.read_text(encoding="utf-8").startswith(
        "from hedron import include_feature, refreshable\n"
    )


def test_region_fragment_is_reported_partial_and_not_rewritten(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text(
        "@app.fragment('/legacy', region='panel')\ndef old(): pass\n",
        encoding="utf-8",
    )
    report = scan_api(source)
    assert report.requires_review
    assert report.findings[0].confidence == "partial"
    assert unified_diff(source) == ""


def test_unsafe_component_route_is_manual_action_migration(tmp_path: Path) -> None:
    source = tmp_path / "unsafe.py"
    source.write_text(
        "@app.component('/save', methods=['POST'])\n"
        "def save(): pass\n",
        encoding="utf-8",
    )

    finding = scan_api(source).findings[0]

    assert finding.replacement == "app.action"
    assert finding.confidence == "partial"
    assert finding.automation_status == "manual-review"
    assert unified_diff(source) == ""


def test_reflection_is_unknown_and_never_rewritten(tmp_path: Path) -> None:
    source = tmp_path / "dynamic.py"
    source.write_text("handler = getattr(app, 'component')\n", encoding="utf-8")
    finding = scan_api(source).findings[0]
    assert finding.confidence == "unknown"
    assert finding.automation_status == "manual-review"
    assert unified_diff(source) == ""


def test_transform_is_non_executing_idempotent_and_refuses_overwrite(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text(
        "raise RuntimeError('must never execute')\napp.include_feature(bundle)\n",
        encoding="utf-8",
    )
    output = tmp_path / "out.py"
    report = transform_api(source, output=output)
    assert report.changes[0].replacements == 1
    assert "app.include(bundle)" in output.read_text(encoding="utf-8")
    with pytest.raises(FileExistsError):
        transform_api(source, output=output)
    assert transform_api(output).findings == ()


def test_transform_output_is_a_complete_reviewable_tree(tmp_path: Path) -> None:
    source = tmp_path / "project"
    source.mkdir()
    (source / "app.py").write_text("app.include_feature(bundle)\n", encoding="utf-8")
    (source / "README.md").write_text("unchanged project notes\n", encoding="utf-8")
    output = tmp_path / "migrated"

    report = transform_api(source, output=output)

    assert report.changes[0].path == "app.py"
    assert (output / "app.py").read_text(encoding="utf-8") == "app.include(bundle)\n"
    assert (output / "README.md").read_text(encoding="utf-8") == "unchanged project notes\n"


def test_transform_output_creates_nested_destination_parent(tmp_path: Path) -> None:
    source = tmp_path / "project"
    source.mkdir()
    (source / "app.py").write_text("app.include_feature(bundle)\n", encoding="utf-8")
    output = tmp_path / "artifacts" / "migrated"

    transform_api(source, output=output)

    assert (output / "app.py").read_text(encoding="utf-8") == "app.include(bundle)\n"


@pytest.mark.parametrize("suffix", [".pyi", ".ini", ".cfg", ".conf", ".env", ".lock"])
def test_scan_covers_project_text_artifact_suffixes(tmp_path: Path, suffix: str) -> None:
    source = tmp_path / f"settings{suffix}"
    source.write_text("app.include_feature(bundle)\n", encoding="utf-8")

    findings = scan_api(source).findings

    assert len(findings) == 1
    assert findings[0].kind == "text"
    assert findings[0].old_path == "app.include_feature"


def test_json_is_stable_and_advertises_schema(tmp_path: Path) -> None:
    source = tmp_path / "app.py"
    source.write_text("@app.component('/')\ndef old(): pass\n", encoding="utf-8")
    payload = json.loads(scan_api(source).to_json())
    assert payload["schema"] == "hedron.api-migration/1"
    assert payload["non_executing"] is True
    assert scan_api(source).to_json() == scan_api(source).to_json()


def test_runtime_and_static_warning_registry_has_complete_metadata() -> None:
    assert PUBLIC_FUTURE_WARNINGS.validate(root=Path(__file__).parents[2]) == ()


def test_cli_registers_the_targeted_api_migrator() -> None:
    from hedron.cli.parser import _build_parser

    args = _build_parser().parse_args(["migrate", "api", "--target", "1.0", "project"])
    assert args.source == "project"
    assert args.target == "1.0"


def test_canonical_app_view_owns_a_refreshable_handle_without_legacy_warning() -> None:
    from tests.unit._helpers_043 import make_app, reset_043

    from hedron import FragmentHandle, Text

    reset_043()
    app = make_app()

    @app.view("/status")
    def status():
        return Text("live")

    assert isinstance(status, FragmentHandle)
    assert status.path == "/status"
