"""REMOTE-046: McpExposure and RemoteWorkflow are explicit opt-in."""

from __future__ import annotations

import pytest
from pydantic import BaseModel
from tests.unit._helpers_046 import make_app, reset_046

from hedron import Text
from hedron_core.bundles import FeatureConflictError
from hedron_core.codes import HED_BUNDLE_0002
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


def test_mcp_to_bundle_does_not_register_tools() -> None:
    projection = McpProjection(enabled=True)
    exposure = McpExposure(
        catalog_id="x",
        role="tool",
        projection=projection,
        name="echo_tool",
        authorize=lambda **k: None,
        schema={},
        handler=lambda: "ok",
    )
    exposure.to_bundle()
    assert projection.tools == ()


def test_mcp_double_include_keeps_one_tool() -> None:
    app = make_app()
    projection = McpProjection(enabled=True)

    def make() -> McpExposure:
        return McpExposure(
            catalog_id="x",
            role="tool",
            projection=projection,
            name="echo_tool",
            authorize=lambda **k: None,
            schema={},
            handler=lambda: "ok",
        )

    app.include_feature(make())
    app.include_feature(make())
    assert [tool.name for tool in projection.tools] == ["echo_tool"]


def test_mcp_duplicate_apply_is_feature_conflict() -> None:
    projection = McpProjection(enabled=True)
    exposure = McpExposure(
        catalog_id="x",
        role="tool",
        projection=projection,
        name="echo_tool",
        authorize=lambda **k: None,
        schema={},
        handler=lambda: "ok",
    )
    exposure.apply()
    with pytest.raises(FeatureConflictError) as raised:
        exposure.apply()
    assert raised.value.diagnostic.code == HED_BUNDLE_0002
    assert [tool.name for tool in projection.tools] == ["echo_tool"]


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


def test_mcp_second_exposure_keeps_first_tool_authorize() -> None:
    from hedron_mcp import AuthorizationError

    proj = McpProjection(enabled=True)

    def deny_admin(**kwargs: object) -> None:
        if kwargs.get("resource") == "admin_wipe":
            raise AuthorizationError("admin only")

    admin = McpExposure(
        catalog_id="admin",
        role="tool",
        projection=proj,
        name="admin_wipe",
        authorize=deny_admin,
        handler=lambda: "wiped",
        mutate=True,
        schema={},
    )
    read = McpExposure(
        catalog_id="list",
        role="tool",
        projection=proj,
        name="list_items",
        authorize=lambda **k: None,
        handler=lambda: [],
        schema={},
    )
    admin.apply()
    read.apply()
    with pytest.raises(AuthorizationError):
        proj.authorize(principal="alice", action="tools/call", resource="admin_wipe")
    proj.authorize(principal="alice", action="tools/call", resource="list_items")
    read.unapply()
    with pytest.raises(AuthorizationError):
        proj.authorize(principal="alice", action="tools/call", resource="admin_wipe")
    assert [tool.name for tool in proj.tools] == ["admin_wipe"]
