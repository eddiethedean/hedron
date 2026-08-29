#!/usr/bin/env python3
"""NATIVE-028: optional native acceleration Verified evidence."""

from __future__ import annotations

import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_028 import require_files, require_inventory_supported, run_pytest  # noqa: E402

WHEEL_EVIDENCE = ROOT / "docs" / "acceptance" / "native-wheels-028.toml"
FUZZ_EVIDENCE = ROOT / "docs" / "acceptance" / "native-fuzz-028" / "RESULT.log"
EXPECTED_TAGS = (
    "manylinux_x86_64",
    "manylinux_aarch64",
    "macosx_arm64",
    "win_amd64",
    "source_sdist",
)


def _check_wheel_evidence(errors: list[str]) -> None:
    if not WHEEL_EVIDENCE.is_file():
        errors.append(f"missing {WHEEL_EVIDENCE.relative_to(ROOT)}")
        return
    data = tomllib.loads(WHEEL_EVIDENCE.read_text(encoding="utf-8"))
    tags = set(data.get("supported_platform_tags") or [])
    missing = [tag for tag in EXPECTED_TAGS if tag not in tags]
    if missing:
        errors.append(f"native-wheels-028.toml missing tags: {missing}")
    if "wheels_macos_x86_64" in tags or "macosx_x86_64" in tags:
        errors.append("macOS x86_64 must not be claimed in Supported wheel evidence")
    workflow = (ROOT / ".github" / "workflows" / "native-wheels.yml").read_text(encoding="utf-8")
    if "publish-pypi:" not in workflow or "PYPI_API_TOKEN" not in workflow:
        errors.append("native-wheels.yml must publish cibuildwheel artifacts to PyPI")


def _check_pypi_wheel_tags(errors: list[str]) -> None:
    """Fail closed when enabled and PyPI is missing Supported wheel tags."""
    import json
    import urllib.error
    import urllib.request

    data = tomllib.loads(WHEEL_EVIDENCE.read_text(encoding="utf-8"))
    if not bool(data.get("require_pypi_wheels", False)):
        return

    pyproject = tomllib.loads(
        (ROOT / "packages" / "hedron-native" / "pyproject.toml").read_text(encoding="utf-8")
    )
    version = str(pyproject["project"]["version"])
    url = f"https://pypi.org/pypi/hedron-native/{version}/json"
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            payload = json.load(resp)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        errors.append(f"unable to query PyPI for hedron-native=={version}: {exc}")
        return
    filenames = [str(item.get("filename") or "") for item in payload.get("urls") or []]
    required = {
        "manylinux_x86_64": any(
            "manylinux" in name and "x86_64" in name and name.endswith(".whl") for name in filenames
        ),
        "manylinux_aarch64": any(
            "manylinux" in name and "aarch64" in name and name.endswith(".whl")
            for name in filenames
        ),
        "macosx_arm64": any(
            "macosx" in name and "arm64" in name and name.endswith(".whl") for name in filenames
        ),
        "win_amd64": any("win_amd64" in name and name.endswith(".whl") for name in filenames),
        "source_sdist": any(name.endswith(".tar.gz") for name in filenames),
    }
    missing = [tag for tag, ok in required.items() if not ok]
    if missing:
        errors.append(
            f"PyPI hedron-native=={version} missing Supported artifacts {missing}; "
            f"found={filenames or ['<none>']}"
        )


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "docs" / "packages" / "hedron-native.md",
            ROOT / "docs" / "acceptance" / "upgrade-fixtures-028.md",
            ROOT / "packages" / "hedron-native" / "src" / "hedron_native" / "__init__.py",
            ROOT / "tests" / "unit" / "test_native_fallback_028.py",
            ROOT / "tests" / "unit" / "test_native_parity.py",
            ROOT / "tests" / "unit" / "test_native_fuzz.py",
            WHEEL_EVIDENCE,
            FUZZ_EVIDENCE,
            ROOT / ".github" / "workflows" / "native-wheels.yml",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron-native",
        (
            "escape_text",
            "escape_attr",
            "wheels_manylinux_x86_64",
            "wheels_manylinux_aarch64",
            "wheels_macos_arm64",
            "wheels_windows_amd64",
            "source_builds",
            "fuzz_sanitizer_parity",
            "serialize_stage_benefit",
            "fallback_absence",
            "fallback_import_failure",
            "fallback_unsupported_platform",
            "fallback_runtime_disable",
        ),
        errors,
    )
    _check_wheel_evidence(errors)
    _check_pypi_wheel_tags(errors)
    native_docs = (ROOT / "docs" / "packages" / "hedron-native.md").read_text(encoding="utf-8")
    if "HEDRON_NATIVE_DISABLE" not in native_docs:
        errors.append("docs/packages/hedron-native.md must document HEDRON_NATIVE_DISABLE")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if run_pytest(
        [
            "tests/unit/test_native_fallback_028.py",
            "tests/unit/test_native_parity.py",
            "tests/unit/test_native_fuzz.py",
            "tests/unit/test_native_accel.py",
            "tests/performance/test_native_serialize_bench_028.py",
        ],
        "NATIVE-028",
    ):
        return 1
    print("ok: NATIVE-028 wheels/fallback/fuzz/serialize evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
