"""Machine-readable AccessibilityContract (CONTRACT-019 / RFC-0051)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hedron_core.a11y.governance import Waiver
from hedron_core.registry import ComponentMeta, get_registry

__all__ = [
    "REQUIRED_REVIEWED_CONTRACTS",
    "AccessibilityContract",
    "AccessibilityContractCatalog",
    "contract_for_registered",
    "default_contract",
    "reviewed_contract",
    "seed_reviewed_contracts",
]

# Curated surfaces that must carry reviewed=True contracts at cut (CONTRACT-019).
REQUIRED_REVIEWED_CONTRACTS = frozenset(
    {
        "Page",
        "Header",
        "Main",
        "Nav",
        "Aside",
        "Footer",
        "Section",
        "Form",
        "FormField",
        "TextInput",
        "TextArea",
        "Button",
        "SubmitButton",
        "Label",
        "Dialog",
        "ChatMessage",
        "HtmxLink",
        "Link",
        "Image",
        "Audio",
        "Video",
    }
)

_LANDMARK_SEMANTICS = {
    "Header": "native <header> landmark",
    "Main": "native <main> landmark",
    "Nav": "native <nav> landmark",
    "Aside": "native <aside> landmark",
    "Footer": "native <footer> landmark",
    "Section": "native <section> landmark",
}


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
    reviewed: bool = False

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
            "reviewed": self.reviewed,
            "implies_application_conformance": False,
        }


def default_contract(
    name: str,
    *,
    package: str = "hedron-core",
    notes: str = "",
    native_semantics: str = "native HTML preferred",
    reviewed: bool = False,
) -> AccessibilityContract:
    return AccessibilityContract(
        component=name,
        package=package,
        native_semantics=native_semantics,
        keyboard="Documented per component; interactive controls are keyboard operable",
        focus="Visible focus; restore after HTMX swaps where applicable",
        notes=notes,
        evidence=("CONTRACT-019",),
        reviewed=reviewed,
    )


def reviewed_contract(
    name: str,
    *,
    package: str = "hedron-core",
    native_semantics: str = "",
    keyboard: str = "",
    focus: str = "",
    name_sources: tuple[str, ...] = (),
    notes: str = "",
    limitations: tuple[str, ...] = (),
    aria_roles: tuple[str, ...] = (),
) -> AccessibilityContract:
    """Curated contract marked reviewed for CONTRACT-019 completeness."""
    return AccessibilityContract(
        component=name,
        package=package,
        native_semantics=native_semantics or "native HTML preferred",
        keyboard=keyboard or "Keyboard operable via native control semantics",
        focus=focus or "Visible focus; restore after HTMX swaps where applicable",
        name_sources=name_sources,
        aria_roles=aria_roles,
        notes=notes,
        limitations=limitations,
        evidence=("CONTRACT-019", "reviewed"),
        reviewed=True,
    )


def contract_for_registered(
    meta: ComponentMeta, *, package: str = "hedron-core"
) -> AccessibilityContract:
    notes = meta.accessibility_notes or ""
    return default_contract(meta.name, package=package, notes=notes, reviewed=False)


def _curated_for(name: str, *, package: str) -> AccessibilityContract:
    if name in _LANDMARK_SEMANTICS:
        return reviewed_contract(
            name,
            package=package,
            native_semantics=_LANDMARK_SEMANTICS[name],
            keyboard="Landmarks participate in browser landmark navigation",
            focus="Not focusable by default; children receive focus",
            notes="LANDMARK-019: allowlisted safe attrs; hostile roles rejected",
            limitations=("Do not override landmark role with presentation/none",),
        )
    if name == "Page":
        return reviewed_contract(
            name,
            package=package,
            native_semantics="html/lang/dir document shell",
            keyboard="Document order defines Tab order",
            focus="Skip links and landmarks recommended in body",
            notes="SCRIPT-019: Page(scripts=) allowlisted same-origin ASSET SafeUrl only",
            limitations=("Page scripts are progressive enhancement; app must work without them",),
        )
    if name in {"Form", "FormField", "TextInput", "TextArea", "Label", "SubmitButton"}:
        return reviewed_contract(
            name,
            package=package,
            native_semantics="native form controls / labels",
            keyboard="Native form keyboard behavior",
            focus="Visible focus on controls; associate Label via for_/id",
            name_sources=("label", "aria-label", "aria-labelledby"),
            notes="PE-019: no-JS POST / full document path alongside HTMX",
        )
    if name == "Button":
        return reviewed_contract(
            name,
            package=package,
            native_semantics="native <button>",
            keyboard="Enter/Space activate",
            focus="Visible focus ring",
            name_sources=("text content", "aria-label"),
        )
    if name == "Dialog":
        return reviewed_contract(
            name,
            package=package,
            native_semantics="native <dialog>",
            keyboard="Escape / formmethod=dialog close; Tab within dialog",
            focus="Focus moves into dialog when shown; restore on close (app/browser)",
            name_sources=("aria-labelledby title",),
            aria_roles=("dialog",),
            notes="aria-modal when modal=True; title wired via aria-labelledby",
        )
    if name == "ChatMessage":
        return reviewed_contract(
            name,
            package=package,
            native_semantics="article/region for chat turns",
            keyboard="Content is readable in DOM order",
            focus="Not independently focusable unless interactive children present",
            name_sources=("role status text",),
        )
    if name in {"HtmxLink", "Link"}:
        return reviewed_contract(
            name,
            package=package,
            native_semantics="native <a> with SafeUrl",
            keyboard="Enter activates; HTMX enhances when available",
            focus="Visible focus",
            name_sources=("link text", "aria-label"),
            notes="Progressive enhancement: href works without JS",
        )
    if name == "Image":
        return reviewed_contract(
            name,
            package=package,
            native_semantics="native <img>",
            keyboard="N/A (non-interactive)",
            focus="Not focusable",
            name_sources=("alt",),
            limitations=("Authors must supply meaningful alt or empty alt for decorative",),
        )
    if name in {"Audio", "Video"}:
        return AccessibilityContract(
            component=name,
            package=package,
            native_semantics=f"native <{name.lower()}>",
            keyboard="Native media controls when controls=True",
            focus="Controls receive focus when present",
            alternatives="Captions/transcripts via MediaTrackContract (MEDIA-019)",
            limitations=("Authors must supply text alternatives for media",),
            evidence=("CONTRACT-019", "reviewed"),
            reviewed=True,
        )
    return reviewed_contract(name, package=package, notes=f"Reviewed family default for {name}")


def seed_reviewed_contracts(
    catalog: AccessibilityContractCatalog,
    *,
    package: str | None = None,
    names: frozenset[str] | None = None,
) -> None:
    """Register reviewed contracts for the curated REQUIRED set (and optional extras)."""
    pkg = package or catalog.package
    target = names or REQUIRED_REVIEWED_CONTRACTS
    for name in sorted(target):
        catalog.register(_curated_for(name, package=pkg))


@dataclass
class AccessibilityContractCatalog:
    """Registry-driven catalog of public component contracts."""

    contracts: dict[str, AccessibilityContract] = field(
        default_factory=dict[str, AccessibilityContract]
    )
    package: str = "hedron-core"

    def register(self, contract: AccessibilityContract) -> None:
        self.contracts[contract.component] = contract

    def ensure_registry(self, *, package: str | None = None) -> None:
        """Fill missing names with unreviewed stubs (Explorer / eject convenience)."""
        pkg = package or self.package
        for meta in get_registry().components():
            if meta.name not in self.contracts:
                self.register(contract_for_registered(meta, package=pkg))

    def missing(self) -> list[str]:
        registered = {meta.name for meta in get_registry().components()}
        return sorted(registered - set(self.contracts))

    def unreviewed(self, required: frozenset[str] | None = None) -> list[str]:
        need = required if required is not None else REQUIRED_REVIEWED_CONTRACTS
        bad: list[str] = []
        for name in sorted(need):
            contract = self.contracts.get(name)
            if contract is None or not contract.reviewed:
                bad.append(name)
        return bad

    def assert_complete(self, *, require_reviewed: frozenset[str] | None = None) -> None:
        """Fail if registry names lack contracts or required contracts are unreviewed.

        Does **not** auto-fill stubs (CONTRACT-019). Call ``seed_reviewed_contracts``
        and/or ``register`` first; use ``ensure_registry`` only for exploratory fill.
        """
        missing = self.missing()
        if missing:
            raise AssertionError(f"Missing AccessibilityContract for: {missing[:20]}")
        need = REQUIRED_REVIEWED_CONTRACTS if require_reviewed is None else require_reviewed
        registered = {meta.name for meta in get_registry().components()}
        absent = sorted(name for name in need if name not in registered)
        if absent:
            raise AssertionError(
                f"REQUIRED AccessibilityContract components missing from registry: {absent[:20]}"
            )
        bad = self.unreviewed(need)
        if bad:
            raise AssertionError(f"Unreviewed AccessibilityContract for: {bad[:20]}")

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
            reviewed=all(p.reviewed for p in parts),
        )
