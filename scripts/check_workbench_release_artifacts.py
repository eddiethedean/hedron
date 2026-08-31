#!/usr/bin/env python3
"""Verify the built Workbench package pair and immutable PyPI artifact parity.

This check deliberately reads and installs wheels from ``dist/``. Importing the
workspace source tree cannot detect a stale wheel that has already been uploaded
under the same immutable version.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import tomllib
import urllib.error
import urllib.request
import zipfile
from collections.abc import Iterable
from email.parser import BytesParser
from email.policy import default
from pathlib import Path

from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parents[1]
PAIR = ("fastapi-workbench", "hedron-posit")
PYPI_JSON = "https://pypi.org/pypi/{name}/{version}/json"


def project_version(distribution: str) -> str:
    data = tomllib.loads(
        (ROOT / "packages" / distribution / "pyproject.toml").read_text(encoding="utf-8")
    )
    return str(data["project"]["version"])


def find_wheel(dist_dir: Path, distribution: str, version: str) -> Path:
    stem = distribution.replace("-", "_")
    matches = sorted(dist_dir.glob(f"{stem}-{version}-*.whl"))
    pure = [path for path in matches if path.name.endswith("-py3-none-any.whl")]
    candidates = pure or matches
    if len(candidates) != 1:
        found = ", ".join(path.name for path in candidates) or "none"
        raise ValueError(
            f"expected one {distribution}=={version} wheel in {dist_dir}; found {found}"
        )
    return candidates[0].resolve()


def wheel_metadata(path: Path) -> object:
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(names) != 1:
            raise ValueError(f"{path.name}: expected one METADATA entry")
        return BytesParser(policy=default).parsebytes(archive.read(names[0]))


def init_parameters_from_wheel(path: Path, module: str, class_name: str) -> set[str]:
    member = module.replace(".", "/") + ".py"
    with zipfile.ZipFile(path) as archive:
        try:
            source = archive.read(member).decode("utf-8")
        except KeyError as exc:
            raise ValueError(f"{path.name}: missing {member}") from exc
    tree = ast.parse(source, filename=f"{path.name}:{member}")
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if (
                    isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and item.name == "__init__"
                ):
                    return {argument.arg for argument in (*item.args.args, *item.args.kwonlyargs)}
    raise ValueError(f"{path.name}: missing {class_name}.__init__")


def validate_pair_contract(wheels: dict[str, Path], versions: dict[str, str]) -> list[str]:
    errors: list[str] = []
    middleware_parameters = init_parameters_from_wheel(
        wheels["fastapi-workbench"],
        "fastapi_workbench.middleware",
        "WorkbenchPathMiddleware",
    )
    required_parameters = {"absolute_redirects", "absolute_origin"}
    missing = sorted(required_parameters - middleware_parameters)
    if missing:
        errors.append(
            f"{wheels['fastapi-workbench'].name}: WorkbenchPathMiddleware.__init__ "
            f"is missing {', '.join(missing)}"
        )

    metadata = wheel_metadata(wheels["hedron-posit"])
    requirements = [Requirement(value) for value in metadata.get_all("Requires-Dist", [])]
    workbench = [item for item in requirements if item.name.lower() == "fastapi-workbench"]
    if len(workbench) != 1:
        errors.append(f"{wheels['hedron-posit'].name}: expected one fastapi-workbench requirement")
    elif not workbench[0].specifier.contains(versions["fastapi-workbench"], prereleases=True):
        errors.append(
            f"{wheels['hedron-posit'].name}: requirement {workbench[0]} does not accept "
            f"the built fastapi-workbench=={versions['fastapi-workbench']} wheel"
        )
    return errors


def comparable_wheel_payload(raw: bytes) -> dict[str, str]:
    """Return runtime payload and dependency metadata hashes, excluding build records."""
    payload: dict[str, str] = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for name in sorted(archive.namelist()):
            if name.endswith("/"):
                continue
            if ".dist-info/" in name and not name.endswith(".dist-info/METADATA"):
                continue
            payload[name] = hashlib.sha256(archive.read(name)).hexdigest()
    return payload


def published_wheel(distribution: str, version: str) -> tuple[str, bytes] | None:
    url = PYPI_JSON.format(name=distribution, version=version)
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            release = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    candidates = [
        item
        for item in release.get("urls", [])
        if item.get("packagetype") == "bdist_wheel"
        and str(item.get("filename", "")).endswith("-py3-none-any.whl")
    ]
    if len(candidates) != 1:
        raise ValueError(
            f"PyPI {distribution}=={version}: expected one py3-none-any wheel, "
            f"found {len(candidates)}"
        )
    candidate = candidates[0]
    with urllib.request.urlopen(str(candidate["url"]), timeout=30) as response:
        raw = response.read()
    expected = str(candidate.get("digests", {}).get("sha256", ""))
    actual = hashlib.sha256(raw).hexdigest()
    if not expected or actual != expected:
        raise ValueError(
            f"PyPI {distribution}=={version}: downloaded wheel hash does not match JSON metadata"
        )
    return str(candidate["filename"]), raw


def validate_published_parity(wheels: dict[str, Path], versions: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for distribution in PAIR:
        published = published_wheel(distribution, versions[distribution])
        if published is None:
            print(
                f"ok: {distribution}=={versions[distribution]} is not yet on PyPI; "
                "the built wheel is a new immutable artifact"
            )
            continue
        filename, public_raw = published
        local_raw = wheels[distribution].read_bytes()
        local_payload = comparable_wheel_payload(local_raw)
        public_payload = comparable_wheel_payload(public_raw)
        if local_payload != public_payload:
            changed = sorted(
                name
                for name in set(local_payload) | set(public_payload)
                if local_payload.get(name) != public_payload.get(name)
            )
            errors.append(
                f"{distribution}=={versions[distribution]} already exists on PyPI but its "
                f"immutable wheel differs from the release candidate ({filename}); bump the "
                f"package version. Changed payload: {', '.join(changed[:8])}"
            )
        else:
            print(
                f"ok: {distribution}=={versions[distribution]} candidate matches its "
                "immutable PyPI runtime payload"
            )
    return errors


def run_installed_smoke(wheels: dict[str, Path], dist_dir: Path) -> None:
    versions = {name: project_version(name) for name in ("hedron-core", "hedron", *PAIR)}
    install_wheels = [find_wheel(dist_dir, name, version) for name, version in versions.items()]
    with tempfile.TemporaryDirectory(prefix="hedron-workbench-wheels-") as raw_tmp:
        tmp = Path(raw_tmp)
        environment = tmp / ".venv"
        subprocess.run(
            ["uv", "venv", str(environment), "--python", sys.executable],
            check=True,
            cwd=tmp,
        )
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run(
            [
                "uv",
                "pip",
                "install",
                "--refresh",
                "--python",
                str(python),
                *(str(path) for path in install_wheels),
            ],
            check=True,
            cwd=tmp,
        )
        code = (
            """
import importlib.metadata as metadata
import inspect

from fastapi_workbench.middleware import WorkbenchPathMiddleware
from hedron_posit import HedronPosit

parameters = inspect.signature(WorkbenchPathMiddleware.__init__).parameters
assert "absolute_redirects" in parameters
assert "absolute_origin" in parameters
app = HedronPosit(title="wheel smoke", session_secret="artifact-smoke-secret")
assert app.routes
assert app.hedron_workbench.browser_mount == "/s/session/p/8000"
assert app.hedron_workbench.external_origin == "https://workbench.example"
assert metadata.version("fastapi-workbench") == """
            + repr(versions["fastapi-workbench"])
            + """
assert metadata.version("hedron-posit") == """
            + repr(versions["hedron-posit"])
            + """
"""
        )
        env = os.environ.copy()
        env.update(
            {
                "RS_SERVER_URL": "http://127.0.0.1:8787/",
                "UVICORN_ROOT_PATH": "https://workbench.example/s/session/p/8000/",
            }
        )
        subprocess.run([str(python), "-c", code], check=True, cwd=tmp, env=env)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist-dir", type=Path, default=ROOT / "dist")
    parser.add_argument(
        "--skip-published-parity",
        action="store_true",
        help="Run only local wheel contract/install checks (offline development use)",
    )
    args = parser.parse_args(argv)
    dist_dir = args.dist_dir.resolve()
    versions = {name: project_version(name) for name in PAIR}
    try:
        wheels = {name: find_wheel(dist_dir, name, versions[name]) for name in PAIR}
        errors = validate_pair_contract(wheels, versions)
        if not args.skip_published_parity:
            errors.extend(validate_published_parity(wheels, versions))
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        run_installed_smoke(wheels, dist_dir)
    except (OSError, ValueError, subprocess.CalledProcessError, urllib.error.URLError) as exc:
        print(f"workbench release artifact check failed: {exc}", file=sys.stderr)
        return 1
    print("ok: built Workbench wheels satisfy metadata, API, install, and PyPI parity checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
