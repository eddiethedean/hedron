from __future__ import annotations

import json
import math
from pathlib import Path
from zipfile import BadZipFile

import pytest
from jinja2 import DictLoader, Environment

from hedron.csp import ingest_csp_report
from hedron.replay import MemoryReplayStore, ReplayState
from hedron.upload import UploadHandle
from hedron_core import HedronError
from hedron_core.navigation import is_safe_navigation_url
from hedron_core.origin import is_same_origin
from hedron_data.advanced import evaluate_formula
from hedron_data.sources import DataQuery
from hedron_data.spreadsheet import export_rows_xlsx, import_rows_xlsx
from hedron_jinja import HedronJinja
from hedron_jinja.source import inferred_capabilities, parse_hdj_source


def _hdj(body: str) -> str:
    return f'---hdj\nversion = 1\nkind = "fragment"\nprofile = "standard"\n---\n{body}'


def test_srcset_infers_every_remote_origin() -> None:
    parsed = parse_hdj_source(
        "x.hdj",
        _hdj(
            '<img srcset="/local.png 1x, https://cdn-a.test/a.png 2x, https://cdn-b.test/b.png 3x">'
        ),
    )
    capabilities = inferred_capabilities(parsed)
    assert "network.image-origin:https://cdn-a.test" in capabilities
    assert "network.image-origin:https://cdn-b.test" in capabilities


def test_malformed_network_ports_fail_closed() -> None:
    assert not is_same_origin(
        "https://example.test:notaport",
        request_scheme="https",
        request_hostname="example.test",
        request_port=443,
    )
    assert not is_safe_navigation_url("https://[", origin="https://example.test")


def test_xlsx_bounds_and_duplicate_headers_are_rejected() -> None:
    with pytest.raises(BadZipFile):
        import_rows_xlsx(
            b"PK\x03\x04"  # malformed archive is rejected before any allocation
        )
    with pytest.raises(HedronError):
        import_rows_xlsx(export_rows_xlsx([], ["dup", "dup"]))


def test_csp_reporting_batch_is_normalized() -> None:
    body = json.dumps([{"type": "csp", "body": {"effective-directive": "script-src"}}]).encode()
    parsed = ingest_csp_report(body, content_type="application/reports+json")
    assert parsed == [
        {
            "effective_directive": "script-src",
            "violated_directive": "",
            "disposition": "",
            "status_code": None,
            "redacted": True,
        }
    ]


def test_replay_capacity_allows_completed_retry() -> None:
    store = MemoryReplayStore(max_keys=1)
    first = store.claim(key="k", fingerprint="f", scope="s", retention_seconds=60)
    assert first.state is ReplayState.FIRST
    store.complete(key="k", scope="s", fingerprint="f", status=200, body=b"ok")
    assert (
        store.claim(key="k", fingerprint="f", scope="s", retention_seconds=60).state
        is ReplayState.REPLAYED
    )


def test_query_and_timeout_values_reject_non_finite_or_non_integer() -> None:
    with pytest.raises(ValueError):
        DataQuery(limit=1.5).validated()  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        DataQuery(offset=True).validated()  # type: ignore[arg-type]
    with pytest.raises(HedronError):
        evaluate_formula("=[x]", {"x": math.inf})


def test_upload_cleanup_retains_ownership_on_unlink_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "upload.bin"
    path.write_bytes(b"x")
    handle = UploadHandle("x", None, 1, path)
    monkeypatch.setattr(Path, "unlink", lambda _self: (_ for _ in ()).throw(OSError("busy")))
    handle.cleanup()
    assert handle.owned is True


def test_hdj_tojson_rejects_non_finite_values() -> None:
    env = Environment(loader=DictLoader({"x.hdj": _hdj("{{ view.value|tojson }}")}))
    templates = HedronJinja(env)
    with pytest.raises(ValueError):
        templates.render("x.hdj", {"value": math.nan})
