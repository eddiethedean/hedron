#!/usr/bin/env python3
"""NATIVE-028: optional native acceleration Verified evidence."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

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
