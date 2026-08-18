"""#265: chart reject_remote_urls must block blob: and vbscript:."""

from __future__ import annotations

import pytest

from hedron_charts.limits import _is_remote_url, reject_remote_urls
from hedron_core.diagnostics import HedronError


def test_blob_and_vbscript_are_remote_asset_schemes() -> None:
    assert _is_remote_url("blob:foo") is True
    assert _is_remote_url("vbscript:alert(1)") is True
    with pytest.raises(HedronError, match="HED-CHART-0005"):
        reject_remote_urls({"href": "blob:foo"})
    with pytest.raises(HedronError, match="HED-CHART-0005"):
        reject_remote_urls({"src": "vbscript:alert(1)"})
    with pytest.raises(HedronError, match="HED-CHART-0005"):
        reject_remote_urls({"href": "javascript:alert(1)"})
