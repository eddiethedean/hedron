"""Visible, structured compatibility warnings for the 0.67 to 1.0 bridge."""

from __future__ import annotations

import inspect
import warnings
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Final

__all__ = [
    "FutureWarningRegistry",
    "HedronFutureWarning",
    "FutureWarningRecord",
    "PUBLIC_FUTURE_WARNINGS",
    "emit_future_warning",
    "warn_legacy_path",
]

FUTURE_WARNING_SCHEMA: Final = "hedron.future-warning/1"


class HedronFutureWarning(UserWarning):
    """Visible-by-default warning for a public path removed in Hedron 1.0."""


@dataclass(frozen=True, slots=True)
class FutureWarningRecord:
    """Structured warning metadata shared by runtime and static tooling."""

    code: str
    old_path: str
    replacement: str
    owner: str
    first_warning_version: str = "0.67"
    removal_version: str = "1.0"
    source: str = ""
    documentation: str = ""
    fixture: str = ""
    confidence: str = "complete"
    automation_status: str = "manual-review"

    def __post_init__(self) -> None:
        for name in ("code", "old_path", "owner", "replacement"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} is required")
        if self.confidence not in {"complete", "partial", "unknown"}:
            raise ValueError("confidence must be complete, partial, or unknown")
        if self.automation_status not in {"automatic", "manual-review", "not-applicable"}:
            raise ValueError("invalid automation_status")

    def to_dict(self) -> dict[str, str]:
        return {
            "schema": FUTURE_WARNING_SCHEMA,
            "code": self.code,
            "old_path": self.old_path,
            "replacement": self.replacement,
            "owner": self.owner,
            "first_warning_version": self.first_warning_version,
            "removal_version": self.removal_version,
            "source": self.source,
            "documentation": self.documentation,
            "fixture": self.fixture,
            "confidence": self.confidence,
            "automation_status": self.automation_status,
        }

    def message(self) -> str:
        return (
            f"{self.code}: {self.old_path} is transitional in Hedron {self.first_warning_version} "
            f"and is removed in {self.removal_version}; use {self.replacement}. "
            f"Confidence: {self.confidence}."
        )


class FutureWarningRegistry:
    """Deterministic registry for runtime and static target-version findings."""

    def __init__(self, records: Iterable[FutureWarningRecord] = ()) -> None:
        self._records: dict[str, FutureWarningRecord] = {}
        for record in records:
            self.register(record)

    def register(self, record: object) -> FutureWarningRecord:
        candidate = record
        if not isinstance(candidate, FutureWarningRecord):
            raise TypeError("warning registry accepts FutureWarningRecord values")
        prior = self._records.get(candidate.code)
        if prior is not None and prior != candidate:
            raise ValueError(f"warning code {candidate.code!r} is already registered")
        self._records[candidate.code] = candidate
        return candidate

    def get(self, code: str) -> FutureWarningRecord | None:
        return self._records.get(code)

    def for_path(self, old_path: str) -> tuple[FutureWarningRecord, ...]:
        return tuple(record for record in self._records.values() if record.old_path == old_path)

    def emit(self, code: str, *, stacklevel: int = 2) -> None:
        record = self.get(code)
        if record is None:
            raise KeyError(code)
        emit_future_warning(record, stacklevel=stacklevel)

    def records(self) -> tuple[FutureWarningRecord, ...]:
        return tuple(self._records[key] for key in sorted(self._records))

    def to_dict(self) -> list[dict[str, str]]:
        return [record.to_dict() for record in self.records()]

    def validate(self, *, root: str | Path | None = None) -> tuple[str, ...]:
        """Return deterministic registry issues without mutating the registry.

        A release gate can use this check before deleting a path.  Missing
        documentation/fixture metadata is an error even when the runtime
        warning itself is otherwise valid.
        """
        base = Path(root).resolve() if root is not None else None
        issues: list[str] = []
        seen_paths: dict[str, str] = {}
        for record in self.records():
            previous = seen_paths.get(record.old_path)
            if previous is not None and previous != record.code:
                issues.append(f"{record.old_path}: registered by both {previous} and {record.code}")
            seen_paths[record.old_path] = record.code
            for field in ("source", "documentation", "fixture"):
                value = getattr(record, field)
                if not value.strip():
                    issues.append(f"{record.code}: missing {field}")
                elif (
                    base is not None
                    and field in {"documentation", "fixture"}
                    and not (base / value).is_file()
                ):
                    issues.append(f"{record.code}: {field} does not exist: {value}")
        return tuple(sorted(set(issues)))


PUBLIC_FUTURE_WARNINGS = FutureWarningRegistry(
    (
        FutureWarningRecord(
            code="HED-MIGRATE-0671",
            old_path="app.component",
            replacement="app.view",
            owner="hedron.routing",
            source="contract-freeze-067.toml",
            documentation="docs/rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md",
            fixture="tests/upgrade/shared.py",
            automation_status="automatic",
        ),
        FutureWarningRecord(
            code="HED-MIGRATE-0672",
            old_path="app.fragment",
            replacement="app.view",
            owner="hedron.routing",
            source="contract-freeze-067.toml",
            documentation="docs/rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md",
            fixture="tests/upgrade/shared.py",
            automation_status="automatic",
        ),
        FutureWarningRecord(
            code="HED-MIGRATE-0673",
            old_path="app.include_feature",
            replacement="app.include",
            owner="hedron.app",
            source="contract-freeze-067.toml",
            documentation="docs/rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md",
            fixture="tests/upgrade/shared.py",
            automation_status="automatic",
        ),
        FutureWarningRecord(
            code="HED-MIGRATE-0674",
            old_path="router.component",
            replacement="router.view",
            owner="hedron.routing",
            source="contract-freeze-067.toml",
            documentation="docs/rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md",
            fixture="tests/upgrade/shared.py",
            automation_status="automatic",
        ),
        FutureWarningRecord(
            code="HED-MIGRATE-0675",
            old_path="app.screen",
            replacement="app.page",
            owner="hedron.app",
            source="contract-freeze-067.toml",
            documentation="docs/rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md",
            fixture="tests/upgrade/shared.py",
            confidence="partial",
            automation_status="manual-review",
        ),
        FutureWarningRecord(
            code="HED-MIGRATE-0676",
            old_path="app.refreshable",
            replacement="app.view",
            owner="hedron.app",
            source="contract-freeze-067.toml",
            documentation="docs/rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md",
            fixture="tests/upgrade/shared.py",
            confidence="partial",
            automation_status="manual-review",
        ),
        FutureWarningRecord(
            code="HED-MIGRATE-0677",
            old_path="app.command",
            replacement="app.action",
            owner="hedron.app",
            source="contract-freeze-067.toml",
            documentation="docs/rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md",
            fixture="tests/upgrade/shared.py",
            confidence="partial",
            automation_status="manual-review",
        ),
        FutureWarningRecord(
            code="HED-MIGRATE-0678",
            old_path="app.form_command",
            replacement="app.action",
            owner="hedron.app",
            source="contract-freeze-067.toml",
            documentation="docs/rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md",
            fixture="tests/upgrade/shared.py",
            confidence="partial",
            automation_status="manual-review",
        ),
        FutureWarningRecord(
            code="HED-MIGRATE-0679",
            old_path="flask.component",
            replacement="flask.view",
            owner="hedron-flask",
            source="contract-freeze-067.toml",
            documentation="docs/rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md",
            fixture="tests/upgrade/phase_1_0/transitional/flask_component.py",
            confidence="complete",
            automation_status="automatic",
        ),
        FutureWarningRecord(
            code="HED-MIGRATE-0680",
            old_path="blueprint.component",
            replacement="blueprint.view",
            owner="hedron-flask",
            source="contract-freeze-067.toml",
            documentation="docs/rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md",
            fixture="tests/upgrade/phase_1_0/transitional/blueprint_component.py",
            confidence="complete",
            automation_status="automatic",
        ),
        FutureWarningRecord(
            code="HED-MIGRATE-0681",
            old_path="blueprint.include_feature",
            replacement="blueprint.include",
            owner="hedron-flask",
            source="contract-freeze-067.toml",
            documentation="docs/rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md",
            fixture="tests/upgrade/phase_1_0/transitional/blueprint_include_feature.py",
            confidence="complete",
            automation_status="automatic",
        ),
    )
)


def emit_future_warning(record: FutureWarningRecord, *, stacklevel: int = 2) -> None:
    """Emit a visible compatibility warning carrying the structured record."""
    warning = HedronFutureWarning(record.message())
    warning.record = record  # type: ignore[attr-defined]
    warnings.warn(warning, stacklevel=stacklevel)


def warn_legacy_path(path: str, *, stacklevel: int = 2) -> None:
    """Emit the registered warning for a documented transitional public path."""
    record = next(iter(PUBLIC_FUTURE_WARNINGS.for_path(path)), None)
    if record is None:
        raise KeyError(path)
    # Framework-owned helpers can invoke transitional decorators while
    # assembling a workspace.  Those are implementation details rather than
    # application compatibility sites, so do not emit duplicate warnings for
    # them.  ``emit_future_warning`` adds one call frame of its own; account
    # for both helpers so direct application calls point at their source.
    package_roots = ("/packages/hedron/", "/packages/hedron-core/", "/packages/hedron-data/")
    frames = inspect.stack(context=0)
    caller = frames[stacklevel] if len(frames) > stacklevel else None
    if caller is not None:
        filename = caller.filename.replace("\\", "/")
        module = str(caller.frame.f_globals.get("__package__", ""))
        framework_module = module in {"hedron", "hedron_core", "hedron_data"} or module.startswith(
            ("hedron.", "hedron_core.", "hedron_data.")
        )
        if framework_module or any(root in filename for root in package_roots):
            return
    emit_future_warning(record, stacklevel=stacklevel + 2)
