# Test your UI

Hedron components are deterministic Python objects, so most interface tests need neither
an ASGI server nor a browser. Add progressively broader tests only where HTTP or browser
behavior is part of the contract.

## Render a component

```python
from hedron import Card, Text
from hedron.testing import assert_renders, render_html


def test_welcome_card() -> None:
    card = Card(Text("Welcome, Ada"))

    assert_renders(card, contains="Welcome, Ada")
    assert "<script" not in render_html(card)
```

`render_html` is useful for focused assertions. `assert_renders` and
`assert_render_result` retain render metadata when assets or diagnostics are the behavior
under test.

## Exercise an HTMX fragment

```python
from hedron.testing import fragment_client


def test_home_fragment(app) -> None:
    with fragment_client(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "<html" not in response.text
```

The fragment client supplies the relevant HTMX request context so the test verifies the
fragment contract rather than an ordinary full-page response.

## Portable adapter harness (0.11)

For PAGE/FRAGMENT scenarios shared across FastAPI, Flask, and Django, use
`hedron.testing.adapters` (`fastapi_fixture` / `flask_fixture` / `django_fixture` plus
`assert_page_document` / `assert_fragment_body`). See [TESTING.md](../api/TESTING.md).

## Override FastAPI dependencies

```python
from hedron.testing import override_dependencies


def test_as_an_admin(app, current_user, fake_admin) -> None:
    with override_dependencies(app, {current_user: lambda: fake_admin}):
        # Make requests while the override is active.
        ...
```

The context manager restores `dependency_overrides` even if an assertion fails, keeping
tests isolated.

## Snapshot intentionally

Use `normalize_snapshot_html` only for documented nondeterminism. Prefer semantic
assertions for text, attributes, diagnostics, and assets; broad snapshots can obscure a
small but important accessibility or security regression.

Browser-level accessibility checks are available from `hedron.testing.browser` after
installing `hedron[browser]`. Keep those for interaction and platform behavior that a
render test cannot prove.

See the [testing API contract](../api/TESTING.md) for the complete helper inventory.
