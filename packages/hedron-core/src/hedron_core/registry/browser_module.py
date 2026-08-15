"""Browser-module registry catalog."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hedron_core.diagnostics import error


@dataclass(frozen=True, slots=True)
class BrowserModuleMeta:
    logical_id: str
    tag_name: str
    module_path: str
    observed_attributes: tuple[str, ...] = ()
    events: tuple[str, ...] = ()
    shadow_dom: bool = False
    htmx_lifecycle: bool = True


def register_browser_module(
    *,
    logical_id: str,
    tag_name: str,
    module_path: str,
    observed_attributes: Iterable[str] = (),
    events: Iterable[str] = (),
    shadow_dom: bool = False,
    htmx_lifecycle: bool = True,
) -> None:
    from hedron_core.registry.builder import active_builder

    if "-" not in tag_name:
        raise error(
            "HED-ASSET-0011",
            title="Invalid custom element tag",
            explanation=f"Custom element tag {tag_name!r} must contain a hyphen.",
            remediation="Use a hyphenated custom element name.",
        )
    active_builder().register_browser_module(
        BrowserModuleMeta(
            logical_id=logical_id,
            tag_name=tag_name,
            module_path=module_path,
            observed_attributes=tuple(observed_attributes),
            events=tuple(events),
            shadow_dom=shadow_dom,
            htmx_lifecycle=htmx_lifecycle,
        )
    )
