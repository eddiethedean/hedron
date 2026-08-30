"""Shared authoring-loop fixture and diagnostic contracts (phase 0.54)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal, cast

AUTHORING_LOOP_SCHEMA_VERSION = "hedron-authoring-loop-1"

# Deterministic failure codes (RFC-0081 / authoring-shared-054.toml)
HED_SIM_UNSUPPORTED = "HED-SIM-UNSUPPORTED"
HED_SIM_LIMIT = "HED-SIM-LIMIT"
HED_NOTEBOOK_TOPOLOGY = "HED-NOTEBOOK-TOPOLOGY"
HED_NOTEBOOK_TOKEN = "HED-NOTEBOOK-TOKEN"
HED_PACKAGE_DOCTOR = "HED-PACKAGE-DOCTOR"

FailureCode = Literal[
    "HED-SIM-UNSUPPORTED",
    "HED-SIM-LIMIT",
    "HED-NOTEBOOK-TOPOLOGY",
    "HED-NOTEBOOK-TOKEN",
    "HED-PACKAGE-DOCTOR",
]

Boundary = Literal[
    "sample_kit",
    "simulator",
    "notebook",
    "package_doctor",
    "real_server",
    "app_scenario",
]


def _empty_details() -> dict[str, Any]:
    return {}


@dataclass(frozen=True, slots=True)
class AuthoringLoopDiagnostic:
    """Machine-readable diagnostic that survives tool boundaries."""

    code: str
    message: str
    boundary: Boundary
    severity: Literal["error", "warning", "information"] = "error"
    details: dict[str, Any] = field(default_factory=_empty_details)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class AuthoringLoopFixture:
    """Shared fixture envelope for sample → sim → notebook → doctor."""

    fixture_id: str
    kind: str
    payload: dict[str, Any]
    schema_version: str = AUTHORING_LOOP_SCHEMA_VERSION
    diagnostics: tuple[AuthoringLoopDiagnostic, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "fixture_id": self.fixture_id,
            "kind": self.kind,
            "payload": dict(self.payload),
            "diagnostics": [d.to_dict() for d in self.diagnostics],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuthoringLoopFixture:
        version = str(data.get("schema_version") or AUTHORING_LOOP_SCHEMA_VERSION)
        raw_diagnostics = cast(list[dict[str, Any]], data.get("diagnostics") or [])
        diagnostics = tuple(
            AuthoringLoopDiagnostic(
                code=str(row["code"]),
                message=str(row["message"]),
                boundary=row["boundary"],  # type: ignore[arg-type]
                severity=row.get("severity", "error"),  # type: ignore[arg-type]
                details=dict(row.get("details") or {}),
            )
            for row in raw_diagnostics
        )
        return cls(
            fixture_id=str(data["fixture_id"]),
            kind=str(data["kind"]),
            payload=dict(data.get("payload") or {}),
            schema_version=version,
            diagnostics=diagnostics,
        )


def validate_fixture_schema(data: dict[str, Any]) -> list[AuthoringLoopDiagnostic]:
    """Return diagnostics when a fixture envelope is incomplete or version-skewed."""
    found: list[AuthoringLoopDiagnostic] = []
    version = str(data.get("schema_version") or "")
    if version != AUTHORING_LOOP_SCHEMA_VERSION:
        found.append(
            AuthoringLoopDiagnostic(
                code=HED_PACKAGE_DOCTOR,
                message=(
                    f"authoring-loop schema_version {version!r} != "
                    f"{AUTHORING_LOOP_SCHEMA_VERSION!r}"
                ),
                boundary="package_doctor",
                severity="error",
            )
        )
    for key in ("fixture_id", "kind", "payload"):
        if key not in data:
            found.append(
                AuthoringLoopDiagnostic(
                    code=HED_PACKAGE_DOCTOR,
                    message=f"authoring-loop fixture missing required field {key!r}",
                    boundary="package_doctor",
                    severity="error",
                )
            )
    return found


__all__ = [
    "AUTHORING_LOOP_SCHEMA_VERSION",
    "HED_NOTEBOOK_TOKEN",
    "HED_NOTEBOOK_TOPOLOGY",
    "HED_PACKAGE_DOCTOR",
    "HED_SIM_LIMIT",
    "HED_SIM_UNSUPPORTED",
    "AuthoringLoopDiagnostic",
    "AuthoringLoopFixture",
    "Boundary",
    "FailureCode",
    "validate_fixture_schema",
]
