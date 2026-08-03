"""Typed style symbol bindings for scoped CSS."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from hedron_core.codes import HED_CSS_UNKNOWN_SYMBOL
from hedron_core.diagnostics import error

__all__ = ["StyleSymbols", "styles_from_manifest"]


@dataclass(frozen=True, slots=True)
class StyleSymbols:
    """Attribute-access binding for authored local class names."""

    _symbols: Mapping[str, str]
    _component_id: str = ""

    def __getattr__(self, name: str) -> str:
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            return self._symbols[name]
        except KeyError as exc:
            suggestions = sorted(self._symbols)
            hint = f" Known symbols: {', '.join(suggestions)}." if suggestions else ""
            raise error(
                HED_CSS_UNKNOWN_SYMBOL,
                title="Unknown style symbol",
                explanation=f"styles.{name} is not defined for this component.{hint}",
                remediation="Define the class in styles.css or fix the symbol name.",
                component_id=self._component_id or None,
                context={"symbol": name, "known": suggestions},
            ) from exc

    def get(self, name: str, default: str | None = None) -> str | None:
        return self._symbols.get(name, default)

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._symbols

    def as_dict(self) -> dict[str, str]:
        return dict(self._symbols)

    def __iter__(self) -> Any:
        return iter(self._symbols)


def styles_from_manifest(symbols: Mapping[str, str], *, component_id: str = "") -> StyleSymbols:
    return StyleSymbols(_symbols=dict(symbols), _component_id=component_id)
