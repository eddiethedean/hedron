"""Locked 14-issue phase 0.41 regression packet.

Historical honesty: this packet listed 14 issue IDs but only ships two behavioral
tests below. New remediations must follow the REGRESS-042 ``ISSUE_TESTS`` binding
pattern instead of length-only locks.
"""

from __future__ import annotations

from fastapi_workbench.config import WorkbenchConfig
from fastapi_workbench.resolve import explicit_mount_hint
from hedron_core.diagnostics import HedronError
from hedron_core.htmx_eval import reject_hx_eval_value

ISSUES = (70, 74, 85, 98, 103, 106, 135, 149, 150, 185, 186, 200, 202, 207)


def test_historical_packet_lists_fourteen_ids_without_overclaiming_coverage() -> None:
    assert len(ISSUES) == 14
    # Explicitly document incomplete binding — do not equate this with Verified
    # remediation coverage for every ID.
    behavioral_tests_in_this_module = 2
    assert behavioral_tests_in_this_module < len(ISSUES)


def test_explicit_mount_hint_accepts_hedron_root_path() -> None:
    assert (
        explicit_mount_hint(WorkbenchConfig(), {"HEDRON_ROOT_PATH": "/s/session/p/1"})
        == "/s/session/p/1"
    )


def test_zero_width_unicode_cannot_hide_js_eval() -> None:
    for value in ("js\u200b:alert(1)", "js\u200c:alert(1)", "js\ufeff:alert(1)"):
        try:
            reject_hx_eval_value("hx-vals", value)
        except HedronError as exc:
            assert "HED-SEC-0011" in str(exc)
        else:
            raise AssertionError(f"eval value accepted: {value!r}")
