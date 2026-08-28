#!/usr/bin/env python3
"""CONTRACT-030: dual-package production-grade inventory agrees with docs and install guards."""

from __future__ import annotations

import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-030.toml"
REQUIRED_PACKAGES = ("fastapi-workbench", "hedron-workbench")
REQUIRED_DOCS = (
    ROOT / "docs" / "api" / "STABILITY.md",
    ROOT / "docs" / "COMPATIBILITY.md",
    ROOT / "docs" / "guides" / "whats-ready.md",
    ROOT / "docs" / "packages" / "hedron-workbench.md",
    ROOT / "docs" / "guides" / "posit-workbench.md",
    ROOT / "docs" / "api" / "MOUNT.md",
    ROOT / "docs" / "rfcs" / "RFC-0063-FASTAPI-WORKBENCH-EXTRACTION.md",
    ROOT / "docs" / "acceptance" / "upgrade-fixtures-030.md",
    ROOT / "docs" / "acceptance" / "fastapi-workbench-provenance-030.toml",
    ROOT / "docs" / "acceptance" / "security-review-030" / "BRIEF.md",
    ROOT / "packages" / "fastapi-workbench" / "README.md",
    ROOT / "docs" / "DECISIONS.md",
)


def main() -> int:
    errors: list[str] = []
    if not INVENTORY.is_file():
        print(f"missing {INVENTORY.relative_to(ROOT)}", file=sys.stderr)
        return 1

    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    if data.get("baseline") != "v0.29.0":
        errors.append("inventory baseline must be v0.29.0")
    packages = data.get("packages")
    if packages != list(REQUIRED_PACKAGES):
        errors.append(f"packages must be {list(REQUIRED_PACKAGES)!r}, got {packages!r}")

    fwb = data.get("fastapi-workbench")
    if not isinstance(fwb, dict):
        errors.append("missing [fastapi-workbench] section")
    else:
        for key in ("supported", "experimental", "excluded"):
            value = fwb.get(key)
            if not isinstance(value, list) or not value:
                errors.append(f"fastapi-workbench.{key} must be a non-empty list")
        supported = set(fwb.get("supported") or [])
        for required in (
            "pure_resolver",
            "single_normalizer",
            "pre_import_launcher",
            "workbenchify_wrap_once",
            "fastapi_workbench_cli",
            "fastapi_run_and_factory",
        ):
            if required not in supported:
                errors.append(f"fastapi-workbench.supported must include {required}")
        excluded = set(fwb.get("excluded") or [])
        for required in ("hedron_dependency", "import_auto_activation", "bundle_rserver_url"):
            if required not in excluded:
                errors.append(f"fastapi-workbench.excluded must include {required}")

    hed = data.get("hedron-workbench")
    if not isinstance(hed, dict):
        errors.append("missing [hedron-workbench] section")
    else:
        for key in ("supported", "experimental", "excluded"):
            value = hed.get(key)
            if not isinstance(value, list) or not value:
                errors.append(f"hedron-workbench.{key} must be a non-empty list")
        supported = set(hed.get("supported") or [])
        for required in (
            "hedron_workbench_facade",
            "fastapi_workbench_delegation",
            "hedron_root_path_export",
            "cookie_path_at_construction",
        ):
            if required not in supported:
                errors.append(f"hedron-workbench.supported must include {required}")
        excluded = set(hed.get("excluded") or [])
        for required in (
            "duplicate_generic_resolver",
            "duplicate_generic_middleware",
            "duplicate_generic_runner",
        ):
            if required not in excluded:
                errors.append(f"hedron-workbench.excluded must include {required}")

    guards = data.get("install_guards") or {}
    for key in (
        "workbench_import_does_not_wrap",
        "fastapi_workbench_import_does_not_wrap",
        "inactive_facade_matches_hedron",
        "rs_server_url_does_not_activate",
        "flask_django_untouched",
        "reload_not_default",
        "multi_worker_not_default",
        "connect_header_not_default_trust",
        "fastapi_workbench_has_no_hedron_import",
        "hedron_workbench_declares_fastapi_workbench",
    ):
        if guards.get(key) is not True:
            errors.append(f"install_guards.{key} must be true")

    anchors = data.get("docs_anchors") or {}
    for key, rel in (
        ("stability", "docs/api/STABILITY.md"),
        ("compatibility", "docs/COMPATIBILITY.md"),
        ("whats_ready", "docs/guides/whats-ready.md"),
        ("workbench_package", "docs/packages/hedron-workbench.md"),
        ("workbench_guide", "docs/guides/posit-workbench.md"),
        ("mount_api", "docs/api/MOUNT.md"),
        ("rfc", "docs/rfcs/RFC-0063-FASTAPI-WORKBENCH-EXTRACTION.md"),
        ("fastapi_workbench_readme", "packages/fastapi-workbench/README.md"),
    ):
        if anchors.get(key) != rel:
            errors.append(f"docs_anchors.{key} must be {rel!r}")

    for path in REQUIRED_DOCS:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")

    decisions = (ROOT / "docs" / "DECISIONS.md").read_text(encoding="utf-8")
    if "| D-058 |" not in decisions:
        errors.append("docs/DECISIONS.md must contain D-058")
    rfc_index = (ROOT / "docs" / "rfcs" / "README.md").read_text(encoding="utf-8")
    if "RFC-0063" not in rfc_index and "0063" not in rfc_index:
        errors.append("docs/rfcs/README.md must index RFC-0063")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: CONTRACT-030 production-grade inventory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
