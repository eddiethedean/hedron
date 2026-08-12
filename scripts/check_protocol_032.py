#!/usr/bin/env python3
"""PROTOCOL-032: MCP protocol/SDK matrix + Streamable HTTP evidence."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_032 import (  # noqa: E402
    fail_errors,
    require_files,
    require_inventory_supported,
    run_pytest,
)


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "packages" / "hedron-mcp" / "src" / "hedron_mcp" / "compat.py",
            ROOT / "packages" / "hedron-mcp" / "src" / "hedron_mcp" / "transport.py",
            ROOT / "packages" / "hedron-mcp" / "src" / "hedron_mcp" / "server.py",
            ROOT / "docs" / "acceptance" / "upgrade-fixtures-032.md",
            ROOT / "tests" / "unit" / "test_protocol_032.py",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron-mcp",
        (
            "deny_by_default_streamable_http_mount",
            "explicit_resource_registration",
            "explicit_tool_registration",
            "fail_closed_empty_mount",
            "read_resources",
            "read_only_tools",
        ),
        errors,
    )
    pyproject = (
        ROOT / "packages" / "hedron-mcp" / "pyproject.toml"
    ).read_text(encoding="utf-8")
    if "mcp" not in pyproject:
        errors.append("hedron-mcp pyproject must pin official mcp SDK")
    if fail_errors(errors, "PROTOCOL-032"):
        return 1
    return run_pytest(
        [
            "tests/unit/test_protocol_032.py",
            "tests/unit/test_phase17_mcp.py",
        ],
        "PROTOCOL-032",
    )


if __name__ == "__main__":
    raise SystemExit(main())
