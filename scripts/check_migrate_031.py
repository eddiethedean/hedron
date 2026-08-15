#!/usr/bin/env python3
"""MIGRATE-031: Streamlit AST migrator gate (RFC-0061)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_031 import (  # noqa: E402
    fail_errors,
    require_dirs,
    require_files,
    require_inventory_supported,
    run_pytest,
)

MIGRATE_PKG = ROOT / "packages" / "hedron" / "src" / "hedron" / "migrate"


def main() -> int:
    errors: list[str] = []
    require_dirs(
        [
            MIGRATE_PKG,
            MIGRATE_PKG / "registry",
            ROOT / "tests" / "fixtures" / "migrate_streamlit" / "sales_dashboard",
            ROOT / "tests" / "unit" / "migrate_streamlit",
        ],
        errors,
    )
    require_files(
        [
            MIGRATE_PKG / "__init__.py",
            MIGRATE_PKG / "cli.py",
            MIGRATE_PKG / "discovery.py",
            MIGRATE_PKG / "parse.py",
            MIGRATE_PKG / "resolve.py",
            MIGRATE_PKG / "ir.py",
            MIGRATE_PKG / "analyze.py",
            MIGRATE_PKG / "findings.py",
            MIGRATE_PKG / "report.py",
            MIGRATE_PKG / "generate.py",
            MIGRATE_PKG / "source_map.py",
            MIGRATE_PKG / "pins.py",
            MIGRATE_PKG / "limits.py",
            MIGRATE_PKG / "registry" / "catalog.py",
            MIGRATE_PKG / "registry" / "data" / "supported_symbols.toml",
            ROOT
            / "tests"
            / "fixtures"
            / "migrate_streamlit"
            / "sales_dashboard"
            / "streamlit_app.py",
            ROOT / "examples" / "streamlit-migration" / "app.py",
            ROOT / "docs" / "guides" / "streamlit-migration-matrix.md",
            ROOT / "packages" / "hedron-core" / "src" / "hedron_core" / "codes.py",
            ROOT / "docs" / "guides" / "error-codes.md",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron",
        (
            "migrate_streamlit_cli",
            "non_executing_ast_inventory",
            "versioned_mapping_report_schema",
            "secure_scaffold_generation",
            "source_maps_and_findings",
        ),
        errors,
    )

    # Codes + docs alignment for HED-MIG-ST-*
    codes = (ROOT / "packages" / "hedron-core" / "src" / "hedron_core" / "codes.py").read_text(
        encoding="utf-8"
    )
    docs = (ROOT / "docs" / "guides" / "error-codes.md").read_text(encoding="utf-8")
    for code in (
        "HED-MIG-ST-0001",
        "HED-MIG-ST-0002",
        "HED-MIG-ST-0012",
        "HED-MIG-ST-0014",
    ):
        if code not in codes:
            errors.append(f"codes.py missing {code}")
        if code not in docs:
            errors.append(f"error-codes.md missing {code}")

    cli = (ROOT / "packages" / "hedron" / "src" / "hedron" / "cli" / "parser.py").read_text(
        encoding="utf-8"
    )
    if "migrate" not in cli or "build_streamlit_parser" not in cli:
        errors.append("hedron.cli missing migrate streamlit wiring")

    if fail_errors(errors, "MIGRATE-031"):
        return 1

    paths = [
        "tests/unit/migrate_streamlit",
        "tests/integration/migrate_streamlit",
    ]
    if run_pytest(paths, "MIGRATE-031"):
        return 1

    # Hed codes registration must still pass with multi-segment MIG-ST codes.
    from _gate_031 import run_script

    if run_script("scripts/check_hed_codes.py", "MIGRATE-031 hed-codes", "--docs-align"):
        return 1

    print("ok: MIGRATE-031")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
