"""#376: SseTrigger rejects morph and extended hx-target selectors."""

from __future__ import annotations

import pytest

from hedron_core.builtins import Text
from hedron_core.codes import HED_EXT_0010
from hedron_core.diagnostics import HedronError
from hedron_core.rendering import RenderMode, render
from hedron_core.sse_ext import SseTrigger


def test_sse_trigger_rejects_morph_and_extended_targets() -> None:
    with pytest.raises(HedronError) as morph:
        SseTrigger(Text("x"), event="ping", swap="morph")
    assert morph.value.diagnostics[0].code == HED_EXT_0010
    with pytest.raises(HedronError) as closest:
        SseTrigger(Text("x"), event="ping", target="closest body")
    assert closest.value.diagnostics[0].code == HED_EXT_0010
    with pytest.raises(HedronError) as script:
        SseTrigger(Text("x"), event="ping", target="javascript:alert(1)")
    assert script.value.diagnostics[0].code == HED_EXT_0010


def test_sse_trigger_id_target_still_works() -> None:
    html = render(
        SseTrigger(Text("x"), event="ping", target="#panel"),
        mode=RenderMode.FRAGMENT,
    ).html
    assert 'hx-target="#panel"' in html
