"""Phase 0.34 Gradio production-grade behavior."""

from __future__ import annotations

import json
from pathlib import Path

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


def test_validate_remote_url_allows_declared_host() -> None:
    config = GradioRemoteConfig.from_base_url("https://demo.example.invalid")
    validate_remote_url("https://demo.example.invalid/predict", config)


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
