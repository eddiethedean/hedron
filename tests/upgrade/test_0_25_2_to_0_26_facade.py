"""CORE-026: facade upgrade fixtures from Published v0.25.2 goldens."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GOLDENS = Path(__file__).resolve().parent / "goldens_0_25_2"
FACADE = ROOT / "docs" / "api" / "STABLE_FACADE.md"


def _load(name: str) -> dict:
    return json.loads((GOLDENS / name).read_text(encoding="utf-8"))


def test_baseline_is_v0_25_2() -> None:
    for name in (
        "identities.json",
        "diagnostics.json",
        "manifest_keys.json",
        "htmx_interaction.json",
    ):
        assert _load(name)["baseline"] == "v0.25.2"


def test_facade_symbols_match_stable_facade_inventory() -> None:
    identities = _load("identities.json")
    text = FACADE.read_text(encoding="utf-8")
    start = text.index("```text")
    end = text.index("```", start + 7)
    current = sorted(
        ln.strip()
        for ln in text[start:end].splitlines()
        if ":" in ln and not ln.strip().startswith("```")
    )
    assert identities["facade_symbols"] == current


def test_diagnostics_forbid_secrets() -> None:
    diagnostics = _load("diagnostics.json")
    sample = {
        "package": "hedron",
        "version": "0.25.2",
        "security_profile": "standard",
        "explorer_mode": "off",
    }
    for key in diagnostics["required_keys"]:
        assert key in sample
    for forbidden in diagnostics["forbidden_keys"]:
        assert forbidden not in sample


def test_manifest_required_keys_documented() -> None:
    keys = _load("manifest_keys.json")["required_keys"]
    assert "assets" in keys
    assert "htmx_version" in keys
    assert "content_hash" in keys


def test_htmx_interaction_polling_only() -> None:
    htmx = _load("htmx_interaction.json")
    assert htmx["polling_only"] is True
    for header in ("HX-Retarget", "HX-Reswap"):
        assert header in htmx["supported_headers"]


def test_facade_symbols_importable() -> None:
    """Supported facade symbols remain importable (no silent removals)."""
    identities = _load("identities.json")
    missing: list[str] = []
    for entry in identities["facade_symbols"]:
        module_name, _, attr = entry.partition(":")
        if "." in attr:
            # methods like Hedron.region — check class exists
            cls_name, _, _method = attr.partition(".")
            attr = cls_name
        try:
            module = __import__(module_name, fromlist=[attr])
            getattr(module, attr)
        except Exception as exc:  # noqa: BLE001 - collect import failures
            missing.append(f"{entry}: {exc}")
    assert not missing, missing
