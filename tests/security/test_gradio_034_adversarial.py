"""Adversarial Gradio remote policy tests (EGRESS-034 / FILES-034)."""

from __future__ import annotations

import pytest

from hedron_gradio import GradioClientAdapter, GradioEndpoint, GradioRemoteError
from hedron_gradio.policy import GradioRemoteConfig, validate_remote_url


def test_disallowed_scheme_rejected() -> None:
    config = GradioRemoteConfig.from_base_url("https://demo.example.invalid")
    with pytest.raises(GradioRemoteError, match="scheme"):
        validate_remote_url("file:///etc/passwd", config, label="artifact")


def test_metadata_endpoint_blocked() -> None:
    config = GradioRemoteConfig.from_base_url("https://demo.example.invalid")
    with pytest.raises(GradioRemoteError, match="allowlist|Private"):
        validate_remote_url("https://169.254.169.254/latest/meta-data/", config)


def test_allowlisted_dns_to_metadata_is_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    """#268: hostname-only private checks cannot bypass link-local SSRF."""
    import socket

    import hedron_gradio.policy as policy

    monkeypatch.setattr(
        policy.socket,
        "getaddrinfo",
        lambda host, port, *a, **k: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("169.254.169.254", 0))
        ],
    )
    config = GradioRemoteConfig.from_base_url("https://attacker.example")
    with pytest.raises(GradioRemoteError, match="Private or loopback"):
        validate_remote_url("https://attacker.example/latest/meta-data/", config)


def test_adapter_requires_allowlisted_base_when_enabled() -> None:
    adapter = GradioClientAdapter(
        "https://allowed.example.invalid",
        enabled=True,
        remote_config=GradioRemoteConfig.from_base_url("https://allowed.example.invalid"),
        endpoints=(
            GradioEndpoint(name="predict", api_name="/predict", parameters={"text": "string"}),
        ),
    )
    adapter.discover()
    bad = GradioClientAdapter(
        "https://other.example.invalid",
        enabled=True,
        remote_config=GradioRemoteConfig.from_base_url("https://allowed.example.invalid"),
        endpoints=(
            GradioEndpoint(name="predict", api_name="/predict", parameters={"text": "string"}),
        ),
    )
    with pytest.raises(GradioRemoteError, match="allowlist"):
        bad.discover()


def test_path_traversal_artifact_id_rejected() -> None:
    adapter = GradioClientAdapter(
        "https://demo.example.invalid",
        enabled=True,
        remote_config=GradioRemoteConfig.from_base_url(
            "https://demo.example.invalid",
            allow_private_hosts=True,
        ),
        endpoints=(
            GradioEndpoint(name="predict", api_name="/predict", parameters={"text": "string"}),
        ),
    )
    file_id = adapter.upload_file("ok.txt", b"data")
    adapter.download_artifact(file_id)
    with pytest.raises(GradioRemoteError, match="Invalid artifact id"):
        adapter.download_artifact("../../../etc/passwd")


def test_artifact_download_fails_closed_across_tenant() -> None:
    """#267: shared ArtifactStore ids are not readable after a principal change."""
    adapter = GradioClientAdapter(
        "https://demo.example.invalid",
        enabled=True,
        remote_config=GradioRemoteConfig.from_base_url(
            "https://demo.example.invalid",
            allow_private_hosts=True,
        ),
        tenant_id="tenant-a",
        auth_subject="alice",
    )
    file_id = adapter.upload_file("secret.txt", b"tenant-a-secret")
    adapter.tenant_id = "tenant-b"
    adapter.auth_subject = "bob"
    with pytest.raises(GradioRemoteError, match="Artifact scope mismatch"):
        adapter.download_artifact(file_id)
