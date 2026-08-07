"""Behavioral contracts for every docs ``hedron-sim`` island.

Imported by unit + browser tests (not shipped to readers). Keep ``CONTRACTS``
in sync with ``docs/includes/sim/*.html`` — the completeness test enforces that.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from demos.components import COMPONENT_DEMO_BUILDERS
from demos.core_concepts import build_core_concepts_modes_demo
from demos.guides import (
    build_allowlist_403_demo,
    build_charts_htmx_demo,
    build_cookbook_oob_demo,
    build_crud_demo,
    build_forms_invite_demo,
    build_htmx_interactions_demo,
    build_live_poll_demo,
    build_mutations_htmx_demo,
)
from demos.hello_refresh import build_hello_refresh_demo

__all__ = ["CONTRACTS", "DemoContract", "Step", "contract_ids"]


@dataclass(frozen=True)
class Step:
    """One browser interaction against a sim island."""

    fill: dict[str, str] = field(default_factory=dict)
    click: str | None = None
    """Playwright selector scoped to the demo root when possible."""
    confirm: bool | None = None
    """If set, handle the next ``dialog`` (True=accept, False=dismiss)."""
    wait_ms: int = 600
    expect_text: str | None = None
    contains: str | None = None
    expect_trace: str | None = None
    auto: bool = False
    """Wait for ``contains`` without clicking (lazy / poll boot)."""


@dataclass(frozen=True)
class DemoContract:
    id: str
    builder: Callable[[], str]
    steps: tuple[Step, ...]
    mode_demo: bool = False
    """True for PAGE/FRAGMENT toggle demos (no route table)."""


def _btn(label: str) -> str:
    return f'button:has-text("{label}")'


def _link(label: str) -> str:
    return f'a:has-text("{label}")'


CONTRACTS: tuple[DemoContract, ...] = (
    DemoContract(
        id="hello-refresh",
        builder=lambda: build_hello_refresh_demo(status_id="service-status"),
        steps=(
            Step(
                click=_btn("Refresh status"),
                expect_text="[data-hbs-stamp]",
                contains="UTC",
                expect_trace="GET /status → 200",
            ),
        ),
    ),
    DemoContract(
        id="hello-refresh-quickstart",
        builder=lambda: build_hello_refresh_demo(
            status_id="qs-service-status",
            logo_src="../assets/hedron-mark.svg",
        ),
        steps=(
            Step(
                click=_btn("Refresh status"),
                expect_text="[data-hbs-stamp]",
                contains="UTC",
                expect_trace="GET /status → 200",
            ),
        ),
    ),
    DemoContract(
        id="htmx-interactions",
        builder=build_htmx_interactions_demo,
        steps=(
            Step(
                click=_btn("Refresh status"),
                expect_trace="GET /status → 200",
                expect_text="#hx-guide-status",
                contains="Service healthy",
            ),
            Step(
                click=_btn("Wrong #panel → 403"),
                expect_trace="403",
            ),
        ),
    ),
    DemoContract(
        id="forms-invite",
        builder=build_forms_invite_demo,
        steps=(
            Step(
                fill={"#invite-email": "nope"},
                click=_btn("Send invite"),
                expect_text="#invite-form",
                contains="valid work email",
                expect_trace="422",
            ),
            Step(
                fill={"#invite-email": "ada@example.com"},
                click=_btn("Send invite"),
                expect_text="#invite-form",
                contains="Invite sent",
                expect_trace="200",
            ),
        ),
    ),
    DemoContract(
        id="live-poll",
        builder=build_live_poll_demo,
        steps=(
            Step(
                click=_btn("Start job poll"),
                expect_text="#job-panel",
                contains="Queued",
                expect_trace="GET /jobs/42 → 200",
            ),
        ),
    ),
    DemoContract(
        id="cookbook-oob",
        builder=build_cookbook_oob_demo,
        steps=(
            Step(
                click=_btn("Save settings"),
                expect_text="#settings-main",
                contains="Settings saved",
                expect_trace="POST /settings → 200",
            ),
        ),
    ),
    DemoContract(
        id="allowlist-403",
        builder=build_allowlist_403_demo,
        steps=(
            Step(
                click=_btn("Correct #service-status → 200"),
                expect_trace="200",
            ),
            Step(
                click=_btn("Wrong #panel → 403"),
                expect_trace="403",
            ),
        ),
    ),
    DemoContract(
        id="charts-htmx",
        builder=build_charts_htmx_demo,
        steps=(
            Step(
                click=_btn("Refresh chart panel"),
                expect_text="#chart-panel",
                contains="Fragment refresh #2",
                expect_trace="GET /charts/refresh → 200",
            ),
        ),
    ),
    DemoContract(
        id="crud-notes",
        builder=build_crud_demo,
        steps=(
            Step(
                fill={"#crud-note": "hello"},
                click=_btn("Add note"),
                expect_text="#notes-list",
                contains="hello",
                expect_trace="POST /notes → 200",
            ),
            Step(
                click=_btn("Delete"),
                expect_text="#notes-list",
                contains="No notes yet",
                expect_trace="DELETE /notes/1 → 200",
            ),
        ),
    ),
    DemoContract(
        id="mutations-htmx",
        builder=build_mutations_htmx_demo,
        steps=(
            Step(
                click=_btn("Save"),
                expect_text="#save-result",
                contains="Saved",
                expect_trace="POST /save → 200",
            ),
        ),
    ),
    DemoContract(
        id="core-concepts-modes",
        builder=build_core_concepts_modes_demo,
        mode_demo=True,
        steps=(
            Step(
                click=_btn("FRAGMENT"),
                expect_text="[data-sim-mode-status]",
                contains="FRAGMENT",
            ),
            Step(
                click=_btn("PAGE"),
                expect_text="[data-sim-mode-status]",
                contains="PAGE",
            ),
        ),
    ),
    DemoContract(
        id="component-refresh",
        builder=COMPONENT_DEMO_BUILDERS["component-refresh"],
        steps=(
            Step(
                click=_btn("Refresh status"),
                expect_trace="GET /status → 200",
                expect_text="#status-card",
                contains="Service healthy",
            ),
        ),
    ),
    DemoContract(
        id="component-lazy",
        builder=COMPONENT_DEMO_BUILDERS["component-lazy"],
        steps=(
            Step(
                auto=True,
                wait_ms=800,
                expect_text="#lazy-box",
                contains="3 recent events",
                expect_trace="200",
            ),
        ),
    ),
    DemoContract(
        id="component-poll",
        builder=COMPONENT_DEMO_BUILDERS["component-poll"],
        steps=(
            Step(
                auto=True,
                wait_ms=3500,
                expect_text="#poll-box",
                contains="Complete",
                expect_trace="200",
            ),
        ),
    ),
    DemoContract(
        id="component-infinite",
        builder=COMPONENT_DEMO_BUILDERS["component-infinite"],
        steps=(
            Step(
                click=':text("Load more")',
                expect_text="#event-feed",
                contains="Tests passed",
                expect_trace="GET /events → 200",
            ),
        ),
    ),
    DemoContract(
        id="component-pagination",
        builder=COMPONENT_DEMO_BUILDERS["component-pagination"],
        steps=(
            Step(
                click='a[aria-label="Page 2"]',
                expect_text="#page-results",
                contains="Results 4–6",
                expect_trace="GET /results?page=2 → 200",
            ),
        ),
    ),
    DemoContract(
        id="component-error",
        builder=COMPONENT_DEMO_BUILDERS["component-error"],
        steps=(
            Step(
                click=_btn("Retry"),
                expect_trace="GET /activity → 200",
            ),
        ),
    ),
    DemoContract(
        id="component-form",
        builder=COMPONENT_DEMO_BUILDERS["component-form"],
        steps=(
            Step(
                fill={'input[name="email"]': "ada@example.com"},
                click=_btn("Submit"),
                expect_text="#demo-form",
                contains="Submitted",
                expect_trace="200",
            ),
        ),
    ),
    DemoContract(
        id="component-auto-form",
        builder=COMPONENT_DEMO_BUILDERS["component-auto-form"],
        steps=(
            Step(
                fill={'input[name="email"]': "ada@example.com"},
                click=_btn("Submit"),
                expect_text="#demo-form",
                contains="Submitted",
                expect_trace="200",
            ),
        ),
    ),
    DemoContract(
        id="component-app-shell",
        builder=COMPONENT_DEMO_BUILDERS["component-app-shell"],
        steps=(
            Step(
                click=_link("Reports"),
                expect_trace="GET /reports → 200",
            ),
        ),
    ),
    DemoContract(
        id="component-main-panel",
        builder=COMPONENT_DEMO_BUILDERS["component-main-panel"],
        steps=(
            Step(
                click=_link("Reports"),
                expect_trace="GET /reports → 200",
            ),
        ),
    ),
    DemoContract(
        id="component-nav-link",
        builder=COMPONENT_DEMO_BUILDERS["component-nav-link"],
        steps=(
            Step(
                click=_link("Home"),
                expect_trace="GET /home → 200",
            ),
        ),
    ),
    DemoContract(
        id="component-htmx-link",
        builder=COMPONENT_DEMO_BUILDERS["component-htmx-link"],
        steps=(
            Step(
                click=_link("Reports"),
                expect_trace="GET /reports → 200",
            ),
        ),
    ),
    DemoContract(
        id="component-oob-host",
        builder=COMPONENT_DEMO_BUILDERS["component-oob-host"],
        steps=(
            Step(
                click=_btn("Save"),
                expect_trace="POST /profile → 200",
            ),
        ),
    ),
    DemoContract(
        id="component-attr-host",
        builder=COMPONENT_DEMO_BUILDERS["component-attr-host"],
        steps=(
            Step(
                click=_btn("Run attribute OOB"),
                expect_trace="GET /status-attrs → 200",
            ),
        ),
    ),
    DemoContract(
        id="component-loading",
        builder=COMPONENT_DEMO_BUILDERS["component-loading"],
        steps=(
            Step(
                click=_btn("Load activity"),
                expect_trace="GET /activity → 200",
            ),
        ),
    ),
    DemoContract(
        id="component-form-errors",
        builder=COMPONENT_DEMO_BUILDERS["component-form-errors"],
        steps=(
            Step(
                click=_btn("Submit empty form"),
                expect_trace="422",
            ),
        ),
    ),
    DemoContract(
        id="component-fragment",
        builder=COMPONENT_DEMO_BUILDERS["component-fragment"],
        steps=(
            Step(
                click=_btn("Refresh fragment"),
                expect_trace="GET /profile-fragment → 200",
            ),
        ),
    ),
    DemoContract(
        id="component-skeleton",
        builder=COMPONENT_DEMO_BUILDERS["component-skeleton"],
        steps=(
            Step(
                click=_btn("Load profile"),
                expect_trace="GET /profile → 200",
            ),
        ),
    ),
    DemoContract(
        id="component-toast",
        builder=COMPONENT_DEMO_BUILDERS["component-toast"],
        steps=(
            Step(
                click=_btn("Copy API key"),
                expect_trace="POST /copy-key → 200",
            ),
        ),
    ),
    DemoContract(
        id="component-confirm",
        builder=COMPONENT_DEMO_BUILDERS["component-confirm"],
        steps=(
            Step(
                click=_btn("Delete item"),
                confirm=True,
                expect_text="#confirm-row",
                contains="Item deleted",
                expect_trace="DELETE /items/1 → 200",
            ),
        ),
    ),
)


def contract_ids() -> frozenset[str]:
    return frozenset(c.id for c in CONTRACTS)
