from __future__ import annotations

import asyncio

import pytest
from starlette.requests import Request

from hedron_core import (
    AppShell,
    AppShellChrome,
    DirtyScope,
    PageState,
    PrincipalContext,
    ResourceRef,
    SecretOperation,
    SecretUpdate,
    fetch_page,
    normalize_page,
    presentation_allowed,
    resolve_secret_update,
)
from hedron_core.builtins import Brand, Dialog, FormGrid, ProcessFlow, SecretField
from hedron_core.htmx.policy import InteractionResult
from hedron_core.theme_contract import ComputedStyleAssertion, evaluate_computed_style_assertions
from hedron_posit.urls import ExternalBase, RequestUrlFacade


def test_identity_and_pagination_contracts_fail_closed() -> None:
    principal = PrincipalContext("user-1", display_name="A")
    assert principal.authenticated
    page = normalize_page({"items": [1], "page": 1, "pages": 2, "total": 3})
    assert isinstance(page, PageState) and page.has_next
    assert ResourceRef("dataset", "one").type == "dataset"


def test_authorization_provider_is_presentation_only_and_fail_closed() -> None:
    class Provider:
        async def can(self, request, action, resource):
            return action == "read" and resource is not None

    assert asyncio.run(presentation_allowed(Provider(), None, "read", ResourceRef("x", "1")))
    assert not asyncio.run(presentation_allowed(None, None, "read"))


def test_secret_validation_dirty_scope_and_safe_error_sink() -> None:
    assert SecretUpdate(SecretOperation.KEEP).value is None
    with pytest.raises(ValueError):
        SecretUpdate(SecretOperation.REPLACE)
    scope = DirtyScope("settings")
    scope.mark_changed()
    assert scope.dirty
    scope.commit()
    assert not scope.dirty
    scope.assert_clean()
    scope.mark_changed()
    with pytest.raises(RuntimeError):
        scope.assert_clean()
    assert InteractionResult.error(status_code=422).retarget == "#hedron-errors"
    with pytest.raises(ValueError):
        InteractionResult.error(error_retarget="#arbitrary")


def test_phase_11_component_presentation_hooks_are_additive() -> None:
    assert (
        Brand("App", mark_appearance="plain", name_role="display").props.mark_appearance == "plain"
    )
    assert Dialog("Confirm", class_="compact", mark="confirm").props.class_ == "compact"
    assert FormGrid(alignment="natural").props.alignment == "natural"
    flow = ProcessFlow(label="Steps", appearance="plain")
    assert flow.props.appearance == "plain"
    assert SecretField("api_key", "API key", configured=True).props.configured


def test_app_shell_preserves_chrome_policy_attributes() -> None:
    shell = AppShell(
        chrome=AppShellChrome(
            header_inset="wide",
            footer_inset="compact",
            header_surface="glass",
            nav_toggle="icon",
            nav_footer_collapsed="hide",
        ),
        nav_collapse="user",
        nav=[],
    )
    attrs = shell.render().attributes
    assert attrs["data-hedron-shell-header-inset"] == "wide"
    assert attrs["data-hedron-shell-footer-inset"] == "compact"
    assert attrs["data-hedron-shell-header-surface"] == "glass"
    assert attrs["data-hedron-nav-toggle"] == "icon"
    assert attrs["data-hedron-nav-footer-collapsed"] == "hide"


def test_computed_style_evidence_requires_assertions_and_provenance() -> None:
    assert not evaluate_computed_style_assertions([]).passed
    assertion = ComputedStyleAssertion("Button", "display", "inline-flex", "inline-flex")
    assert not evaluate_computed_style_assertions((assertion,)).passed
    assert evaluate_computed_style_assertions(
        (assertion,), provenance={"runtime": "playwright", "asset": "test.css"}
    ).passed


def test_secret_field_exposes_clear_control_and_keep_default() -> None:
    field = SecretField("api_key", "API key", configured=True, allow_clear=True).render()
    hidden = next(
        child for child in field.children[2].children if child.attributes.get("type") == "hidden"
    )
    clear = next(
        child
        for child in field.children[2].children
        if child.attributes.get("data-hedron-secret-operation") == "clear"
    )
    assert hidden.attributes["value"] == "keep"
    assert clear.attributes["type"] == "submit"
    assert (
        resolve_secret_update({"api_key__clear": "1"}, "api_key").operation
        is SecretOperation.CLEAR
    )


def test_phase11_pagination_and_url_facade_are_provider_neutral() -> None:
    class Source:
        async def fetch(self, **kwargs):
            assert kwargs["page"] == 2
            return {"items": ["row"], "page": 2, "pages": 3}

    page = asyncio.run(fetch_page(Source(), page=2))
    assert tuple(page.items) == ("row",) and page.has_next

    request = Request({"type": "http", "path": "/", "root_path": "/app", "headers": []})
    facade = RequestUrlFacade(
        request=request,
        mount="/app",
        external=ExternalBase("https://example.test", "/app", "test"),
    )
    assert facade.navigation("/settings") == "/app/settings"
    assert facade.form_action("/save") == "/app/save"
    assert facade.location("/settings") == "https://example.test/app/settings"
    assert facade.hx_redirect("/settings") == "/settings"
