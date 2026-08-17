"""REMOTE-046: McpExposure and RemoteWorkflow are explicit opt-in."""

from __future__ import annotations

import pytest
from pydantic import BaseModel
from tests.unit._helpers_046 import make_app, reset_046

from hedron import Text
from hedron_core.bundles import FeatureConflictError
from hedron_gradio import GradioClientAdapter, GradioEndpoint, GradioRemoteConfig, RemoteWorkflow
from hedron_mcp import McpExposure, McpProjection


def setup_function() -> None:
    reset_046()


class Payload(BaseModel):
    q: str = "ok"


def test_mcp_consume_catalog_does_not_expose() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    projection = McpProjection(enabled=False)
    ids = projection.consume_catalog(app.interactions)
    assert status.logical_id in ids
    assert projection.tools == ()
    assert projection.resources == ()


def test_mcp_exposure_registers_tool_with_live_authz() -> None:
    app = make_app()

    @app.command("/echo")
    def echo(data: Payload):
        return Text(data.q)

    calls: list[str] = []

    def authorize(*, principal: str | None, action: str, **kwargs: object) -> None:
        del kwargs
        calls.append(f"{principal}:{action}")

    projection = McpProjection(enabled=True, authz_hook=authorize)
    exposure = McpExposure(
        catalog_id=echo.logical_id,
        role="tool",
        projection=projection,
        name="echo_tool",
        authorize=authorize,
        schema={"type": "object"},
        handler=lambda: "ok",
    )
    app.include_feature(exposure)
    assert any(tool.name == "echo_tool" for tool in projection.tools)


def test_remote_workflow_requires_enabled_adapter() -> None:
    endpoint = GradioEndpoint(name="predict", api_name="/predict", parameters={})
    adapter = GradioClientAdapter(
        base_url="https://example.invalid", enabled=False, endpoints=(endpoint,)
    )
    with pytest.raises(FeatureConflictError):
        RemoteWorkflow(adapter=adapter, endpoint=endpoint, input_model=Payload, outcomes={})


def test_remote_workflow_include() -> None:
    app = make_app()
    endpoint = GradioEndpoint(name="predict", api_name="/predict", parameters={})
    adapter = GradioClientAdapter(
        base_url="https://example.invalid",
        enabled=True,
        endpoints=(endpoint,),
        remote_config=GradioRemoteConfig.from_base_url(
            "https://example.invalid", extra_hosts=("example.invalid",)
        ),
    )
    workflow = RemoteWorkflow(
        adapter=adapter,
        endpoint=endpoint,
        input_model=Payload,
        outcomes={"ok": "ok"},
        name="tests:gradio-predict",
    )
    app.include_feature(workflow)
    assert any(
        item.namespace.startswith("hedron.gradio.workflow")
        for item in app.interactions.catalog_projections.values()
    )


def _enabled_adapter(endpoints: tuple[GradioEndpoint, ...]) -> GradioClientAdapter:
    return GradioClientAdapter(
        base_url="https://example.invalid",
        enabled=True,
        endpoints=endpoints,
        remote_config=GradioRemoteConfig.from_base_url(
            "https://example.invalid", extra_hosts=("example.invalid",)
        ),
    )


def test_remote_workflow_empty_endpoints_fails_closed() -> None:
    endpoint = GradioEndpoint(name="secret-predict", api_name="/predict", parameters={})
    with pytest.raises(FeatureConflictError) as raised:
        RemoteWorkflow(
            adapter=_enabled_adapter(()),
            endpoint=endpoint,
            input_model=Payload,
            outcomes={},
        )
    from hedron_core.codes import HED_BUNDLE_0007

    assert raised.value.diagnostic.code == HED_BUNDLE_0007


def test_remote_workflow_rejects_endpoint_outside_allowlist() -> None:
    endpoint = GradioEndpoint(name="secret-predict", api_name="/predict", parameters={})
    allowed = GradioEndpoint(name="public-predict", api_name="/predict", parameters={})
    with pytest.raises(FeatureConflictError) as raised:
        RemoteWorkflow(
            adapter=_enabled_adapter((allowed,)),
            endpoint=endpoint,
            input_model=Payload,
            outcomes={},
        )
    from hedron_core.codes import HED_BUNDLE_0007

    assert raised.value.diagnostic.code == HED_BUNDLE_0007
