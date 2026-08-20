"""REGRESS-054 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path


def test_regress_054_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.54.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["REGRESS-054"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0081-AUTHORING-LOOP-AND-CHROME.md").is_file()


def test_verify_pkg_53_still_present() -> None:
    assert Path("scripts/verify_pkg_53.py").is_file()
    assert Path("docs/acceptance/release-gate-0.53.toml").is_file()


def test_all_054_gates_verified_no_deferred() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.54.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    for gate_id, row in rows.items():
        assert row["state"] != "Deferred", gate_id
        assert row["state"] == "Verified", f"{gate_id}={row['state']}"


def test_boundaries_not_reopened() -> None:
    inventory = tomllib.loads(
        Path("docs/acceptance/authoring-loop-inventory-054.toml").read_text(encoding="utf-8")
    )
    bounds = inventory["boundaries"]
    assert bounds["reopen_polling_only"] is False
    assert bounds["replace_fleet_doctor"] is False
    assert bounds["public_notebook_hosting"] is False
    assert bounds["silent_sim_parity"] is False
    assert bounds["schedule_1_0"] is False


def test_authoring_loop_schema_stable() -> None:
    from hedron_conformance.authoring_loop import AUTHORING_LOOP_SCHEMA_VERSION

    assert AUTHORING_LOOP_SCHEMA_VERSION == "hedron-authoring-loop-1"


def test_fleet_still_not_package_doctor() -> None:
    from hedron.fleet import diagnose_installed_fleet

    report = diagnose_installed_fleet()
    assert report.get("package_doctor") is False
