#!/usr/bin/env python3
"""AUTHZ-032: host authn reuse + app authz/tenant fail-closed evidence."""

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
            ROOT / "packages" / "hedron-mcp" / "src" / "hedron_mcp" / "server.py",
            ROOT / "tests" / "security" / "test_mcp_adversarial.py",
            ROOT / "tests" / "unit" / "test_authz_032.py",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron-mcp",
        (
            "host_authn_reuse",
            "app_owned_authz_hooks",
            "app_owned_tenant_hooks",
        ),
        errors,
    )
    if fail_errors(errors, "AUTHZ-032"):
        return 1
    return run_pytest(
        [
            "tests/unit/test_authz_032.py",
            "tests/security/test_mcp_adversarial.py",
        ],
        "AUTHZ-032",
    )


if __name__ == "__main__":
    raise SystemExit(main())
