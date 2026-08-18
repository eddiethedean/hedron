"""#257: ActionAsync hx-post must use UrlPurpose.FORM_ACTION."""

from __future__ import annotations

import pytest

from hedron_core.diagnostics import HedronError
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_elements.action_async import ActionAsync


def test_fragment_only_hx_post_is_rejected() -> None:
    with pytest.raises(HedronError, match="HED-SEC-0001"):
        ActionAsync("Go", hx_post="#frag")
    with pytest.raises(HedronError, match="HED-SEC-0001"):
        SafeUrl.parse("#frag", purpose=UrlPurpose.FORM_ACTION)


def test_root_relative_hx_post_is_accepted() -> None:
    el = ActionAsync("Go", hx_post="/actions")
    assert el.props.hx_post is not None
    assert str(el.props.hx_post) == "/actions"
