"""Public testing helpers for Hedron applications."""

from __future__ import annotations

from hedron.testing.adapters import (
    AdapterAppFixture as AdapterAppFixture,
)
from hedron.testing.adapters import (
    AdapterResponse as AdapterResponse,
)
from hedron.testing.adapters import (
    assert_dialog_markup as assert_dialog_markup,
)
from hedron.testing.adapters import (
    assert_fragment_body as assert_fragment_body,
)
from hedron.testing.adapters import (
    assert_html_contains as assert_html_contains,
)
from hedron.testing.adapters import (
    assert_htmx_trigger as assert_htmx_trigger,
)
from hedron.testing.adapters import (
    assert_hx_push_url as assert_hx_push_url,
)
from hedron.testing.adapters import (
    assert_hx_redirect as assert_hx_redirect,
)
from hedron.testing.adapters import (
    assert_hx_reswap as assert_hx_reswap,
)
from hedron.testing.adapters import (
    assert_hx_retarget as assert_hx_retarget,
)
from hedron.testing.adapters import (
    assert_lazy_markup as assert_lazy_markup,
)
from hedron.testing.adapters import (
    assert_oob_present as assert_oob_present,
)
from hedron.testing.adapters import (
    assert_page_document as assert_page_document,
)
from hedron.testing.adapters import (
    assert_pagination_markup as assert_pagination_markup,
)
from hedron.testing.adapters import (
    assert_tabs_markup as assert_tabs_markup,
)
from hedron.testing.adapters import (
    assert_toast_markup as assert_toast_markup,
)
from hedron.testing.adapters import (
    django_fixture as django_fixture,
)
from hedron.testing.adapters import (
    fastapi_fixture as fastapi_fixture,
)
from hedron.testing.adapters import (
    flask_fixture as flask_fixture,
)
from hedron.testing.data import (
    AdversarialCase as AdversarialCase,
)
from hedron.testing.data import (
    assert_accessible_fallback as assert_accessible_fallback,
)
from hedron.testing.data import (
    assert_budget as assert_budget,
)
from hedron.testing.data import (
    assert_stable_row_identity as assert_stable_row_identity,
)
from hedron.testing.data import (
    assert_stable_trace_identity as assert_stable_trace_identity,
)
from hedron.testing.data import (
    chart_event_fixture as chart_event_fixture,
)
from hedron.testing.data import (
    data_changes_fixture as data_changes_fixture,
)
from hedron.testing.data import (
    data_query_fixture as data_query_fixture,
)
from hedron.testing.data import (
    grid_event_fixture as grid_event_fixture,
)
from hedron.testing.data import (
    labeled_adversarial_cases as labeled_adversarial_cases,
)
from hedron.testing.data import (
    transform_plan_fixture as transform_plan_fixture,
)
from hedron.testing.fastapi import (
    as_adapter as as_adapter,
)
from hedron.testing.fastapi import (
    assert_non_200_fragment as assert_non_200_fragment,
)
from hedron.testing.fastapi import (
    assert_render_result as assert_render_result,
)
from hedron.testing.fastapi import (
    assert_renders as assert_renders,
)
from hedron.testing.fastapi import (
    fragment_client as fragment_client,
)
from hedron.testing.fastapi import (
    iter_named_examples as iter_named_examples,
)
from hedron.testing.fastapi import (
    named_example as named_example,
)
from hedron.testing.fastapi import (
    normalize_snapshot_html as normalize_snapshot_html,
)
from hedron.testing.fastapi import (
    override_dependencies as override_dependencies,
)
from hedron.testing.fastapi import (
    render_html as render_html,
)
from hedron_core.testing.app import (
    AppScenario as AppScenario,
)
from hedron_core.testing.app import (
    MarkedElement as MarkedElement,
)
from hedron_core.testing.app import (
    find_all_marks as find_all_marks,
)
from hedron_core.testing.app import (
    find_mark as find_mark,
)
from hedron_core.testing.async_scenario import (
    AsyncScenario as AsyncScenario,
)
from hedron_core.testing.async_scenario import (
    ControllableClock as ControllableClock,
)
from hedron_core.testing.async_scenario import (
    ScriptedDependency as ScriptedDependency,
)
from hedron_core.testing.async_scenario import (
    assert_ordered_events as assert_ordered_events,
)
from hedron_core.testing.async_scenario import (
    scripted_outcome as scripted_outcome,
)
from hedron_core.testing.fixtures import (
    AuthPrincipal as AuthPrincipal,
)
from hedron_core.testing.fixtures import (
    BrowserHintFixture as BrowserHintFixture,
)
from hedron_core.testing.fixtures import (
    NamedConnectionFixture as NamedConnectionFixture,
)
from hedron_core.testing.fixtures import (
    OidcCallbackStub as OidcCallbackStub,
)
from hedron_core.testing.fixtures import (
    StoragePayload as StoragePayload,
)
from hedron_core.testing.fixtures import (
    UploadFixture as UploadFixture,
)
from hedron_core.testing.fixtures import (
    redact_secrets_for_failure as redact_secrets_for_failure,
)
from hedron_core.testing.fixtures import (
    validate_fixture as validate_fixture,
)
from hedron_core.testing.htmx_asserts import (
    assert_shell_dual_path as assert_shell_dual_path,
)
from hedron_core.testing.htmx_asserts import (
    assert_ui_targets_subset_of_regions as assert_ui_targets_subset_of_regions,
)
from hedron_core.testing.htmx_asserts import (
    assert_undeclared_target_rejected as assert_undeclared_target_rejected,
)
from hedron_core.testing.workbench import (
    SandboxBudgetFixture as SandboxBudgetFixture,
)
from hedron_core.testing.workbench import (
    assert_action_authorized as assert_action_authorized,
)
from hedron_core.testing.workbench import (
    assert_http_fallback_present as assert_http_fallback_present,
)
from hedron_core.testing.workbench import (
    assert_transform_plan_bounded as assert_transform_plan_bounded,
)
from hedron_core.testing.workbench import (
    image_region_fixture as image_region_fixture,
)
from hedron_core.testing.workbench import (
    json_document_fixture as json_document_fixture,
)
from hedron_core.testing.workbench import (
    sandbox_budget_fixture as sandbox_budget_fixture,
)
from hedron_core.testing.workbench import (
    tree_document_fixture as tree_document_fixture,
)
from hedron_core.testing.workbench import (
    workbench_action_fixture as workbench_action_fixture,
)

__all__ = [
    "AdapterAppFixture",
    "AdapterResponse",
    "AdversarialCase",
    "AppScenario",
    "AsyncScenario",
    "AuthPrincipal",
    "BrowserHintFixture",
    "ControllableClock",
    "MarkedElement",
    "NamedConnectionFixture",
    "OidcCallbackStub",
    "SandboxBudgetFixture",
    "ScriptedDependency",
    "StoragePayload",
    "UploadFixture",
    "as_adapter",
    "assert_accessible_fallback",
    "assert_action_authorized",
    "assert_budget",
    "assert_fragment_body",
    "assert_html_contains",
    "assert_http_fallback_present",
    "assert_htmx_trigger",
    "assert_hx_push_url",
    "assert_hx_redirect",
    "assert_hx_reswap",
    "assert_hx_retarget",
    "assert_non_200_fragment",
    "assert_oob_present",
    "assert_ordered_events",
    "assert_page_document",
    "assert_render_result",
    "assert_renders",
    "assert_shell_dual_path",
    "assert_stable_row_identity",
    "assert_stable_trace_identity",
    "assert_toast_markup",
    "assert_lazy_markup",
    "assert_pagination_markup",
    "assert_tabs_markup",
    "assert_dialog_markup",
    "assert_transform_plan_bounded",
    "assert_ui_targets_subset_of_regions",
    "assert_undeclared_target_rejected",
    "chart_event_fixture",
    "data_changes_fixture",
    "data_query_fixture",
    "django_fixture",
    "fastapi_fixture",
    "find_all_marks",
    "find_mark",
    "flask_fixture",
    "fragment_client",
    "grid_event_fixture",
    "image_region_fixture",
    "iter_named_examples",
    "json_document_fixture",
    "labeled_adversarial_cases",
    "named_example",
    "normalize_snapshot_html",
    "override_dependencies",
    "redact_secrets_for_failure",
    "render_html",
    "sandbox_budget_fixture",
    "scripted_outcome",
    "transform_plan_fixture",
    "tree_document_fixture",
    "validate_fixture",
    "workbench_action_fixture",
]
