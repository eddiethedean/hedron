"""Regression coverage for Edron dependency lowering and action binding."""

from __future__ import annotations

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

import edron as ed
from edron.errors import BindingError
from hedron import ActionHandle, FragmentHandle


def test_surfaces_use_hedron_1_0_canonical_handles() -> None:
    app = ed.App(title="canonical", session_secret="test-secret")

    @app.page("/", title="Home")
    class Home(ed.Page):
        @ed.fragment
        def status(self) -> None:
            self.text("ready")

        @ed.action
        def save(self) -> ed.Outcome:
            return ed.refresh(self.status)

        def render(self) -> None:
            self.status()
            self.button("Save", action=self.save)

    fragment = app.native_surface(Home.status)
    action = app.native_surface(Home.save)
    assert isinstance(fragment, FragmentHandle)
    assert isinstance(action, ActionHandle)
    assert fragment is Home.status._native
    assert action is Home.save._native
    assert app.native.state.hedron_handles[fragment.logical_id] is fragment
    assert app.native.state.hedron_handles[action.logical_id] is action


def test_fragment_dependencies_are_lowered_to_native_route() -> None:
    calls: list[str] = []

    def provide_label() -> str:
        calls.append("called")
        return "from dependency"

    app = ed.App(title="dependencies", session_secret="test-secret")

    @app.page("/", title="Home")
    class Home(ed.Page):
        @ed.fragment(dependencies=(Depends(provide_label),))
        def status(self) -> None:
            self.text("fragment")

        def render(self) -> None:
            self.status()

    response = TestClient(app.native).get("/__edron/status")
    assert response.status_code == 200
    assert "fragment" in response.text
    assert calls == ["called"]


def test_action_binding_is_encoded_in_action_control() -> None:
    app = ed.App(title="binding", session_secret="test-secret")

    @app.page("/", title="Home")
    class Home(ed.Page):
        @ed.action
        def archive(self, item_id: int) -> ed.Outcome:
            return ed.success(str(item_id))

        def render(self) -> None:
            self.button("Archive", action=self.archive.bind(item_id=42))

    response = TestClient(app.native).get("/")
    assert response.status_code == 200
    assert 'hx-post="/__edron/archive?item_id=42"' in response.text


def test_action_binding_quotes_path_values_and_preserves_queries() -> None:
    app = ed.App(title="binding", session_secret="test-secret")

    @app.page("/", title="Home")
    class Home(ed.Page):
        @ed.action(path="/__edron/archive/{item_id:path}?source=button")
        def archive(self, item_id: str) -> None:
            return None

        def render(self) -> None:
            self.button("Archive", action=self.archive.bind(item_id="a/b"))

    response = TestClient(app.native).get("/")
    assert response.status_code == 200
    assert 'hx-post="/__edron/archive/a%2Fb?source=button"' in response.text


def test_action_binding_rejects_unknown_and_dependency_arguments() -> None:
    app = ed.App(title="binding", session_secret="test-secret")

    @app.page("/", title="Home")
    class Home(ed.Page):
        @ed.action
        def archive(self, item_id: int, user: str = Depends(lambda: "server")) -> None:
            return None

        def render(self) -> None:
            self.text("Home")

    with pytest.raises(BindingError, match="unknown action argument"):
        Home.archive.bind(unknown=1)
    with pytest.raises(BindingError, match="unknown action argument"):
        Home.archive.bind(user="forged")
