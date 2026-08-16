"""UPDATE-043: portable Patch/PatchSet/RefreshIntent compilation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tests.unit._helpers_043 import reset_043

from hedron_core.codes import (
    HED_HOST_0001,
    HED_UPDATE_0001,
    HED_UPDATE_0002,
    HED_UPDATE_0003,
    HED_UPDATE_0004,
    HED_UPDATE_0005,
    HED_UPDATE_0006,
    HED_UPDATE_0007,
    HED_VIEW_0002,
    HED_VIEW_0004,
)
from hedron_core.diagnostics import HedronError
from hedron_core.hosts import FragmentHost
from hedron_core.html import html
from hedron_core.htmx.policy import FragmentRegion, InteractionResult, OobUpdate
from hedron_core.rendering import render
from hedron_core.updates import (
    MAX_PATCH_TARGETS,
    MAX_REFRESH_TARGETS,
    BaseHandleDescriptor,
    BindingPlan,
    Patch,
    PatchSet,
    PortableTarget,
    RefreshIntent,
    StructuralBindingAdapter,
    compile_to_interaction,
    descriptor_fingerprint,
    matches_declared_host,
    refresh_event_name,
    reset_handles_for_tests,
    safe_dom_id,
    structural_bind,
)


def setup_function() -> None:
    reset_043()
    reset_handles_for_tests()


def _target(*, app: str = "app-a", bound: bool = True, logical: str = "status") -> PortableTarget:
    dom = safe_dom_id(logical)
    return PortableTarget(
        logical_id=logical,
        dom_id=dom,
        path=f"/_hedron/views/{logical}",
        app_id=app,
        region=FragmentRegion(id=dom, selector=f"#{dom}"),
        bound=bound,
        selector=f"#{dom}",
    )


def test_refresh_intent_coalesces_and_compiles_trigger() -> None:
    target = _target()
    intent = RefreshIntent(targets=(target, target)).toast("ok")
    assert len(intent.targets) == 1
    result = compile_to_interaction(intent, expected_app_id="app-a")
    assert isinstance(result, InteractionResult)
    assert result.refresh is False
    event = refresh_event_name(target.dom_id)
    assert isinstance(result.trigger, dict)
    assert event in result.trigger
    assert result.oob
    assert result.oob[0].element_id == "hedron-toast"


def test_refresh_unbound_and_limit() -> None:
    with pytest.raises(HedronError) as unbound:
        RefreshIntent(targets=(_target(bound=False),))
    assert unbound.value.diagnostic.code == HED_UPDATE_0007
    targets = tuple(_target(logical=f"v{i}") for i in range(MAX_REFRESH_TARGETS + 1))
    with pytest.raises(HedronError) as over:
        RefreshIntent(targets=targets)
    assert over.value.diagnostic.code == HED_UPDATE_0004


def test_patchset_primary_oob_and_fail_closed_mix() -> None:
    primary = Patch(target=_target(), content=html.div("a"), swap="outerHTML")
    secondary = Patch(target=_target(logical="other"), content=html.div("b"), swap="innerHTML")
    compiled = compile_to_interaction(PatchSet(primary=primary, secondary=(secondary,)))
    assert isinstance(compiled, InteractionResult)
    assert compiled.retarget == "#h-view-status"
    assert compiled.swap == "outerHTML"
    assert compiled.oob[0].element_id == "h-view-other"
    mixed = InteractionResult(
        content=html.div("x"),
        trigger={refresh_event_name("h-view-status"): {}},
        oob=(OobUpdate(content=html.div("y"), element_id="other"),),
    )
    with pytest.raises(HedronError) as err:
        compile_to_interaction(mixed)
    assert err.value.diagnostic.code == HED_UPDATE_0001


def test_patch_duplicate_unsafe_swap_204_foreign() -> None:
    target = _target()
    patch = Patch(target=target, content="x")
    with pytest.raises(HedronError) as dup:
        PatchSet(primary=patch, secondary=(Patch(target=target, content="y"),))
    assert dup.value.diagnostic.code == HED_UPDATE_0002
    with pytest.raises(HedronError) as swap:
        Patch(target=target, content="x", swap="beforeend")  # type: ignore[arg-type]
    assert swap.value.diagnostic.code == HED_UPDATE_0005
    with pytest.raises(HedronError) as empty:
        PatchSet(primary=patch, secondary=(), status_code=204, toast="hi")
    assert empty.value.diagnostic.code == HED_UPDATE_0006
    other = Patch(target=_target(app="app-b"), content="z")
    with pytest.raises(HedronError) as foreign:
        compile_to_interaction(PatchSet(primary=patch, secondary=(other,)), expected_app_id="app-a")
    assert foreign.value.diagnostic.code == HED_UPDATE_0003
    with pytest.raises(HedronError) as unbound:
        Patch(target=_target(bound=False), content="x")
    assert unbound.value.diagnostic.code == HED_UPDATE_0007


def test_descriptor_fingerprint_ignores_extensions() -> None:
    base = BaseHandleDescriptor(logical_id="status", path="/x", app_id="a")
    extended = BaseHandleDescriptor(
        logical_id="status",
        path="/x",
        app_id="a",
        extensions={"hedron.type": {"schema": "TypeSchema"}},
    )
    assert descriptor_fingerprint(base) == descriptor_fingerprint(extended)
    with pytest.raises(HedronError) as override:
        BaseHandleDescriptor(
            logical_id="status",
            path="/x",
            extensions={"hedron.type": {"path": "/hijack"}},
        )
    assert override.value.diagnostic.code == HED_UPDATE_0003


def test_structural_bind_rejects_unknown_and_secrets() -> None:
    from hedron_core.security import Secret

    plan = BindingPlan(path_params=("item_id",), query_params=("q",), required=("item_id",))
    bound = StructuralBindingAdapter().bind(plan, {"item_id": "12"}, path="/v/{item_id}")
    assert bound.path == "/v/12"
    with pytest.raises(HedronError) as extra:
        structural_bind(plan, {"item_id": "1", "nope": "x"}, path="/v/{item_id}")
    assert extra.value.diagnostic.code == HED_VIEW_0004
    with pytest.raises(HedronError) as secret:
        structural_bind(plan, {"item_id": Secret("abc")}, path="/v/{item_id}")
    assert secret.value.diagnostic.code == HED_VIEW_0004


def test_fragment_host_allowlist_and_duplicate_mount() -> None:
    with pytest.raises(HedronError) as tag:
        FragmentHost(html.div("x"), tag="script")
    assert tag.value.diagnostic.code == HED_HOST_0001
    with pytest.raises(HedronError) as attr:
        FragmentHost(html.div("x"), attrs={"onclick": "alert(1)"})
    assert attr.value.diagnostic.code == HED_HOST_0001
    host = FragmentHost(
        html.div("ok"),
        dom_id="h-view-status",
        get_url="/x",
        event_name="hedron:refresh-h-view-status",
    )
    markup = render(host).html
    assert 'id="h-view-status"' in markup
    assert 'hx-trigger="hedron:refresh-h-view-status from:body"' in markup
    assert 'aria-busy="false"' in markup
    with pytest.raises(HedronError) as dup:
        render(html.div(host, FragmentHost(html.div("y"), dom_id="h-view-status")))
    assert dup.value.diagnostic.code == HED_VIEW_0002


def test_matches_declared_host_instances() -> None:
    region = FragmentRegion(id="h-view-status", selector="#h-view-status")
    user = FragmentRegion(id="h-view-user", selector="#h-view-user")
    token = "a" * 20
    assert matches_declared_host(region, None)
    assert matches_declared_host(region, "h-view-status")
    assert matches_declared_host(region, f"#h-view-status-{token}")
    assert not matches_declared_host(region, "#h-view-status-abc")
    assert not matches_declared_host(user, "#h-view-user-admin")
    assert not matches_declared_host(region, "#evil")


def test_conformance_fixture_file_covers_adversarial_cases() -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "packages"
        / "hedron-conformance"
        / "src"
        / "hedron_conformance"
        / "fixtures"
        / "updates_043"
        / "cases.json"
    )
    data = json.loads(path.read_text(encoding="utf-8"))
    ids = {row["id"] for row in data}
    assert {
        "refresh-ok",
        "foreign-handle",
        "unbound-target",
        "duplicate-patch-target",
        "unsafe-swap",
        "status-204-oob",
        "oversize-fan-out",
    } <= ids


def test_patch_limit() -> None:
    primary = Patch(target=_target(), content="a")
    extras = tuple(
        Patch(target=_target(logical=f"p{i}"), content="x") for i in range(MAX_PATCH_TARGETS)
    )
    with pytest.raises(HedronError) as err:
        PatchSet(primary=primary, secondary=extras)
    assert err.value.diagnostic.code == HED_UPDATE_0004
