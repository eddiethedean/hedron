"""Registered AssetRef head merge for the official head-support extension."""

from __future__ import annotations

import re
from collections.abc import Sequence

from hedron_core.codes import HED_EXT_0011
from hedron_core.diagnostics import error
from hedron_core.htmx_contract import is_local_path
from hedron_core.rendering import AssetRef

__all__ = [
    "admit_head_assets",
    "head_tags_from_assets",
    "merge_registered_head",
    "reject_invented_fragment_scripts",
]

_SCRIPT_SRC = re.compile(r"<script\b[^>]*\bsrc=['\"]([^'\"]+)['\"][^>]*>", re.IGNORECASE)
_INLINE_SCRIPT = re.compile(r"<script\b(?![^>]*\bsrc=)[^>]*>", re.IGNORECASE)
_ON_HANDLER = re.compile(r"\son[a-z]+\s*=", re.IGNORECASE)
_HTTP_ORIGIN = re.compile(r"^https?://", re.IGNORECASE)


def admit_head_assets(assets: Sequence[AssetRef]) -> tuple[AssetRef, ...]:
    admitted: list[AssetRef] = []
    seen: set[str] = set()
    for asset in assets:
        href = asset.href.strip()
        if not href:
            continue
        if _HTTP_ORIGIN.match(href) or href.startswith("//"):
            raise error(
                HED_EXT_0011,
                title="Remote head asset rejected",
                explanation=f"Head AssetRef href {href!r} is not a local path.",
                remediation="Register same-origin AssetRef values only.",
            )
        if not is_local_path(href) and not href.startswith("/"):
            raise error(
                HED_EXT_0011,
                title="Unregistered head asset rejected",
                explanation=f"Head AssetRef href {href!r} is not an admitted local path.",
                remediation="Use a root-relative AssetRef under the application origin.",
            )
        for key, value in asset.attributes.items():
            lowered = key.lower()
            if lowered.startswith("on") or lowered == "nonce":
                raise error(
                    HED_EXT_0011,
                    title="Head merge rejected unsafe attribute",
                    explanation=f"Attribute {key!r} is not admitted on registered head assets.",
                    remediation="Omit event handlers and do not invent nonces.",
                )
            if lowered == "srcdoc" or (isinstance(value, str) and _ON_HANDLER.search(value)):
                raise error(
                    HED_EXT_0011,
                    title="Head merge rejected inline handler",
                    explanation="Registered head assets cannot carry event handlers.",
                    remediation="Use CSP-safe local scripts without inline handlers.",
                )
        if asset.kind not in {"css", "js", "module"}:
            continue
        if href in seen:
            continue
        seen.add(href)
        admitted.append(asset)
    return tuple(admitted)


def head_tags_from_assets(assets: Sequence[AssetRef]) -> str:
    tags: list[str] = []
    for asset in admit_head_assets(assets):
        href = asset.href
        if asset.kind == "css":
            tags.append(f'<link rel="stylesheet" href="{href}">')
        elif asset.kind == "module":
            tags.append(f'<script type="module" src="{href}"></script>')
        else:
            tags.append(f'<script src="{href}" defer></script>')
    return "\n".join(tags)


def merge_registered_head(
    html_text: str,
    assets: Sequence[AssetRef] | None,
    *,
    enabled: bool,
) -> str:
    """Merge admitted AssetRef tags into PAGE ``<head>`` when head-support is planned."""
    if not enabled or not assets:
        return html_text
    tags = head_tags_from_assets(assets)
    if not tags:
        return html_text
    injection = tags + "\n"
    if "</head>" in html_text:
        # Dedup: skip tags already present.
        missing = [line for line in tags.split("\n") if line and line not in html_text]
        if not missing:
            return html_text
        injection = "\n".join(missing) + "\n"
        return html_text.replace("</head>", f"{injection}</head>", 1)
    return html_text + injection


def reject_invented_fragment_scripts(html_text: str, *, admitted_hrefs: Sequence[str] = ()) -> None:
    """FRAGMENT responses never invent executable assets."""
    allowed = set(admitted_hrefs)
    if _INLINE_SCRIPT.search(html_text):
        raise error(
            HED_EXT_0011,
            title="Fragment invented an inline script",
            explanation="FRAGMENT responses cannot introduce executable head or inline script.",
            remediation="Keep scripts on the PAGE shell via admitted AssetRef values.",
        )
    for match in _SCRIPT_SRC.finditer(html_text):
        href = match.group(1)
        if href not in allowed:
            raise error(
                HED_EXT_0011,
                title="Fragment invented an executable asset",
                explanation=(
                    f"FRAGMENT included script src {href!r} that is not an admitted AssetRef."
                ),
                remediation=(
                    "Declare the asset on the PAGE shell; fragments must not install scripts."
                ),
            )
