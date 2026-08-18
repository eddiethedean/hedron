"""#375: SseRegion.connect rejects navigation-only EventSource URLs."""

from __future__ import annotations

import pytest

from hedron_core.builtins import Text
from hedron_core.codes import HED_EXT_0010, HED_SEC_0001
from hedron_core.diagnostics import HedronError
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.sse_ext import SseRegion


def test_sse_connect_rejects_fragment_mailto_and_external() -> None:
    with pytest.raises(HedronError) as fragment:
        SseRegion(Text("x"), connect="#main")
    assert fragment.value.diagnostics[0].code in {HED_EXT_0010, HED_SEC_0001}
    with pytest.raises(HedronError) as mail:
        SseRegion(Text("x"), connect="mailto:x@y.com")
    assert mail.value.diagnostics[0].code in {HED_EXT_0010, HED_SEC_0001}
    ext = SafeUrl.parse(
        "https://evil.example/stream",
        purpose=UrlPurpose.NAVIGATION,
        allow_external=True,
    )
    with pytest.raises(HedronError) as foreign:
        SseRegion(Text("x"), connect=ext)
    assert foreign.value.diagnostics[0].code in {HED_EXT_0010, HED_SEC_0001}


def test_sse_connect_accepts_local_path() -> None:
    region = SseRegion(Text("x"), connect="/jobs/1/events")
    assert str(region.props.connect).startswith("/jobs/")
