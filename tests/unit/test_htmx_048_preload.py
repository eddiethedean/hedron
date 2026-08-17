"""PRELOAD-048 GET authoring value mapped to decide_preload."""

from __future__ import annotations

import pytest
from tests.unit._helpers_048 import injected_page

from hedron.experimental import apply_preload_headers, evaluate_preload_request
from hedron.live_claims import EXPERIMENTAL_LIVE_SURFACES
from hedron_core import HedronError
from hedron_core.builtins.shell import HtmxLink
from hedron_core.codes import HED_EXT_0006
from hedron_core.preload import HX_PRELOADED, NavigationPreloadPolicy, decide_preload
from hedron_core.rendering import RenderMode, render
from hedron_core.security import SafeUrl, UrlPurpose


def test_get_link_emits_closed_preload_mode() -> None:
    link = HtmxLink(
        "Next",
        SafeUrl.parse("/next", purpose=UrlPurpose.NAVIGATION),
        preload="mouseover",
    )
    html, result = injected_page(link, htmx_extensions={"preload"})
    assert 'preload="mouseover"' in html
    assert "preload.js" in html
    assert result.htmx_plan.ids == ("preload",)  # type: ignore[union-attr]


def test_mutation_and_external_preload_rejected() -> None:
    url = SafeUrl.parse("/next", purpose=UrlPurpose.NAVIGATION)
    with pytest.raises(HedronError) as post:
        HtmxLink("Save", url, method="post", preload="mousedown")
    assert post.value.diagnostic.code == HED_EXT_0006
    with pytest.raises(HedronError) as ext:
        HtmxLink(
            "Away",
            SafeUrl.parse(
                "https://example.com/",
                purpose=UrlPurpose.NAVIGATION,
                allow_external=True,
            ),
            external=True,
            preload="mousedown",
        )
    assert ext.value.diagnostic.code == HED_EXT_0006
    with pytest.raises(HedronError) as mode:
        HtmxLink("Next", url, preload="preload:init")
    assert mode.value.diagnostic.code == HED_EXT_0006


def test_decide_preload_and_helpers_stay_experimental() -> None:
    allowed = decide_preload(
        NavigationPreloadPolicy(enabled=True),
        method="GET",
        same_origin=True,
        speculative_count=0,
        concurrent=0,
    )
    assert allowed.allowed
    assert allowed.header_value == "1"
    denied = decide_preload(
        NavigationPreloadPolicy(enabled=True),
        method="POST",
        same_origin=True,
        speculative_count=0,
        concurrent=0,
    )
    assert not denied.allowed
    assert HX_PRELOADED == "HX-Preloaded"
    assert "evaluate_preload_request" in EXPERIMENTAL_LIVE_SURFACES
    assert "apply_preload_headers" in EXPERIMENTAL_LIVE_SURFACES
    assert callable(evaluate_preload_request)
    assert callable(apply_preload_headers)


def test_unset_page_does_not_inject_preload() -> None:
    html = render(
        HtmxLink("Next", SafeUrl.parse("/next", purpose=UrlPurpose.NAVIGATION)),
        mode=RenderMode.FRAGMENT,
    ).html
    assert "preload=" not in html
