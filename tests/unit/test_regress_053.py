"""REGRESS-053 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path


def test_regress_053_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.53.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["REGRESS-053"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md").is_file()


def test_verify_pkg_52_still_importable_path() -> None:
    path = Path("scripts/verify_pkg_52.py")
    assert path.is_file()
    assert Path("docs/acceptance/release-gate-0.52.toml").is_file()
    import importlib.util

    spec = importlib.util.spec_from_file_location("verify_pkg_52", path)
    assert spec is not None and spec.loader is not None
    assert "verify_pkg_52" in str(path)


def test_contract_version_still_portable_1() -> None:
    from hedron_conformance import CONTRACT_VERSION

    assert CONTRACT_VERSION == "hedron-portable-1"


def test_all_053_gates_verified_no_deferred() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.53.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    for gate_id, row in rows.items():
        assert row["state"] != "Deferred", gate_id
        assert row["state"] == "Verified", f"{gate_id}={row['state']}"


def test_polling_only_not_reopened() -> None:
    inventory = tomllib.loads(
        Path("docs/acceptance/application-dx-inventory-053.toml").read_text(encoding="utf-8")
    )
    assert inventory["boundaries"]["reopen_polling_only"] is False
    contracts = tomllib.loads(
        Path("docs/acceptance/application-contracts-053.toml").read_text(encoding="utf-8")
    )
    assert contracts["workflow"]["reopens_polling_only"] is False
    impl = Path("docs/implementation/APPLICATION_DX_053.md").read_text(encoding="utf-8")
    assert "polling_only" in impl
    assert "Do **not** reopen `polling_only`" in impl
