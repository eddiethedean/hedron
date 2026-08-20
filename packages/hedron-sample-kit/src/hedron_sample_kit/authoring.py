"""Shared authoring-loop fixture published by the sample kit (SAMPLE-054).

The fixture envelope is the same one consumed by the simulator, the notebook
preview, and ``hedron package doctor``. ``hedron-conformance`` is an optional
extra, so the import stays inside the function and the failure is explicit.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from hedron_sample_kit.variants import VARIANT_MODULES, list_variants

if TYPE_CHECKING:
    from hedron_conformance.authoring_loop import AuthoringLoopFixture

FIXTURE_ID = "hedron-sample-kit:authoring-loop"
FIXTURE_KIND = "authoring_loop_fixture"

__all__ = ["FIXTURE_ID", "FIXTURE_KIND", "authoring_fixture", "fixture_payload"]


def fixture_payload() -> dict[str, Any]:
    """Return the public facts the authoring loop carries across boundaries."""
    from hedron_sample_kit import __version__

    present = list_variants()
    return {
        "distribution": "hedron-sample-kit",
        "version": __version__,
        "plugin": "sample_kit",
        "entry_point": "hedron_sample_kit.plugin:register",
        "component": "hedron-sample-kit:callout.Callout",
        "examples": ["default"],
        "variants": list(present),
        "removable_variants": list(VARIANT_MODULES),
    }


def authoring_fixture() -> AuthoringLoopFixture:
    """Return the sample kit's shared authoring-loop fixture."""
    from hedron_conformance.authoring_loop import (
        HED_PACKAGE_DOCTOR,
        AuthoringLoopDiagnostic,
        AuthoringLoopFixture,
    )

    payload = fixture_payload()
    present = set(payload["variants"])
    diagnostics = tuple(
        AuthoringLoopDiagnostic(
            code=HED_PACKAGE_DOCTOR,
            message=f"sample-kit variant {name!r} is not installed",
            boundary="sample_kit",
            severity="information",
            details={"variant": name},
        )
        for name in VARIANT_MODULES
        if name not in present
    )
    return AuthoringLoopFixture(
        fixture_id=FIXTURE_ID,
        kind=FIXTURE_KIND,
        payload=payload,
        diagnostics=diagnostics,
    )
