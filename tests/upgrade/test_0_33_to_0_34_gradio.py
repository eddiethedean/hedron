"""Upgrade fixtures for hedron-gradio 0.1.x -> 0.2.x."""

from __future__ import annotations

import json
from pathlib import Path

from hedron_gradio import GradioClientAdapter, GradioEndpoint, __version__

GOLDEN = Path(__file__).resolve().parents[1] / "goldens_0_33_0" / "gradio_adapter_disabled.json"


def test_gradio_version_bumped() -> None:
    assert __version__ == "0.2.1"


def test_disabled_adapter_snapshot_stable() -> None:
    adapter = GradioClientAdapter("https://demo.example.invalid")
    payload = {
        "enabled": adapter.enabled,
        "discover": adapter.discover(),
        "version": __version__,
    }
    if GOLDEN.is_file():
        expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
        assert payload == expected
    else:
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_enabled_adapter_still_supports_preloaded_endpoints() -> None:
    endpoints = (
        GradioEndpoint(name="predict", api_name="/predict", parameters={"text": "string"}),
    )
    adapter = GradioClientAdapter(
        "https://demo.example.invalid",
        enabled=True,
        remote_config=None,
        endpoints=endpoints,
    )
    assert [item.name for item in adapter.discover()] == ["predict"]
    result = adapter.predict("predict", {"text": "hi"})
    assert result["status"] == "ok"
