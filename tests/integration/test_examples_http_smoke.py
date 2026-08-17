"""Isolated HTTP smokes so every example actually serves its home route.

Hedron keeps a process-wide route registry, so each app is loaded in a
subprocess. Modules are registered in ``sys.modules`` before exec so postponed
annotations (``from __future__ import annotations``) resolve for FormBody.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

_ASGI_CASES: tuple[tuple[str, str, int], ...] = (
    ("examples/theme-gallery/app.py", "/", 200),
    ("examples/streamlit-migration/app.py", "/", 200),
    ("examples/notes-sqlalchemy/app.py", "/", 200),
    ("examples/session-auth/app.py", "/", 303),
    ("examples/session-auth/app.py", "/login", 200),
    ("examples/file-upload/app.py", "/", 200),
    ("examples/jobs-poll/app.py", "/", 200),
    ("examples/package-workflows/app.py", "/", 200),
    ("examples/live-interaction/app.py", "/", 200),
    ("examples/reference-app/app.py", "/", 401),
    ("examples/workbench-reference/app.py", "/", 200),
    ("examples/workbench-reference/app_facade.py", "/", 200),
    ("examples/workbench-reference/app_posit.py", "/", 200),
    ("examples/connect-reference/app.py", "/", 200),
    ("examples/fastapi-workbench-reference/app.py", "/", 200),
    ("examples/model-demo-0.18/app.py", "/", 200),
    ("examples/dashboard-0.17/app.py", "/", 200),
    ("examples/data-app-0.16/app.py", "/", 200),
    ("examples/data-app-0.15/app.py", "/", 200),
    ("docs/demos/runnable/hello-refresh.py", "/", 200),
)

_CHILD = r"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

root = Path(sys.argv[1])
rel = sys.argv[2]
path = sys.argv[3]
expected = int(sys.argv[4])
os.chdir(root)

spec = importlib.util.spec_from_file_location("hedron_example_http_smoke", root / rel)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules["hedron_example_http_smoke"] = module
spec.loader.exec_module(module)

from fastapi.testclient import TestClient

with TestClient(module.app) as client:
    response = client.get(path, follow_redirects=False)
if response.status_code != expected:
    raise SystemExit(
        f"{rel} GET {path} -> {response.status_code} (want {expected})\n{response.text[:800]}"
    )
print(f"ok {rel} GET {path} {response.status_code}")
"""


def _run_child(code: str, *args: str, env: dict[str, str] | None = None) -> None:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    proc = subprocess.run(
        [sys.executable, "-c", code, str(ROOT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=merged,
        check=False,
    )
    if proc.returncode != 0:
        pytest.fail(proc.stdout + proc.stderr)


@pytest.mark.parametrize(("rel", "path", "expected"), _ASGI_CASES)
def test_example_asgi_home(rel: str, path: str, expected: int) -> None:
    _run_child(_CHILD, rel, path, str(expected))


def test_oidc_example_home_with_settings() -> None:
    _run_child(
        _CHILD,
        "examples/oidc/app.py",
        "/",
        "200",
        env={
            "OIDC_ISSUER": "https://identity.example.test",
            "OIDC_CLIENT_ID": "client",
            "OIDC_CLIENT_SECRET": "secret",
            "SESSION_SECRET": "test-session-secret",
        },
    )


def test_flask_reference_home_and_fragment() -> None:
    _run_child(
        r"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

root = Path(sys.argv[1])
os.chdir(root)
path = root / "examples" / "flask-reference" / "app.py"
spec = importlib.util.spec_from_file_location("flask_ref_smoke", path)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules["flask_ref_smoke"] = mod
spec.loader.exec_module(mod)
client = mod.create_app().test_client()
home = client.get("/")
assert home.status_code == 200, home.status_code
assert b"Flask Reference" in home.get_data()
frag = client.get("/fragment", headers={"HX-Request": "true", "HX-Target": "#panel"})
assert frag.status_code == 200, frag.status_code
print("ok flask-reference")
"""
    )


def test_django_reference_home_and_fragment() -> None:
    _run_child(
        r"""
from __future__ import annotations

import os
import sys
from pathlib import Path

root = Path(sys.argv[1])
django_root = root / "examples" / "django-reference"
os.chdir(django_root)
sys.path.insert(0, str(django_root))
from django.test import Client
from hedron_django_ref import application  # noqa: F401

client = Client()
home = client.get("/")
assert home.status_code == 200, home.content[:800]
assert b"Django Reference" in home.content
frag = client.get("/fragment", HTTP_HX_REQUEST="true", HTTP_HX_TARGET="#panel")
assert frag.status_code == 200, frag.status_code
print("ok django-reference")
"""
    )


def test_hdj_progressive_prints_html() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "examples" / "hdj-progressive" / "app.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0 or "<" not in proc.stdout:
        pytest.fail(proc.stdout + proc.stderr)
