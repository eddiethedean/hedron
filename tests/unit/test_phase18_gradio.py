"""Phase 0.18 Gradio client interop (GRADIO-018, MIGRATE-018)."""

from __future__ import annotations

import pytest

from hedron_gradio import (
    GradioClientAdapter,
    GradioEndpoint,
    GradioRemoteError,
    HuggingFaceVendorNode,
    __version__,
    hf_space_node,
)
from hedron_gradio.migration import GRADIO_NON_PARITY, diagnose


def test_package_version() -> None:
    assert __version__ == "0.2.0"


def test_disabled_adapter_discover_empty() -> None:
    adapter = GradioClientAdapter("http://127.0.0.1:7860")
    assert adapter.enabled is False
    assert adapter.discover() == []


def test_version_mismatch_error() -> None:
    adapter = GradioClientAdapter(
        "http://127.0.0.1:7860",
        enabled=True,
        gradio_version="6.22.0",
    )
    adapter.check_version_compat("6.22.0")
    with pytest.raises(GradioRemoteError, match="outside supported range"):
        adapter.check_version_compat("6.16.0")
    with pytest.raises(GradioRemoteError, match="outside supported major"):
        adapter.check_version_compat("5.0.0")


def test_predict_job_stream_with_preloaded_endpoints() -> None:
    endpoints = (
        GradioEndpoint(
            name="predict",
            api_name="/predict",
            parameters={"type": "object", "properties": {"text": {"type": "string"}}},
            supports_stream=True,
        ),
    )
    adapter = GradioClientAdapter(
        "http://127.0.0.1:7860",
        enabled=True,
        endpoints=endpoints,
        gradio_version="6.22.0",
    )
    assert [endpoint.name for endpoint in adapter.discover()] == ["predict"]

    result = adapter.predict("predict", {"text": "hello"})
    assert result["status"] == "ok"
    assert result["payload"] == {"text": "hello"}

    job_id = adapter.submit_job("predict", {"text": "queued"})
    status = adapter.job_status(job_id)
    assert status["status"] == "complete"
    assert status["result"]["payload"] == {"text": "queued"}
    assert adapter.cancel_job(job_id) is False

    chunks = list(adapter.stream_results("predict", {"text": "stream"}))
    assert len(chunks) == 2
    assert chunks[-1]["done"] is True

    file_id = adapter.upload_file("sample.txt", b"data")
    assert adapter.download_artifact(file_id) == b"data"


def test_hf_vendor_node_to_workflow_node() -> None:
    node = hf_space_node("demo-space", "org/demo")
    workflow = node.to_workflow_node()
    assert workflow["node_id"] == "demo-space"
    assert workflow["kind"] == "remote"
    assert workflow["action_id"] == "hf:space:org/demo"
    assert workflow["label"]
    assert len(workflow["ports"]) == 2

    dataset = HuggingFaceVendorNode(node_id="ds", kind="dataset", ref="org/data")
    assert dataset.to_workflow_node()["kind"] == "dataset"
    assert dataset.to_workflow_node()["action_id"] == "hf:dataset:org/data"
    assert dataset.to_workflow_node()["node_id"] == "ds"


def test_disabled_file_apis_refuse() -> None:
    adapter = GradioClientAdapter("http://127.0.0.1:7860", enabled=False)
    with pytest.raises(GradioRemoteError, match="disabled"):
        adapter.upload_file("x.txt", b"data")
    with pytest.raises(GradioRemoteError, match="disabled"):
        adapter.download_artifact("missing")


def test_discover_via_transport_and_client_shape() -> None:
    endpoints = (
        GradioEndpoint(name="predict", api_name="/predict", parameters={"text": "string"}),
    )

    def transport(op: str, **_: object) -> object:
        if op == "discover":
            return list(endpoints)
        raise AssertionError(op)

    adapter = GradioClientAdapter(
        "http://127.0.0.1:7860",
        enabled=True,
        _transport=transport,
    )
    assert [e.name for e in adapter.discover()] == ["predict"]

    class _FakeClient:
        def view_api(self, return_format: str = "dict") -> dict[str, object]:
            assert return_format == "dict"
            return {
                "named_endpoints": {
                    "/classify": {
                        "name": "classify",
                        "parameters": {"text": {"type": "string"}},
                        "supports_stream": False,
                    }
                }
            }

    discovered = GradioClientAdapter("http://127.0.0.1:7860", enabled=True)._endpoints_from_client(
        _FakeClient()
    )
    assert discovered[0].name == "classify"
    assert discovered[0].api_name == "/classify"


def test_migration_diagnose_mentions_share_links_and_raw_js() -> None:
    assert any("share link" in item for item in GRADIO_NON_PARITY)
    assert any("raw" in item.lower() and "js" in item.lower() for item in GRADIO_NON_PARITY)

    findings = diagnose(
        {
            "share_link": True,
            "custom_js": "alert('x')",
            "notes": "uses share link in dev",
        }
    )
    joined = "\n".join(findings).lower()
    assert "share link" in joined
    assert "raw js" in joined


def test_hedron_core_imports_without_hedron_gradio() -> None:
    """Core must not require hedron-gradio; the adapter is an optional plugin."""
    try:
        import hedron_core
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"hedron_core import unavailable in this workspace: {exc}")
    assert hasattr(hedron_core, "__version__")
    try:
        import hedron_gradio  # noqa: F401
    except ImportError:
        pytest.skip("hedron-gradio not installed in this environment")
