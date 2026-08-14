"""Form contract validation for Web Component registry entries (phase 0.37)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from hedron_core.diagnostics import error

FORM_CONTRACT_KEYS = frozenset(
    {
        "association_mode",
        "value_encoding",
        "reset_policy",
        "restore_policy",
        "validation_mapping",
        "fallback_tag",
    }
)

ASSOCIATION_MODES = frozenset({"none", "single", "multi"})


def validate_form_contract(contract: Mapping[str, object] | None, *, tag_name: str) -> None:
    """Require populated form_contract for form-associated 0.37+ elements."""
    if contract is None:
        return
    missing = FORM_CONTRACT_KEYS - set(contract.keys())
    if missing:
        raise error(
            "HED-ELEMENT-0007",
            title="Incomplete form contract",
            explanation=(
                f"Element {tag_name!r} form_contract missing required keys: {sorted(missing)!r}."
            ),
            remediation="Populate all form_contract fields per WEB_COMPONENT_PLATFORM.md.",
        )
    mode = str(contract.get("association_mode", ""))
    if mode not in ASSOCIATION_MODES:
        raise error(
            "HED-ELEMENT-0007",
            title="Invalid form association mode",
            explanation=f"association_mode {mode!r} is not supported.",
            remediation="Use none, single, or multi.",
        )
    if mode == "none":
        raise error(
            "HED-ELEMENT-0007",
            title="Form contract on non-associated element",
            explanation=f"Element {tag_name!r} declares association_mode=none with form_contract.",
            remediation="Omit form_contract or use single/multi for form-associated elements.",
        )
    for key in FORM_CONTRACT_KEYS:
        val = contract.get(key)
        if val is None or (isinstance(val, str) and not val.strip()):
            raise error(
                "HED-ELEMENT-0007",
                title="Empty form contract field",
                explanation=f"form_contract[{key!r}] must be non-empty for {tag_name!r}.",
                remediation="Provide explicit form_contract values.",
            )


def form_contract_dict(**kwargs: Any) -> dict[str, object]:
    """Build a validated form_contract mapping for registration."""
    contract = dict(kwargs)
    validate_form_contract(contract, tag_name=str(kwargs.get("fallback_tag", "unknown")))
    return contract
