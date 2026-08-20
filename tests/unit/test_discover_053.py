"""DISCOVER-053 evidence."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest

from hedron.cli import main
from hedron.discover_api import STABILITY_INVENTORY_VERSION, discover_public_api


def test_discover_053_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.53.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["DISCOVER-053"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md").is_file()


def test_discover_public_api_json_covers_all_and_preserves_names() -> None:
    import hedron

    payload = discover_public_api(format="json")
    assert isinstance(payload, dict)
    assert payload["version"] == STABILITY_INVENTORY_VERSION == "1.0.0"
    names = [item["name"] for item in payload["items"]]
    assert names == sorted(hedron.__all__)
    # Existing imports are never renamed — inventory names must match __all__ exactly.
    assert set(names) == set(hedron.__all__)
    by_name = {item["name"]: item["stability"] for item in payload["items"]}
    assert by_name["Hedron"] == "stable"
    assert by_name["Page"] == "stable"
    # Unknown / unmapped public names default to supported.
    assert "Alert" in by_name
    assert by_name["Alert"] == "supported"
    assert set(by_name.values()) <= {"supported", "stable", "experimental"}


def test_discover_public_api_human_is_multiline_text() -> None:
    text = discover_public_api(format="human")
    assert isinstance(text, str)
    lines = text.strip().splitlines()
    assert lines[0].startswith("stability inventory ")
    assert "\t" in lines[1]
    assert "Hedron\tstable" in text


def test_hedron_discover_cli_json(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exited:
        main(["discover", "--format", "json"])
    assert exited.value.code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["version"] == "1.0.0"
    assert any(item["name"] == "Hedron" for item in payload["items"])
