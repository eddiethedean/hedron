"""Machine-readable AccessibilityContract (CONTRACT-019 / RFC-0051)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hedron_core.a11y.governance import Waiver
from hedron_core.registry import ComponentMeta, get_registry

__all__ = [
    "AccessibilityContract",
    "AccessibilityContractCatalog",
    "contract_for_registered",
    "default_contract",
]


@dataclass(frozen=True, slots=True)
class AccessibilityContract:
    """Leaf or package accessibility obligations — never implies app conformance."""

    component: str
    package: str = "hedron-core"
    native_semantics: str = ""
    aria_roles: tuple[str, ...] = ()
    name_sources: tuple[str, ...] = ()
    keyboard: str = ""
    focus: str = ""
    pointer_alternatives: str = ""
    target_reflow: str = ""
    announcements: str = ""
    alternatives: str = ""
    manual_checks: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    waivers: tuple[Waiver, ...] = ()
    dynamic_states: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    notes: str = ""

    def implies_application_conformance(self) -> bool:
        return False

    def as_dict(self) -> dict[str, Any]:
        return {
            "component": self.component,
            "package": self.package,
            "native_semantics": self.native_semantics,
            "aria_roles": list(self.aria_roles),
            "name_sources": list(self.name_sources),
            "keyboard": self.keyboard,
            "focus": self.focus,
            "pointer_alternatives": self.pointer_alternatives,
            "target_reflow": self.target_reflow,
            "announcements": self.announcements,
            "alternatives": self.alternatives,
            "manual_checks": list(self.manual_checks),
            "limitations": list(self.limitations),
            "waivers": [w.as_dict() for w in self.waivers],
            "dynamic_states": list(self.dynamic_states),
            "evidence": list(self.evidence),
            "notes": self.notes,
            "implies_application_conformance": False,
        }


def default_contract(
    name: str,
    *,
    package: str = "hedron-core",
    notes: str = "",
    native_semantics: str = "native HTML preferred",
) -> AccessibilityContract:
    return AccessibilityContract(
        component=name,
        package=package,
        native_semantics=native_semantics,
        keyboard="Documented per component; interactive controls are keyboard operable",
        focus="Visible focus; restore after HTMX swaps where applicable",
        notes=notes,
        evidence=("CONTRACT-019",),
    )


def contract_for_registered(
    meta: ComponentMeta, *, package: str = "hedron-core"
) -> AccessibilityContract:
    notes = meta.accessibility_notes or ""
    return default_contract(meta.name, package=package, notes=notes)


@dataclass
class AccessibilityContractCatalog:
    """Registry-driven catalog of public component contracts."""

    contracts: dict[str, AccessibilityContract] = field(default_factory=dict)
    package: str = "hedron-core"

    def register(self, contract: AccessibilityContract) -> None:
        self.contracts[contract.component] = contract

    def ensure_registry(self, *, package: str | None = None) -> None:
        pkg = package or self.package
        for meta in get_registry().components():
            if meta.name not in self.contracts:
                self.register(contract_for_registered(meta, package=pkg))

    def missing(self) -> list[str]:
        registered = {meta.name for meta in get_registry().components()}
        return sorted(registered - set(self.contracts))

    def assert_complete(self) -> None:
        self.ensure_registry()
        missing = self.missing()
        if missing:
            raise AssertionError(f"Missing AccessibilityContract for: {missing[:20]}")

    def compose(self, *names: str) -> AccessibilityContract:
        """Composition may accumulate unmet obligations; never claims conformance."""
        parts = [self.contracts[n] for n in names if n in self.contracts]
        if not parts:
            raise KeyError(f"No contracts for {names!r}")
        notes = " | ".join(p.notes for p in parts if p.notes)
        limitations = tuple(dict.fromkeys(lim for p in parts for lim in p.limitations))
        return AccessibilityContract(
            component="+".join(p.component for p in parts),
            package=parts[0].package,
            native_semantics="; ".join(p.native_semantics for p in parts if p.native_semantics),
            limitations=limitations,
            notes=notes,
            evidence=("CONTRACT-019", "composed"),
        )
