from __future__ import annotations

import io
import json
import math
import zipfile
from pathlib import Path

import pytest
from fastapi import HTTPException
from jinja2 import DictLoader, Environment

from hedron.csp import ingest_csp_report
from hedron.replay import MemoryReplayStore, ReplayState
from hedron.security.policy import SecurityPolicy
from hedron.security.redirects import redirect_external
from hedron.security.session_timeout import check_session_timeout, stamp_session_created
from hedron.upload import UploadHandle
from hedron_core import HedronError
from hedron_core.intent import IntentError, SecurityKeyring, mint_intent, verify_intent
from hedron_core.navigation import is_safe_navigation_url
from hedron_core.origin import is_same_origin
from hedron_data.advanced import evaluate_formula, pivot_rows
from hedron_data.sources import DataQuery
from hedron_data.spreadsheet import (
    export_rows_ods,
    export_rows_xlsx,
    import_rows_ods,
    import_rows_xlsx,
)
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

    credentialed = parse_hdj_source(
        "credentials.hdj", _hdj('<img src="https://user:pass@cdn-c.test/a.png">')
    )
    assert "network.image-origin:https://cdn-c.test" in inferred_capabilities(credentialed)


def test_malformed_hdj_literal_url_is_a_diagnostic_not_parser_exception() -> None:
    templates = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": _hdj('<button hx-get="https://[">x</button>')}))
    )
    assert any(item.code == "HED-JINJA-0021" for item in templates.check("x.hdj"))


def test_malformed_network_ports_fail_closed() -> None:
    assert not is_same_origin(
        "https://example.test:notaport",
        request_scheme="https",
        request_hostname="example.test",
        request_port=443,
    )
    assert not is_safe_navigation_url("https://[", origin="https://example.test")
    with pytest.raises(HTTPException) as exc_info:
        redirect_external("http://:80/path", policy=SecurityPolicy(allow_external_redirects=True))
    assert getattr(exc_info.value, "status_code", None) == 400


def test_xlsx_bounds_and_duplicate_headers_are_rejected() -> None:
    original = export_rows_xlsx([], ["header"])
    rewritten = io.BytesIO()
    with (
        zipfile.ZipFile(io.BytesIO(original)) as source,
        zipfile.ZipFile(rewritten, "w", zipfile.ZIP_DEFLATED) as target,
    ):
        for member in source.infolist():
            content = source.read(member.filename)
            if member.filename.endswith("worksheets/sheet1.xml"):
                content = content.replace(b'r="A1"', b'r="ZZZZZZ1"')
            target.writestr(member, content)
    with pytest.raises(HedronError, match="outside the XLSX worksheet limits"):
        import_rows_xlsx(rewritten.getvalue())
    with pytest.raises(HedronError):
        import_rows_xlsx(export_rows_xlsx([], ["dup", "dup"]))
    with pytest.raises(HedronError):
        import_rows_ods(export_rows_ods([], ["dup", "dup"]))


def test_csp_reporting_batch_is_normalized() -> None:
    body = json.dumps(
        [
            {"type": "deprecation", "body": {"effectiveDirective": "ignored"}},
            {"type": "csp-violation", "body": {"effectiveDirective": "script-src"}},
        ]
    ).encode()
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


def test_query_and_formula_values_reject_non_finite_or_non_integer() -> None:
    with pytest.raises(ValueError):
        DataQuery(limit=1.5).validated()  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        DataQuery(offset=True).validated()  # type: ignore[arg-type]
    with pytest.raises(HedronError):
        evaluate_formula("=[x]", {"x": math.inf})
    with pytest.raises(ValueError, match="finite JSON number"):
        pivot_rows(
            [
                {"group": "g", "column": "c", "value": 1e308},
                {"group": "g", "column": "c", "value": 1e308},
            ],
            index="group",
            columns="column",
            values="value",
        )


def test_session_and_intent_timestamps_must_be_finite() -> None:
    session = {"hedron_session_created": 0.0, "hedron_session_last_seen": 0.0}
    with pytest.raises(ValueError):
        check_session_timeout(session, idle_seconds=math.nan, absolute_seconds=None, now=1.0)
    with pytest.raises(ValueError):
        stamp_session_created({}, now=math.inf)

    keyring = SecurityKeyring()
    keyring.mint_key(key_id="k", secret=b"x" * 32)
    intent_kwargs = {
        "keyring": keyring,
        "actor": "a",
        "tenant": "t",
        "action": "update",
        "method": "POST",
        "resource": "r",
        "revision": "1",
        "target": "/r",
    }
    with pytest.raises(ValueError):
        mint_intent(**intent_kwargs, ttl_seconds=math.nan)  # type: ignore[arg-type]
    intent = mint_intent(**intent_kwargs, now=1.0)  # type: ignore[arg-type]
    with pytest.raises(IntentError):
        verify_intent(intent, **intent_kwargs, now=math.inf)  # type: ignore[arg-type]


def test_upload_cleanup_retains_ownership_on_unlink_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "upload.bin"
    path.write_bytes(b"x")
    handle = UploadHandle("x", None, 1, path)

    def fail_unlink(_path: Path, *, missing_ok: bool = False) -> None:
        del _path, missing_ok
        raise OSError("busy")

    monkeypatch.setattr(Path, "unlink", fail_unlink)
    handle.cleanup()
    assert handle.owned is True


def test_hdj_tojson_rejects_non_finite_values() -> None:
    env = Environment(loader=DictLoader({"x.hdj": _hdj("{{ view.value|tojson(2) }}")}))
    env.policies["json.dumps_kwargs"] = {"sort_keys": False}
    templates = HedronJinja(env)
    with pytest.raises(ValueError):
        templates.render("x.hdj", {"value": math.nan})
    rendered = templates.render("x.hdj", {"value": {"b": 1, "a": 2}})
    assert rendered.html.index('"b"') < rendered.html.index('"a"')
