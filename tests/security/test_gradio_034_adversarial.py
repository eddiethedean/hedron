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
