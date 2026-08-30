"""ENGINE-067: common native components lower to the typed Alpine lane."""

from __future__ import annotations

from hedron import FileUpload
from hedron_core import (
    Checkbox,
    Dialog,
    DirectoryUpload,
    Expander,
    Select,
    TextArea,
    TextInput,
    render,
)
from hedron_core.rendering import RenderMode


def test_common_components_emit_typed_alpine_lowerings_and_native_fallbacks() -> None:
    result = render(
        (
            Expander("Details", "Body"),
            Dialog("Settings", "Dialog body", id="settings"),
            TextInput("name", value="Ada"),
            TextArea("bio", value="Engineer"),
            Select("role", (("admin", "Admin"),), value="admin"),
            Checkbox("enabled", "Enabled", checked=True),
            DirectoryUpload(name="documents"),
            FileUpload(name="avatar"),
        ),
        mode=RenderMode.PAGE,
    )

    assert 'x-data="{&quot;open&quot;:false}"' in result.html
    assert 'x-on:click.prevent="open = (open !== true)"' in result.html
    assert 'x-on:close="open = false"' in result.html
    assert 'x-model="value"' in result.html
    assert 'x-model="selected"' in result.html
    assert 'x-model="checked"' in result.html
    assert 'x-on:change="has_files = true"' in result.html
    assert 'x-bind:hidden="(has_files !== true)"' in result.html

    # Native semantics remain present for JavaScript-disabled or failed-enhancement paths.
    assert "<details" in result.html
    assert "<dialog" in result.html
    assert '<input id="field-name"' in result.html
    assert '<textarea id="field-bio"' in result.html
    assert '<select id="field-role"' in result.html
    assert 'type="checkbox"' in result.html
    assert 'type="file"' in result.html

    assert result.browser_plan.requires("data")
    assert result.browser_plan.requires("model")
    assert result.browser_plan.requires("on")
    assert result.browser_plan.requires("bind")
    assert result.browser_plan.requires("show")
    assert "/hedron-static/alpine/collapse-3.16.3.js" in result.browser_plan.assets
    assert "/hedron-static/alpine/focus-3.16.3.js" in result.browser_plan.assets


def test_file_enhancement_status_starts_hidden() -> None:
    result = render(FileUpload(name="documents"))

    assert 'class="hedron-file-upload-selected" hidden' in result.html
    assert 'x-bind:hidden="(has_files !== true)"' in result.html


def test_dependent_select_keeps_alpine_state_and_htmx_request_ownership() -> None:
    result = render(
        Select(
            "city",
            (("nyc", "New York"),),
            depends_on="country",
            source="/cities",
        )
    )

    assert 'x-model="selected"' in result.html
    assert 'hx-get="/cities"' in result.html
    assert 'hx-trigger="change from:#field-country"' in result.html
    assert 'hx-include="#field-country"' in result.html
    assert 'hx-target="this"' in result.html
    assert 'hx-swap="outerHTML"' in result.html
