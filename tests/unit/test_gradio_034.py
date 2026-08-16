"""Phase 0.34 Gradio production-grade behavior."""

from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any

import pytest

from hedron_gradio import GradioClientAdapter, GradioEndpoint, GradioRemoteError
from hedron_gradio.artifacts import ArtifactStore
from hedron_gradio.hf import (
    hf_remote_config_for_space,
    hf_space_base_url,
    load_hf_fixture,
    translate_hf_vendor_status,
)
from hedron_gradio.jobs import GradioJobManager, job_scope_key
from hedron_gradio.policy import GradioRemoteConfig, redact_sensitive_text, validate_remote_url

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "gradio"


def test_package_version_is_beta_line() -> None:
    from hedron_gradio import __version__

    assert __version__ == "0.2.0"


def test_validate_remote_url_blocks_private_host() -> None:
    config = GradioRemoteConfig.from_base_url("https://example.invalid")
    with pytest.raises(GradioRemoteError, match="not in the allowlist"):
        validate_remote_url("https://127.0.0.1/predict", config)


def test_host_is_private_for_ipv4_mapped_and_compatible_ipv6() -> None:
    """#284: IPv4-mapped / IPv4-compatible IPv6 literals embed private IPv4."""
    from hedron_gradio.policy import _host_is_private

    assert _host_is_private("::ffff:127.0.0.1") is True
    assert _host_is_private("::127.0.0.1") is True
    assert _host_is_private("::ffff:169.254.169.254") is True
    assert _host_is_private("::ffff:8.8.8.8") is False

    cfg = GradioRemoteConfig(
        base_url="https://example.invalid",
        allowed_hosts=frozenset({"::ffff:127.0.0.1", "::ffff:169.254.169.254"}),
        allowed_schemes=frozenset({"https"}),
        allow_private_hosts=False,
    )
    with pytest.raises(GradioRemoteError, match="Private or loopback"):
        validate_remote_url("https://[::ffff:127.0.0.1]/run", cfg)
    with pytest.raises(GradioRemoteError, match="Private or loopback"):
        validate_remote_url("https://[::ffff:169.254.169.254]/run", cfg)


def test_validate_remote_url_allows_declared_host() -> None:
    config = GradioRemoteConfig.from_base_url("https://demo.example.invalid")
    validate_remote_url("https://demo.example.invalid/predict", config)


def _addrinfo_for(ip: str) -> list[tuple[Any, ...]]:
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    sockaddr: tuple[Any, ...] = (ip, 0, 0, 0) if family == socket.AF_INET6 else (ip, 0)
    return [(family, socket.SOCK_STREAM, 6, "", sockaddr)]


def test_validate_remote_url_blocks_dns_to_private(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """#268: allowlisted names that resolve to link-local/loopback fail closed."""
    import hedron_gradio.policy as policy
    from hedron_gradio.policy import _host_is_private

    def _getaddrinfo(
        host: str, port: object, *args: object, **kwargs: object
    ) -> list[tuple[Any, ...]]:
        del port, args, kwargs
        if str(host).strip().lower().rstrip(".") == "attacker.example":
            return _addrinfo_for("169.254.169.254")
        raise socket.gaierror(socket.EAI_NONAME, "not found")

    monkeypatch.setattr(policy.socket, "getaddrinfo", _getaddrinfo)
    assert _host_is_private("attacker.example") is False
    cfg = GradioRemoteConfig.from_base_url("https://attacker.example", allow_private_hosts=False)
    assert cfg.allow_private_hosts is False
    with pytest.raises(GradioRemoteError, match="Private or loopback"):
        validate_remote_url("https://attacker.example/latest/meta-data/", cfg)


def test_validate_remote_url_blocks_mixed_public_and_private_answers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import hedron_gradio.policy as policy

    def _getaddrinfo(
        host: str, port: object, *args: object, **kwargs: object
    ) -> list[tuple[Any, ...]]:
        del host, port, args, kwargs
        return _addrinfo_for("8.8.8.8") + _addrinfo_for("127.0.0.1")

    monkeypatch.setattr(policy.socket, "getaddrinfo", _getaddrinfo)
    cfg = GradioRemoteConfig.from_base_url("https://mixed.example")
    with pytest.raises(GradioRemoteError, match="resolved 127.0.0.1"):
        validate_remote_url("https://mixed.example/run", cfg)


def test_validate_remote_url_allows_private_dns_when_opted_in(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import hedron_gradio.policy as policy

    monkeypatch.setattr(
        policy.socket,
        "getaddrinfo",
        lambda host, port, *a, **k: _addrinfo_for("127.0.0.1"),
    )
    cfg = GradioRemoteConfig.from_base_url("https://internal.example", allow_private_hosts=True)
    validate_remote_url("https://internal.example/run", cfg)


def test_redact_sensitive_text() -> None:
    text = "Authorization: Bearer hf_abcdefghijklmnopqrstuvwxyz123456"
    assert "hf_" not in redact_sensitive_text(text)


def test_artifact_store_rejects_traversal_name() -> None:
    store = ArtifactStore(max_bytes=1024, retention_seconds=60.0)
    with pytest.raises(GradioRemoteError, match="Unsafe artifact name"):
        store.store("../secret.txt", b"x")


def test_artifact_store_enforces_max_bytes() -> None:
    store = ArtifactStore(max_bytes=8, retention_seconds=60.0)
    with pytest.raises(GradioRemoteError, match="exceeds max size"):
        store.store("sample.txt", b"0123456789")


def test_job_scope_isolation() -> None:
    manager = GradioJobManager(default_timeout_seconds=30.0)
    job_id = manager.submit("predict", {"x": 1}, scope_key=job_scope_key(tenant_id="a"))
    with pytest.raises(GradioRemoteError, match="scope mismatch"):
        manager.poll(job_id, scope_key=job_scope_key(tenant_id="b"))


def test_artifact_store_fails_closed_on_scope_mismatch() -> None:
    """#267: artifacts bind the same scope_key contract as jobs."""
    store = ArtifactStore(max_bytes=1024, retention_seconds=60.0)
    aid = store.store("secret.txt", b"tenant-a-secret", scope_key=job_scope_key(tenant_id="a"))
    assert store.fetch(aid, scope_key=job_scope_key(tenant_id="a")) == b"tenant-a-secret"
    with pytest.raises(GradioRemoteError, match="Artifact scope mismatch"):
        store.fetch(aid, scope_key=job_scope_key(tenant_id="b"))
    with pytest.raises(GradioRemoteError, match="Artifact scope mismatch"):
        store.delete(aid, scope_key=job_scope_key(tenant_id="b"))
    assert store.fetch(aid, scope_key=job_scope_key(tenant_id="a")) == b"tenant-a-secret"
    assert store.delete(aid, scope_key=job_scope_key(tenant_id="a")) is True


def test_adapter_download_artifact_fails_closed_after_principal_change() -> None:
    adapter = GradioClientAdapter(
        "https://demo.example.invalid",
        enabled=True,
        remote_config=GradioRemoteConfig.from_base_url("https://demo.example.invalid"),
        tenant_id="tenant-a",
        auth_subject="alice",
    )
    aid = adapter.upload_file("secret.txt", b"tenant-a-secret")
    assert adapter.download_artifact(aid) == b"tenant-a-secret"
    adapter.tenant_id = "tenant-b"
    adapter.auth_subject = "bob"
    with pytest.raises(GradioRemoteError, match="Artifact scope mismatch"):
        adapter.download_artifact(aid)


def test_hf_space_base_url_and_config() -> None:
    url = hf_space_base_url("org/demo")
    assert url == "https://org-demo.hf.space"
    config = hf_remote_config_for_space("org/demo")
    validate_remote_url(url, config)


def test_hf_fixture_translation() -> None:
    cold = translate_hf_vendor_status(load_hf_fixture("hf_space_cold_start.json"))
    assert cold["status"] == "pending"
    quota = translate_hf_vendor_status(load_hf_fixture("hf_quota_error.json"))
    assert quota["status"] == "failed"
    assert "hf_" not in quota["error"]


def test_discover_from_recorded_fixture_shape() -> None:
    payload = json.loads((FIXTURES / "view_api_minimal.json").read_text(encoding="utf-8"))

    class _FakeClient:
        def view_api(self, return_format: str = "dict") -> dict[str, object]:
            assert return_format == "dict"
            return payload

    adapter = GradioClientAdapter("https://demo.example.invalid", enabled=True)
    endpoints = adapter._endpoints_from_client(_FakeClient())
    assert endpoints[0].name == "predict"


def test_adapter_upload_respects_remote_config_limit() -> None:
    config = GradioRemoteConfig(
        base_url="https://demo.example.invalid",
        allowed_hosts=frozenset({"demo.example.invalid"}),
        max_upload_bytes=4,
    )
    adapter = GradioClientAdapter(
        "https://demo.example.invalid",
        enabled=True,
        remote_config=config,
        endpoints=(
            GradioEndpoint(name="predict", api_name="/predict", parameters={"text": "string"}),
        ),
    )
    with pytest.raises(GradioRemoteError, match="max_upload_bytes"):
        adapter.upload_file("sample.txt", b"012345")
