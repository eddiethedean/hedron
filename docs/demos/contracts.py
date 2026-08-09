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
    build_auth_login_demo,
    build_charts_htmx_demo,
    build_cookbook_oob_demo,
    build_crud_demo,
    build_csrf_guard_demo,
    build_data_table_filter_demo,
    build_file_upload_demo,
    build_forms_invite_demo,
    build_htmx_interactions_demo,
    build_jobs_poll_demo,
    build_live_poll_demo,
    build_minimal_form_demo,
    build_mutations_htmx_demo,
    build_pe_paths_demo,
    build_tenant_deny_demo,
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
    contains_all: tuple[str, ...] = ()
    """Every string must appear in ``expect_text`` (or the sim root)."""
    not_contains: str | None = None
    expect_trace: str | None = None
    auto: bool = False
    """Wait for ``contains`` / ``expect_trace`` without clicking (lazy / poll boot)."""


@dataclass(frozen=True)
class DemoContract:
    id: str
    builder: Callable[[], str]
    steps: tuple[Step, ...]
    mode_demo: bool = False
    """True for PAGE/FRAGMENT toggle demos (no route table)."""
    min_steps: int = 1
    """Structural floor — browser suite also enforces ``len(steps) >= min_steps``."""


def _btn(label: str) -> str:
    return f'button:has-text("{label}")'


def _link(label: str) -> str:
    return f'a:has-text("{label}")'


CONTRACTS: tuple[DemoContract, ...] = (
    DemoContract(
        id="hello-refresh",
        builder=lambda: build_hello_refresh_demo(
            status_id="service-status",
            logo_src="assets/hedron-mark.svg",
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
        id="hello-refresh-quickstart",
        builder=lambda: build_hello_refresh_demo(
            status_id="qs-service-status",
            logo_src="../assets/hedron-mark.svg",
            caption=(
                "Docs simulation — click <strong>Refresh status</strong> for an "
                "HTMX-style fragment swap (no server)."
            ),
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
        min_steps=3,
        steps=(
            Step(
                click=_btn("Refresh status"),
                expect_trace="GET /status → 200",
                expect_text="#hx-guide-status",
                contains="Service healthy",
            ),
            Step(
                click=_btn("Correct target → 200"),
                expect_trace="GET /probe → 200",
                expect_text="#hx-guide-probe",
                contains="Allowlisted swap",
            ),
            Step(
                click=_btn("Wrong #panel → 403"),
                expect_trace="403",
                expect_text="#hx-guide-probe",
                contains="Allowlisted swap",
            ),
        ),
    ),
    DemoContract(
        id="forms-invite",
        builder=build_forms_invite_demo,
        min_steps=2,
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
                contains_all=("ada@example.com",),
                expect_trace="200",
            ),
        ),
    ),
    DemoContract(
        id="live-poll",
        builder=build_live_poll_demo,
        min_steps=5,
        steps=(
            Step(
                click=_btn("Start job poll"),
                expect_text="#job-panel",
                contains="Queued",
                expect_trace="GET /jobs/42 → 200",
            ),
            Step(
                click=_btn("Start job poll"),
                expect_text="#job-panel",
                contains="Step 1 of 2",
                expect_trace="200",
            ),
            Step(
                click=_btn("Start job poll"),
                expect_text="#job-panel",
                contains="Step 2 of 2",
                expect_trace="200",
            ),
            Step(
                click=_btn("Start job poll"),
                expect_text="#job-panel",
                contains="Complete",
                expect_trace="200",
            ),
            Step(
                click=_btn("Start job poll"),
                expect_text="#job-panel",
                contains="Queued",
                expect_trace="200",
            ),
        ),
    ),
    DemoContract(
        id="cookbook-oob",
        builder=build_cookbook_oob_demo,
        min_steps=1,
        steps=(
            Step(
                click=_btn("Save settings"),
                expect_text="[data-hedron-sim]",
                contains="Settings saved",
                contains_all=("Out-of-band update", "Saved"),
                expect_trace="POST /settings → 200",
            ),
        ),
    ),
    DemoContract(
        id="allowlist-403",
        builder=build_allowlist_403_demo,
        min_steps=2,
        steps=(
            Step(
                click=_btn("Correct #service-status → 200"),
                expect_text="#service-status",
                contains="Allowlisted swap",
                expect_trace="200",
            ),
            Step(
                click=_btn("Wrong #panel → 403"),
                expect_text="#service-status",
                contains="Allowlisted swap",
                expect_trace="403",
            ),
        ),
    ),
    DemoContract(
        id="charts-htmx",
        builder=build_charts_htmx_demo,
        min_steps=4,
        steps=(
            Step(
                click=_btn("Refresh chart panel"),
                expect_text="#chart-panel",
                contains="Fragment refresh #2",
                expect_trace="GET /charts/refresh → 200",
            ),
            Step(
                click=_btn("Refresh chart panel"),
                expect_text="#chart-panel",
                contains="Fragment refresh #3",
                expect_trace="200",
            ),
            Step(
                click=_btn("Refresh chart panel"),
                expect_text="#chart-panel",
                contains="Fragment refresh #4",
                expect_trace="200",
            ),
            Step(
                click=_btn("Refresh chart panel"),
                expect_text="#chart-panel",
                contains="Fragment refresh #2",
                expect_trace="200",
            ),
        ),
    ),
    DemoContract(
        id="crud-notes",
        builder=build_crud_demo,
        min_steps=3,
        steps=(
            Step(
                fill={"#crud-note": "hello"},
                click=_btn("Add note"),
                expect_text="#notes-list",
                contains="hello",
                expect_trace="POST /notes → 200",
            ),
            Step(
                fill={"#crud-note": "second"},
                click=_btn("Add note"),
                expect_text="#notes-list",
                contains="second",
                contains_all=("hello",),
                expect_trace="POST /notes → 200",
            ),
            Step(
                click='button[data-hedron-sim-list-index="0"]',
                expect_text="#notes-list",
                contains="second",
                not_contains="hello",
                expect_trace="DELETE /notes/item → 200",
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
                contains_all=("Ship the docs demo",),
                expect_trace="POST /save → 200",
            ),
        ),
    ),
    DemoContract(
        id="minimal-form",
        builder=build_minimal_form_demo,
        min_steps=1,
        steps=(
            Step(
                click=_btn("Save"),
                expect_text="#notes-stage",
                contains="Notes saved: 1",
                contains_all=("Leave a note",),
                expect_trace="POST /save → 200",
            ),
        ),
    ),
    DemoContract(
        id="auth-login",
        builder=build_auth_login_demo,
        min_steps=4,
        steps=(
            Step(
                fill={"#auth-password": "wrong"},
                click=_btn("Sign in"),
                expect_text="#auth-panel",
                contains="Invalid username or password",
                expect_trace="401",
            ),
            Step(
                fill={"#auth-password": "correct-horse"},
                click=_btn("Sign in"),
                expect_text="#auth-panel",
                contains="Signed in as ada",
                expect_trace="200",
            ),
            Step(
                click=_btn("Sign out"),
                expect_text="#auth-panel",
                contains="Sign in",
                expect_trace="GET /login-form → 200",
            ),
            Step(
                click=_btn("Open /home anonymously"),
                expect_text="#auth-panel",
                contains="401",
                expect_trace="401",
            ),
        ),
    ),
    DemoContract(
        id="csrf-guard",
        builder=build_csrf_guard_demo,
        min_steps=2,
        steps=(
            Step(
                click=_btn("POST without CSRF"),
                expect_text="#csrf-result",
                contains="403 CSRF failed",
                expect_trace="403",
            ),
            Step(
                click=_btn("POST with CSRF"),
                expect_text="#csrf-result",
                contains="POST ok",
                expect_trace="200",
            ),
        ),
    ),
    DemoContract(
        id="data-table-filter",
        builder=build_data_table_filter_demo,
        min_steps=3,
        steps=(
            Step(
                click=_btn("Admins"),
                expect_text="#people-table",
                contains="Role: admin",
                not_contains="Grace",
                contains_all=("Ada", "Katherine"),
                expect_trace="GET /rows/admin → 200",
            ),
            Step(
                click=_btn("Members"),
                expect_text="#people-table",
                contains="Role: member",
                not_contains="Ada",
                contains_all=("Grace", "Margaret"),
                expect_trace="GET /rows/member → 200",
            ),
            Step(
                click=_btn("All"),
                expect_text="#people-table",
                contains="Grace",
                contains_all=("Ada", "Katherine"),
                expect_trace="GET /rows → 200",
            ),
        ),
    ),
    DemoContract(
        id="pe-paths",
        builder=build_pe_paths_demo,
        min_steps=3,
        steps=(
            Step(
                click=_btn("Submit with HTMX"),
                expect_text="#pe-result",
                contains="Fragment path",
                expect_trace="POST /save-htmx → 200",
            ),
            Step(
                click=_btn("Submit full page (no HTMX path)"),
                expect_text="#pe-stage",
                contains="Full-page confirmation",
                expect_trace="POST /save-page → 200",
            ),
            Step(
                click=_btn("Start over"),
                expect_text="#pe-stage",
                contains="Submit with HTMX",
                expect_trace="GET /reset → 200",
            ),
        ),
    ),
    DemoContract(
        id="jobs-poll",
        builder=build_jobs_poll_demo,
        min_steps=5,
        steps=(
            Step(
                click=_btn("Start job poll"),
                expect_text="#job-panel",
                contains="Queued",
                expect_trace="GET /jobs/42 → 200",
            ),
            Step(
                click=_btn("Start job poll"),
                expect_text="#job-panel",
                contains="Step 1 of 2",
                expect_trace="200",
            ),
            Step(
                click=_btn("Start job poll"),
                expect_text="#job-panel",
                contains="Step 2 of 2",
                expect_trace="200",
            ),
            Step(
                click=_btn("Start job poll"),
                expect_text="#job-panel",
                contains="Complete",
                expect_trace="200",
            ),
            Step(
                click=_btn("Start job poll"),
                expect_text="#job-panel",
                contains="Queued",
                expect_trace="200",
            ),
        ),
    ),
    DemoContract(
        id="file-upload",
        builder=build_file_upload_demo,
        min_steps=4,
        steps=(
            Step(
                click=_btn("Upload malware.exe"),
                expect_text="#upload-stage",
                contains="Rejected type",
                expect_trace="422",
            ),
            Step(
                click=_btn("Back to upload"),
                expect_text="#upload-stage",
                contains="Upload a .txt",
                expect_trace="GET /reset → 200",
            ),
            Step(
                click=_btn("Upload roster.txt"),
                expect_text="#upload-stage",
                contains="Received roster.txt",
                contains_all=("name,role",),
                expect_trace="POST /upload-ok → 200",
            ),
            Step(
                click=_btn("Upload another"),
                expect_text="#upload-stage",
                contains="Upload malware.exe",
                not_contains="Received roster.txt",
                expect_trace="GET /reset → 200",
            ),
        ),
    ),
    DemoContract(
        id="tenant-deny",
        builder=build_tenant_deny_demo,
        min_steps=2,
        steps=(
            Step(
                click=_btn("Poll (same tenant)"),
                expect_text="#job-status",
                contains="tenant A",
                expect_trace="200",
            ),
            Step(
                click=_btn("Poll (other tenant)"),
                expect_text="#job-status",
                contains="404",
                not_contains="tenant A",
                expect_trace="404",
            ),
        ),
    ),
    DemoContract(
        id="core-concepts-modes",
        builder=build_core_concepts_modes_demo,
        mode_demo=True,
        min_steps=2,
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
                wait_ms=2500,
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
                wait_ms=8000,
                expect_text="#poll-box",
                contains="Complete",
                expect_trace="200",
            ),
        ),
    ),
    DemoContract(
        id="component-infinite",
        builder=COMPONENT_DEMO_BUILDERS["component-infinite"],
        min_steps=2,
        steps=(
            Step(
                click=':text("Load more")',
                expect_text="#event-feed",
                contains="Tests passed",
                expect_trace="GET /events → 200",
            ),
            Step(
                click=':text("Load more")',
                expect_text="#event-feed",
                contains_all=("Tests passed",),
                expect_trace="200",
            ),
        ),
    ),
    DemoContract(
        id="component-pagination",
        builder=COMPONENT_DEMO_BUILDERS["component-pagination"],
        min_steps=2,
        steps=(
            Step(
                click='a[aria-label="Page 2"]',
                expect_text="#page-results",
                contains="Results 4–6",
                expect_trace="GET /results?page=2 → 200",
            ),
            Step(
                # Pagination chrome stays on page=1 in this sim — label keeps "(current)".
                click='a[aria-label^="Page 1"]',
                expect_text="#page-results",
                contains="Results 1–3",
                expect_trace="200",
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
                expect_text="#error-box",
                contains="Activity restored",
            ),
        ),
    ),
    DemoContract(
        id="component-form",
        builder=COMPONENT_DEMO_BUILDERS["component-form"],
        min_steps=2,
        steps=(
            Step(
                fill={'input[name="email"]': "nope"},
                click=_btn("Submit"),
                expect_text="#demo-form",
                contains="valid work email",
                expect_trace="422",
            ),
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
        min_steps=2,
        steps=(
            Step(
                fill={'input[name="email"]': "nope"},
                click=_btn("Submit"),
                expect_text="#demo-form",
                contains="valid work email",
                expect_trace="422",
            ),
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
        min_steps=2,
        steps=(
            Step(
                click=_link("Reports"),
                expect_trace="GET /reports → 200",
                expect_text="#comp-main-panel",
                contains="Reports",
            ),
            Step(
                click=_link("Home"),
                expect_trace="GET /home → 200",
                expect_text="#comp-main-panel",
                contains="Overview metrics",
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
                expect_text="#comp-main-panel",
                contains="Reports",
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
                expect_text="#comp-main-panel",
                contains="Overview metrics",
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
                expect_text="#htmx-link-panel",
                contains="Reports",
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
                expect_text="[data-hedron-sim]",
                contains_all=("Profile saved", "Out-of-band update"),
            ),
        ),
    ),
    DemoContract(
        id="component-attr-host",
        builder=COMPONENT_DEMO_BUILDERS["component-attr-host"],
        min_steps=2,
        steps=(
            Step(
                click=_btn("Run attribute OOB"),
                expect_trace="GET /status-attrs → 200",
                expect_text="#demo-attr-host",
                contains="data-state=busy",
            ),
            Step(
                click=_btn("Run attribute OOB"),
                expect_trace="200",
                expect_text="#demo-attr-host",
                contains="data-state=ready",
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
                expect_text="#loading-target",
                contains="3 events",
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
                expect_text="#errors-slot",
                contains="Email is required",
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
                expect_text="#fragment-demo-target",
                contains="Profile updated",
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
                expect_text="[data-hedron-sim]",
                contains="Ada Lovelace",
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
                expect_text="#toast-host",
                contains="copied",
            ),
        ),
    ),
    DemoContract(
        id="component-confirm",
        builder=COMPONENT_DEMO_BUILDERS["component-confirm"],
        min_steps=2,
        steps=(
            Step(
                click=_btn("Delete item"),
                confirm=False,
                expect_text="#confirm-row",
                contains="Draft report",
                expect_trace="cancelled",
            ),
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
