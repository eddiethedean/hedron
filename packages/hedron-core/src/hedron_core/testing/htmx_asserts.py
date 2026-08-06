"""HTMX region authorization and shell dual-path asserts (phase 0.15 #25–#26)."""

from __future__ import annotations

import re
from collections.abc import Sequence

from hedron_core.interaction import FragmentRegion
from hedron_core.testing.adapters import AdapterResponse, assert_fragment_body, assert_page_document

__all__ = [
    "assert_shell_dual_path",
    "assert_ui_targets_subset_of_regions",
    "assert_undeclared_target_rejected",
]

_TARGET_ATTR_RE = re.compile(
    r"""(?:data-)?hx-target\s*=\s*(?P<q>["'])(?P<value>.*?)(?P=q)""",
    re.IGNORECASE | re.DOTALL,
)
_FRAGMENT_REGION_HINT = re.compile(
    r"FragmentRegionError|HED-HTMX-0001|not an authorized|undeclared",
    re.IGNORECASE,
)


def _region_selectors(regions: Sequence[FragmentRegion | str]) -> set[str]:
    out: set[str] = set()
    for region in regions:
        if isinstance(region, FragmentRegion):
            out.add(region.selector)
        else:
            out.add(str(region))
    return out


def assert_undeclared_target_rejected(response: AdapterResponse) -> None:
    """Assert fail-closed undeclared HX-Target handling.

    Requires HTTP 403 **and** a region-specific signal (``FragmentRegionError``,
    ``HED-HTMX-0001``, or undeclared/not-authorized wording). Generic CSRF 403s and
    200 bodies that merely mention ``HX-Target`` do not pass.
    """
    assert response.status_code == 403, (
        f"expected 403 for undeclared HX-Target, got status={response.status_code} "
        f"body={response.body!r}"
    )
    assert _FRAGMENT_REGION_HINT.search(response.body), (
        f"expected FragmentRegionError / HED-HTMX-0001 detail in 403 body, "
        f"got body={response.body!r}"
    )


def assert_ui_targets_subset_of_regions(
    html: str,
    regions: Sequence[FragmentRegion | str],
) -> None:
    """Assert every ``hx-target`` / ``data-hx-target`` in markup is a declared region selector."""
    allowed = _region_selectors(regions)
    found: list[str] = []
    for match in _TARGET_ATTR_RE.finditer(html):
        value = match.group("value").strip()
        if value:
            found.append(value)
    unknown = sorted({target for target in found if target not in allowed})
    assert not unknown, f"undeclared hx-target selectors {unknown!r}; allowed={sorted(allowed)!r}"


def assert_shell_dual_path(
    fragment_response: AdapterResponse,
    page_response: AdapterResponse,
    *,
    fragment_contains: str | None = None,
) -> None:
    """Assert fragment lacks document chrome while page is a full document or 303."""
    if fragment_contains is not None:
        assert_fragment_body(fragment_response, contains=fragment_contains)
    else:
        assert fragment_response.status_code == 200
        assert "<html" not in fragment_response.body.lower()

    if page_response.status_code in {301, 302, 303, 307, 308}:
        return
    assert_page_document(page_response)
