"""Built-wheel and immutable-artifact regression coverage."""

from __future__ import annotations

import io
import sys
import tomllib
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_workbench_release_artifacts as artifacts  # noqa: E402


def test_workbench_dependency_floors_select_corrected_artifacts() -> None:
    hedron = tomllib.loads(
        (ROOT / "packages" / "hedron" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    posit = tomllib.loads(
        (ROOT / "packages" / "hedron-posit" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    assert hedron["optional-dependencies"]["posit"] == ["hedron-posit>=1.0.2,<2.0"]
    assert "fastapi-workbench>=1.0.3,<2.0" in posit["dependencies"]


def wheel_bytes(entries: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    return output.getvalue()


def test_comparable_payload_ignores_wheel_records_but_keeps_metadata() -> None:
    first = wheel_bytes(
        {
            "demo/__init__.py": b"value = 1\n",
            "demo-1.0.dist-info/METADATA": b"Name: demo\nVersion: 1.0\n",
            "demo-1.0.dist-info/RECORD": b"first",
        }
    )
    second = wheel_bytes(
        {
            "demo/__init__.py": b"value = 1\n",
            "demo-1.0.dist-info/METADATA": b"Name: demo\nVersion: 1.0\n",
            "demo-1.0.dist-info/RECORD": b"second",
        }
    )
    changed_metadata = wheel_bytes(
        {
            "demo/__init__.py": b"value = 1\n",
            "demo-1.0.dist-info/METADATA": b"Name: demo\nVersion: 1.0\nRequires-Dist: x\n",
        }
    )
    assert artifacts.comparable_wheel_payload(first) == artifacts.comparable_wheel_payload(second)
    assert artifacts.comparable_wheel_payload(first) != artifacts.comparable_wheel_payload(
        changed_metadata
    )


def test_middleware_signature_is_read_from_built_wheel(tmp_path: Path) -> None:
    wheel = tmp_path / "fastapi_workbench-1.0.2-py3-none-any.whl"
    wheel.write_bytes(
        wheel_bytes(
            {
                "fastapi_workbench/middleware.py": b"""
class WorkbenchPathMiddleware:
    def __init__(self, app, *, absolute_redirects=False, absolute_origin=None):
        self.app = app
""",
            }
        )
    )
    parameters = artifacts.init_parameters_from_wheel(
        wheel, "fastapi_workbench.middleware", "WorkbenchPathMiddleware"
    )
    assert {"app", "absolute_redirects", "absolute_origin"} <= parameters


def test_published_parity_rejects_reused_version_with_changed_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    local = wheel_bytes({"package/__init__.py": b"current\n"})
    stale = wheel_bytes({"package/__init__.py": b"stale\n"})
    wheels: dict[str, Path] = {}
    versions = {name: "1.0.1" for name in artifacts.PAIR}
    for distribution in artifacts.PAIR:
        path = tmp_path / f"{distribution.replace('-', '_')}-1.0.1-py3-none-any.whl"
        path.write_bytes(local)
        wheels[distribution] = path

    def fake_published(distribution: str, version: str) -> tuple[str, bytes]:
        assert version == "1.0.1"
        payload = stale if distribution == "fastapi-workbench" else local
        return f"{distribution}-1.0.1-py3-none-any.whl", payload

    monkeypatch.setattr(artifacts, "published_wheel", fake_published)
    errors = artifacts.validate_published_parity(wheels, versions)
    assert len(errors) == 1
    assert "fastapi-workbench==1.0.1 already exists on PyPI" in errors[0]
    assert "bump the package version" in errors[0]
