"""RESOLVE-029: pure Workbench resolver corpus (no listener, no app import)."""

from __future__ import annotations

import json

import pytest

from hedron_core.diagnostics import HedronError
from hedron_posit.config import WorkbenchConfig, WorkbenchMode, WorkbenchTopology
from hedron_posit.detect import is_workbench_env, is_workbench_forced
from hedron_posit.redact import redact_record, redact_text, redact_url
from hedron_posit.resolve import (
    RESOLVED_MODE_ENV,
    RESOLVED_MOUNT_ENV,
    RESOLVED_PUBLIC_BASE_ENV,
    parse_rserver_url_output,
    resolve_deployment,
)


def test_default_local_resolution() -> None:
    resolved = resolve_deployment(WorkbenchConfig(), environ={})
    assert resolved.mode is WorkbenchMode.AUTO
    assert resolved.host == "127.0.0.1"
    assert resolved.browser_mount == ""
    assert resolved.cookie_mount == "/"
    assert resolved.reload is False
    assert resolved.workers == 1
    assert resolved.active is False


def test_redaction_covers_nested_and_encoded_sensitive_keys() -> None:
    payload = redact_record({"Token": "secret", "nested": {"password": "pw", "safe": "ok"}})
    assert payload == {"Token": "***", "nested": {"password": "***", "safe": "ok"}}
    assert redact_url("https://example.test/path?%74oken=secret&access%5Ftoken=secret") == (
        "https://example.test/path?%74oken=***&access%5Ftoken=***"
    )


def test_bound_ephemeral_port_replaces_requested_zero() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(mode=WorkbenchMode.ON, port=0, mount="/s/bound/p/1"),
        environ={},
        bound_port=43123,
    )
    assert resolved.port == 43123
    assert resolved.bind == "127.0.0.1:43123"
    assert resolved.external_origin == "http://127.0.0.1:43123"


def test_mode_off_clears_mount() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(mode=WorkbenchMode.OFF, mount="/s/abc/p/1"),
        environ={},
    )
    assert resolved.browser_mount == ""
    assert resolved.source == "mode:off"


def test_namespaced_wins_over_alias() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(),
        environ={
            "HEDRON_WORKBENCH_MOUNT": "/s/ns/p/9",
            "BASE_PATH": "/s/alias/p/9",
        },
    )
    assert resolved.browser_mount == "/s/ns/p/9"
    assert not any("BASE_PATH" in w for w in resolved.warnings)


def test_alias_warns() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(),
        environ={"BASE_PATH": "/s/alias/p/1", "HOST": "127.0.0.1"},
    )
    assert resolved.browser_mount == "/s/alias/p/1"
    assert any("BASE_PATH" in w for w in resolved.warnings)
    assert any("HOST" in w for w in resolved.warnings)


def test_rs_server_url_is_not_activation(monkeypatch: pytest.MonkeyPatch) -> None:
    env = {"RS_SERVER_URL": "https://wb.example/s/abc/"}
    assert is_workbench_env(env) is True
    assert is_workbench_forced(env) is False
    resolved = resolve_deployment(WorkbenchConfig(), environ=env)
    assert resolved.browser_mount == ""
    assert resolved.active is False
    assert "pending" in resolved.source or resolved.source == "default"


def test_noninteractive_workbench_job_does_not_activate_browser_proxy() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(),
        environ={
            "RS_SERVER_URL": "https://wb.example/s/inherited/",
            "UVICORN_ROOT_PATH": "/s/inherited/p/8000",
            "AUDIT_DETAILS_PATH": "/tmp/audit",
        },
    )
    assert resolved.active is False
    assert resolved.browser_mount == ""
    assert resolved.source == "workbench-job:non-interactive"
    assert any("non-interactive" in warning for warning in resolved.warnings)


def test_parse_rserver_path_and_full_url() -> None:
    mount, origin, source = parse_rserver_url_output(
        "https://wb.example/s/4566a3c9ab5a7ad01e1a7/p/30507931/",
        port=8050,
    )
    assert mount == "/s/4566a3c9ab5a7ad01e1a7/p/30507931"
    assert origin == "https://wb.example"
    assert source == "rserver-url:full-url"
    mount, _, source = parse_rserver_url_output("/s/abc/p/12", port=8050)
    assert mount == "/s/abc/p/12"
    assert source == "rserver-url:path"


def test_parse_rserver_strips_proxy_port_segment() -> None:
    mount, _, _ = parse_rserver_url_output("/proxy/8050/s/abc/p/12", port=8050)
    assert mount == "/s/abc/p/12"


def test_parse_rserver_rejects_malformed() -> None:
    with pytest.raises(HedronError) as exc:
        parse_rserver_url_output("//evil.example/x", port=1)
    assert "HED-WB-0002" in str(exc.value)
    with pytest.raises(HedronError):
        parse_rserver_url_output("ftp://x/y", port=1)
    with pytest.raises(HedronError):
        parse_rserver_url_output("https://user:pass@host/s/x", port=1)
    with pytest.raises(HedronError):
        parse_rserver_url_output("\n" * 3, port=1)
    with pytest.raises(HedronError):
        parse_rserver_url_output("x" * 5000, port=1)
    with pytest.raises(HedronError):
        parse_rserver_url_output("https://wb.example/s/x?ignored=true", port=1)
    with pytest.raises(HedronError):
        parse_rserver_url_output("https://wb.example:99999/s/x", port=1)
    with pytest.raises(HedronError):
        parse_rserver_url_output("https://[", port=1)


def test_parse_rserver_canonicalizes_ipv6_origin() -> None:
    mount, origin, _ = parse_rserver_url_output("https://[2001:db8::1]:8443/s/x/p/1", port=1)
    assert mount == "/s/x/p/1"
    assert origin == "https://[2001:db8::1]:8443"


def test_malformed_bracketed_public_urls_are_diagnostics() -> None:
    with pytest.raises(HedronError):
        resolve_deployment(WorkbenchConfig(public_base_url="https://["), environ={})
    with pytest.raises(HedronError):
        resolve_deployment(
            WorkbenchConfig(),
            environ={
                "RS_SERVER_URL": "https://wb.example/",
                "UVICORN_ROOT_PATH": "https://[",
            },
        )


def test_malformed_bracketed_urls_are_safe_to_redact() -> None:
    assert redact_url("https://[") == "https://["
    assert redact_url("https://[?%74oken=secret") == "https://[?%74oken=***"


def test_conflicting_mount_and_public_base() -> None:
    with pytest.raises(HedronError) as exc:
        resolve_deployment(
            WorkbenchConfig(
                mount="/s/a/p/1",
                public_base_url="https://wb.example/s/b/p/2",
            ),
            environ={},
        )
    assert "HED-WB-0001" in str(exc.value)


def test_invalid_port() -> None:
    with pytest.raises(HedronError):
        resolve_deployment(WorkbenchConfig(), environ={"HEDRON_WORKBENCH_PORT": "nope"})
    with pytest.raises(HedronError):
        resolve_deployment(WorkbenchConfig(), environ={"HEDRON_WORKBENCH_PORT": "70000"})
    with pytest.raises(HedronError):
        resolve_deployment(WorkbenchConfig(port=70000), environ={})


def test_invalid_workers_are_diagnostic() -> None:
    with pytest.raises(HedronError) as exc:
        resolve_deployment(WorkbenchConfig(), environ={"HEDRON_WORKBENCH_WORKERS": "many"})
    assert "HED-WB-0001" in str(exc.value)
    with pytest.raises(HedronError):
        resolve_deployment(WorkbenchConfig(workers=0), environ={})


def test_invalid_explicit_mount_fails_closed() -> None:
    with pytest.raises(HedronError) as exc:
        resolve_deployment(WorkbenchConfig(mount="/s/x/../admin"), environ={})
    assert "Invalid Workbench mount" in str(exc.value)


@pytest.mark.parametrize(
    "value",
    [
        "ftp://wb.example/s/x",
        "https://user:secret@wb.example/s/x",
        "https://wb.example/s/x?token=secret",
        "//wb.example/s/x",
    ],
)
def test_unsafe_public_base_fails_closed(value: str) -> None:
    with pytest.raises(HedronError):
        resolve_deployment(WorkbenchConfig(public_base_url=value), environ={})


def test_external_bind_requires_explicit_opt_in() -> None:
    with pytest.raises(HedronError):
        resolve_deployment(WorkbenchConfig(host="0.0.0.0"), environ={})
    resolved = resolve_deployment(
        WorkbenchConfig(host="0.0.0.0", allow_external_bind=True), environ={}
    )
    assert resolved.host == "0.0.0.0"


def test_forwarded_allowlist_is_unified_and_validated() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(forwarded_allow_ips="10.0.0.2"),
        environ={"HEDRON_WORKBENCH_FORWARDED_ALLOW_IPS": "10.0.0.3"},
    )
    assert resolved.forwarded_allow_ips == "10.0.0.2"
    alias = resolve_deployment(WorkbenchConfig(), environ={"FORWARDED_ALLOW_IPS": "10.0.0.4"})
    assert alias.forwarded_allow_ips == "10.0.0.4"
    assert any("FORWARDED_ALLOW_IPS" in warning for warning in alias.warnings)
    with pytest.raises(HedronError):
        resolve_deployment(WorkbenchConfig(forwarded_allow_ips="*"), environ={})
    cidr = resolve_deployment(
        WorkbenchConfig(forwarded_allow_ips="10.42.0.0/24,fd00::/64"), environ={}
    )
    assert cidr.forwarded_allow_ips == "10.42.0.0/24,fd00::/64"


def test_workbench_uvicorn_root_path_is_consumed_only_with_runtime_evidence() -> None:
    workbench = resolve_deployment(
        WorkbenchConfig(),
        environ={
            "RS_SERVER_URL": "https://wb.example/",
            "UVICORN_ROOT_PATH": "/s/default/p/8000",
        },
    )
    assert workbench.active is True
    assert workbench.browser_mount == "/s/default/p/8000"
    ordinary = resolve_deployment(
        WorkbenchConfig(),
        environ={"UVICORN_ROOT_PATH": "/generic"},
    )
    assert ordinary.active is False
    assert ordinary.browser_mount == ""


def test_workbench_uvicorn_root_path_accepts_rserver_url_full_url() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(),
        environ={
            "RS_SERVER_URL": "https://wb.example/s/session/",
            "UVICORN_ROOT_PATH": "https://wb.example/s/session/p/8000/",
        },
    )
    assert resolved.active is True
    assert resolved.browser_mount == "/s/session/p/8000"
    assert resolved.discovered is False


def test_workbench_uvicorn_root_path_is_ignored_for_different_bound_port() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(),
        environ={
            "RS_SERVER_URL": "https://wb.example/s/session/",
            "UVICORN_ROOT_PATH": "https://wb.example/s/session/p/8000/",
        },
        bound_port=8050,
    )
    assert resolved.browser_mount == ""
    assert resolved.active is False


def test_operator_public_origin_may_differ_from_discovery_origin() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(public_base_url="https://canonical.example/s/x/p/1"),
        environ={},
        discovered_raw="https://internal.example/s/x/p/1",
        bound_port=8050,
    )
    assert resolved.external_origin == "https://canonical.example"


@pytest.mark.parametrize(
    "topology",
    [WorkbenchTopology.LAUNCHER_KUBERNETES, WorkbenchTopology.LAUNCHER_SLURM],
)
def test_remote_launcher_profiles_select_reachable_bind(
    topology: WorkbenchTopology,
) -> None:
    resolved = resolve_deployment(WorkbenchConfig(topology=topology), environ={})
    assert resolved.host == "0.0.0.0"
    assert resolved.topology is topology


def test_invalid_topology_is_diagnostic() -> None:
    with pytest.raises(HedronError, match="Invalid Workbench topology"):
        resolve_deployment(
            WorkbenchConfig(),
            environ={"HEDRON_WORKBENCH_TOPOLOGY": "somewhere"},
        )


def test_launcher_handoff_is_consumed_as_active_state() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(),
        environ={
            RESOLVED_MOUNT_ENV: "/s/resolved/p/7",
            RESOLVED_PUBLIC_BASE_ENV: "https://wb.example/s/resolved/p/7",
            RESOLVED_MODE_ENV: "auto",
        },
    )
    assert resolved.active is True
    assert resolved.browser_mount == "/s/resolved/p/7"
    assert resolved.external_origin == "https://wb.example"


def test_redaction_removes_url_credentials_and_assignments() -> None:
    assert "user:secret" not in redact_url("https://user:secret@wb.example/s/x?token=value")
    assert "supersecret" not in redact_text("token=supersecret")


def test_redacted_record_hides_session_and_license() -> None:
    resolved = resolve_deployment(
        WorkbenchConfig(mount="/s/4566a3c9ab5a7ad01e1a7/p/30507931"),
        environ={},
    )
    payload = redact_record(resolved.as_dict())
    dumped = json.dumps(payload)
    assert "4566a3c9ab5a7ad01e1a7" not in dumped
    assert "***" in dumped
    assert "6IX8-R4P6-UDJS-BIE5" not in redact_text("key=6IX8-R4P6-UDJS-BIE5-UGAH-8XSS-26TA")
