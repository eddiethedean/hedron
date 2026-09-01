"""Behavioral coverage for the canonical Hedron 1.0 style CLI."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

import pytest

from hedron.cli.commands.style import (
    APPLICATION_STYLE_EJECTION_SCHEMA,
    DIFF_SCHEMA,
    _application_style_ejection_payload,
    _design_diff,
    _list_diff,
    _mapping_diff,
    _resolve_design,
    _safe_write_text,
)
from hedron.cli.parser import main


def _run_cli(arguments: list[str]) -> int:
    with pytest.raises(SystemExit) as raised:
        main(arguments)
    return int(raised.value.code or 0)


def test_mapping_and_list_diffs_report_each_change_class() -> None:
    assert _mapping_diff(
        {"same": 1, "changed": 2, "removed": 3},
        {"same": 1, "changed": 4, "added": 5},
    ) == {
        "added": {"added": 5},
        "removed": {"removed": 3},
        "changed": {"changed": {"base": 2, "candidate": 4}},
    }
    assert _list_diff(["a"], ["a", "b"]) == {
        "base_count": 1,
        "candidate_count": 2,
        "equal": False,
        "base": ["a"],
        "candidate": ["a", "b"],
    }


def test_builtin_design_diff_is_deterministic_and_detects_css_change() -> None:
    args = argparse.Namespace(app=None, design=None, _hedron_app=None)
    default = _resolve_design(args, name="default")
    aurora = _resolve_design(args, name="aurora")

    first = _design_diff(default, aurora)
    second = _design_diff(default, aurora)

    assert first == second
    assert first["schema"] == DIFF_SCHEMA
    assert first["base_digest"] != first["candidate_digest"]
    assert first["emitted_output"]["css_equal"] is False


def test_style_diff_json_runs_through_public_parser(capsys: pytest.CaptureFixture[str]) -> None:
    assert _run_cli(["style", "diff", "default", "aurora", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema"] == DIFF_SCHEMA
    assert payload["tokens"]["changed"]


def test_style_preview_writes_bounded_gallery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    assert _run_cli(["style", "preview", "--output", "preview", "--mode", "dark"]) == 0
    payload = json.loads(capsys.readouterr().out)
    page = tmp_path / payload["written"][0]
    html = page.read_text(encoding="utf-8")
    assert page == tmp_path / "preview" / "index.html"
    assert 'data-mode="dark"' in html
    assert 'data-mode="light"' not in html
    assert "no application data" in html


def test_style_init_package_and_conform_round_trip(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)
    spec = Path("theme.json")
    archive = Path("theme.zip")

    assert _run_cli(["style", "init", "--name", "company", "--output", str(spec)]) == 0
    initialized = json.loads(capsys.readouterr().out)
    assert initialized["fingerprint"]
    assert json.loads(spec.read_text(encoding="utf-8"))["name"] == "company"

    assert _run_cli(["style", "conform", "--spec", str(spec), "--profile", "core"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["ok"] is True

    assert (
        _run_cli(
            [
                "style",
                "package",
                "--spec",
                str(spec),
                "--output",
                str(archive),
                "--profile",
                "core",
                "--license",
                "MIT",
            ]
        )
        == 0
    )
    packaged = json.loads(capsys.readouterr().out)
    assert packaged["manifest"]["profile"] == "core"
    with zipfile.ZipFile(archive) as bundle:
        assert {"manifest.json", "theme.json"} <= set(bundle.namelist())


def test_safe_write_text_replaces_project_file_without_temporary_leaks(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "result.txt"
    _safe_write_text(target, "first", cwd=tmp_path)
    _safe_write_text(target, "second", cwd=tmp_path)
    assert target.read_text(encoding="utf-8") == "second"
    assert list(target.parent.glob(f".{target.name}.*")) == []


@pytest.mark.parametrize(
    ("update", "message"),
    [
        ({"schema": "other/1"}, "unsupported"),
        ({"files": ["only.css"]}, "two local file names"),
        ({"css_digest": "sha256-nope"}, "invalid CSS digest"),
        ({"styles": [], "blocks": [{}]}, "must align"),
    ],
)
def test_application_style_manifest_validation_fails_closed(
    tmp_path: Path,
    update: dict[str, object],
    message: str,
) -> None:
    digest = "sha256-" + "0" * 64
    payload: dict[str, object] = {
        "schema": APPLICATION_STYLE_EJECTION_SCHEMA,
        "files": ["application-styles.css", "source_map.json"],
        "styles": [],
        "blocks": [],
        "css_digest": digest,
    }
    payload.update(update)
    manifest = tmp_path / "source_map.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        _application_style_ejection_payload(manifest)
