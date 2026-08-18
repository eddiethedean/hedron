"""DataEditor CSRF token resolution for JSON fetch saves (#216)."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

EDITOR_JS = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "hedron-data"
    / "src"
    / "hedron_data"
    / "assets"
    / "tabulator"
    / "editor.js"
)


@pytest.fixture(scope="module")
def node_bin() -> str:
    path = shutil.which("node")
    if path is None:
        pytest.skip("node is required for DataEditor CSRF helper tests")
    return path


def _run_node(node_bin: str, script: str) -> str:
    result = subprocess.run(
        [node_bin, "-e", script],
        check=True,
        capture_output=True,
        text=True,
        cwd=str(EDITOR_JS.parent),
    )
    return result.stdout.strip()


def test_read_csrf_token_prefers_meta_then_hedron_cookie(node_bin: str) -> None:
    script = EDITOR_JS.read_text(encoding="utf-8")
    assert "function readCsrfToken" in script
    assert 'meta[name="csrf-token"]' in script
    assert 'headers["X-CSRF-Token"] = csrfToken' in script

    out = _run_node(
        node_bin,
        f"""
const api = require({json.dumps(str(EDITOR_JS))});
const doc = {{
  querySelector(sel) {{
    if (sel === 'meta[name="csrf-token"]') {{
      return {{ getAttribute(name) {{ return name === "content" ? "from-meta" : ""; }} }};
    }}
    return null;
  }},
}};
const noMeta = {{ querySelector() {{ return null; }} }};
const cookieJar = "a=1; hedron_csrf=cookie%2Dtok; b=2";
process.stdout.write(JSON.stringify({{
  meta: api.readCsrfToken(doc, "hedron_csrf=from-cookie; other=1"),
  cookieOnly: api.readCsrfToken(noMeta, cookieJar),
  empty: api.readCsrfToken(noMeta, "session=abc"),
}}));
""",
    )
    payload = json.loads(out)
    assert payload["meta"] == "from-meta"
    assert payload["cookieOnly"] == "cookie-tok"
    assert payload["empty"] == ""


def test_read_csrf_token_falls_back_to_django_csrftoken_cookie(node_bin: str) -> None:
    out = _run_node(
        node_bin,
        f"""
const api = require({json.dumps(str(EDITOR_JS))});
const noMeta = {{ querySelector() {{ return null; }} }};
const djangoJar = "session=abc; csrftoken=django%2Dtok; other=1";
process.stdout.write(JSON.stringify({{
  django: api.readCsrfToken(noMeta, djangoJar),
  hedronPreferred: api.readCsrfToken(noMeta, "csrftoken=ignored; hedron_csrf=hedron-tok"),
}}));
""",
    )
    payload = json.loads(out)
    assert payload["django"] == "django-tok"
    assert payload["hedronPreferred"] == "hedron-tok"
