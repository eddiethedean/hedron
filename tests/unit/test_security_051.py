"""SECURITY-051 extras CSP/offline and sandbox isolation."""

from __future__ import annotations

from pathlib import Path

from hedron.testing import assert_renders
from hedron_extras.sandbox import BrowserPythonSandbox
from hedron_extras.workbench import JSONEditor


def test_json_not_eval_and_sandbox_network_denied() -> None:
    html = assert_renders(JSONEditor({"ok": True}), contains="no-eval")
    assert "eval(" not in html
    box = assert_renders(BrowserPythonSandbox(), contains="hedron-browser-python-sandbox")
    assert 'data-network="deny"' in box
    assert 'data-server-session="denied"' in box


def test_no_remote_cdn_in_extras_assets() -> None:
    root = Path("packages/hedron-extras/src/hedron_extras/assets")
    for path in root.rglob("*.js"):
        text = path.read_text(encoding="utf-8")
        assert "cdn." not in text.lower()
        assert "http://" not in text
        assert "https://" not in text
