"""Registered AssetRef head merge for the official head-support extension."""

from __future__ import annotations

import html as html_lib
import re
from collections.abc import Mapping, Sequence

from hedron_core.application_assets import is_remote_application_href
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
_LINK_HREF = re.compile(r"<link\b[^>]*\bhref=['\"]([^'\"]+)['\"][^>]*>", re.IGNORECASE)
_INLINE_SCRIPT = re.compile(r"<script\b(?![^>]*\bsrc=)[^>]*>", re.IGNORECASE)
_ON_HANDLER = re.compile(r"\son[a-z]+\s*=", re.IGNORECASE)
_HTTP_ORIGIN = re.compile(r"^https?://", re.IGNORECASE)
# Attribute/tag breakouts that is_local_path can still admit in query/fragment.
_UNSAFE_HEAD_HREF_CHARS = frozenset("\"'<>`")
_SAFE_PASSTHROUGH_ATTRS = frozenset({"integrity", "crossorigin"})


def _require_local_head_href(href: str) -> str:
    text = href.strip()
    if not text:
        return ""
    if is_remote_application_href(text) or _HTTP_ORIGIN.match(text) or text.startswith("//"):
        raise error(
            HED_EXT_0011,
            title="Remote head asset rejected",
            explanation=f"Head AssetRef href {text!r} is not a local path.",
            remediation="Register same-origin AssetRef values only.",
        )
    # Root-relative paths use the HTMX local-path contract; relative paths without
    # a scheme are also local for ASSET-053 (vendor under the app origin).
    relative_ok = (
        not text.startswith("/")
        and not text.startswith("\\")
        and "://" not in text
        and not any(ch in text for ch in _UNSAFE_HEAD_HREF_CHARS)
        and not any(ch.isspace() for ch in text)
        and ".." not in text.split("/")
    )
    if (
        not (is_local_path(text) or relative_ok)
        or any(ch in text for ch in _UNSAFE_HEAD_HREF_CHARS)
        or any(ch.isspace() for ch in text)
    ):
        raise error(
            HED_EXT_0011,
            title="Unregistered head asset rejected",
            explanation=f"Head AssetRef href {text!r} is not an admitted local path.",
            remediation="Use a root-relative or relative AssetRef under the application origin.",
        )
    return text


def _attr_suffix(attributes: Mapping[str, str]) -> str:
    parts: list[str] = []
    for key in sorted(attributes):
        lowered = key.lower()
        if lowered not in _SAFE_PASSTHROUGH_ATTRS:
            continue
        value = attributes[key]
        parts.append(f' {lowered}="{html_lib.escape(str(value), quote=True)}"')
    return "".join(parts)


def admit_head_assets(assets: Sequence[AssetRef]) -> tuple[AssetRef, ...]:
    admitted: list[AssetRef] = []
    seen: set[str] = set()
    for asset in assets:
        href = _require_local_head_href(asset.href)
        if not href:
            continue
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
        href = html_lib.escape(_require_local_head_href(asset.href), quote=True)
        extra = _attr_suffix(asset.attributes)
        if asset.kind == "css":
            tags.append(f'<link rel="stylesheet" href="{href}"{extra}>')
        elif asset.kind == "module":
            tags.append(f'<script type="module" src="{href}"{extra}></script>')
        else:
            tags.append(f'<script src="{href}" defer{extra}></script>')
    return "\n".join(tags)


def _hrefs_already_in_html(html_text: str) -> set[str]:
    found = {m.group(1) for m in _SCRIPT_SRC.finditer(html_text)}
    found.update(m.group(1) for m in _LINK_HREF.finditer(html_text))
    return found


def merge_registered_head(
    html_text: str,
    assets: Sequence[AssetRef] | None,
    *,
    enabled: bool,
) -> str:
    """Merge admitted AssetRef tags into PAGE ``<head>`` when head-support is planned.

    Dedupes by href/src so call-site inject and head-support merge cannot emit the
    same script twice when tag strings differ (e.g. missing ``defer``).
    """
    if not enabled or not assets:
        return html_text
    present = _hrefs_already_in_html(html_text)
    missing_assets = tuple(a for a in assets if a.href.strip() not in present)
    if not missing_assets:
        return html_text
    tags = head_tags_from_assets(missing_assets)
    if not tags:
        return html_text
    injection = tags + "\n"
    if "</head>" in html_text:
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
