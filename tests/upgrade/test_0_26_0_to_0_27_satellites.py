"""0.27 satellite upgrade fixtures from Published v0.26.0 goldens."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLDENS = Path(__file__).resolve().parent / "goldens_0_26_0"


def _load(name: str) -> dict:
    return json.loads((GOLDENS / name).read_text(encoding="utf-8"))


def test_baseline_is_v0_26_0() -> None:
    for name in (
        "data_contracts.json",
        "adapter_interaction.json",
        "hdj_manifest.json",
        "extras_registry.json",
    ):
        assert _load(name)["baseline"] == "v0.26.0"


def test_data_symbols_importable() -> None:
    identities = _load("data_contracts.json")
    missing: list[str] = []
    for entry in identities["data_symbols"]:
        module_name, _, attr = entry.partition(":")
        try:
            module = __import__(module_name, fromlist=[attr])
            getattr(module, attr)
        except Exception as exc:  # noqa: BLE001
            missing.append(f"{entry}: {exc}")
    assert not missing, missing
    for path in identities["spreadsheet_paths"]:
        import hedron_data

        assert hasattr(hedron_data, path)


def test_adapter_interaction_polling_only() -> None:
    htmx = _load("adapter_interaction.json")
    assert htmx["polling_only"] is True
    for header in ("HX-Retarget", "HX-Reswap"):
        assert header in htmx["supported_headers"]
    for banned in htmx["forbidden_live_parity"]:
        assert banned in {"sse", "websocket", "streaming", "preload"}


def test_hdj_v1_prologue_shape() -> None:
    hdj = _load("hdj_manifest.json")
    assert hdj["version"] == 1
    for rel in hdj["sample_templates"]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert text.startswith("---hdj\n") or text.startswith("---hdj\r\n")
        assert "version = 1" in text
    for key in hdj["required_prologue_keys"]:
        assert key in hdj["allowed_prologue_keys"]


def test_extras_curated_registry_matches_default_exports() -> None:
    golden = _load("extras_registry.json")
    import hedron_extras

    current = sorted(x for x in hedron_extras.__all__ if x != "__version__")
    assert current == sorted(golden["curated_registry"])
    banned = set(golden["absent_from_default"])
    assert banned.isdisjoint(set(hedron_extras.__all__))
