"""Phase 0.15 M3 typed controls and surface chrome."""

from __future__ import annotations

import pytest

from hedron_core import render
from hedron_core.builtins import (
    ActionDock,
    BottomDock,
    Carousel,
    ChipInput,
    CircularProgress,
    ClipboardCopy,
    ColorInput,
    ConfirmButton,
    ContextMenu,
    DateInput,
    DateTimeInput,
    DirectoryUpload,
    Help,
    MenuButton,
    MultiSelect,
    NumberInput,
    Pills,
    Popover,
    RangeInput,
    RatingInput,
    SegmentedControl,
    SelectSlider,
    Spacer,
    Text,
    TimeInput,
    Timeline,
    ToggleSwitch,
    Tooltip,
)
from hedron_core.builtins.forms_extra import DirectoryUploadFile, validate_directory_upload
from hedron_core.security import SafeUrl, UrlPurpose


def test_number_and_range_inputs() -> None:
    number = render(NumberInput("qty", value=3, min=0, max=10, step=1)).html
    assert 'type="number"' in number
    assert 'name="qty"' in number
    assert 'value="3"' in number

    range_html = render(RangeInput("vol", value=40, min=0, max=100, markers=[0, 50, 100])).html
    assert 'type="range"' in range_html
    assert 'name="vol"' in range_html
    assert "<datalist" in range_html


def test_date_time_datetime_inputs() -> None:
    assert 'type="date"' in render(DateInput("d", value="2026-08-05")).html
    assert 'type="time"' in render(TimeInput("t", value="12:30")).html
    assert 'type="datetime-local"' in render(DateTimeInput("dt", value="2026-08-05T12:30")).html


def test_multiselect_toggle_segmented_pills() -> None:
    multi = render(MultiSelect("langs", [("py", "Python"), ("rs", "Rust")], values=["py"])).html
    assert "<select" in multi
    assert "multiple" in multi
    assert 'name="langs"' in multi
    assert "selected" in multi

    toggle = render(ToggleSwitch("on", "Enabled", checked=True)).html
    assert 'role="switch"' in toggle
    assert "hedron-switch" in toggle
    assert 'type="checkbox"' in toggle

    segmented = render(
        SegmentedControl("view", "View", [("list", "List"), ("grid", "Grid")], value="list")
    ).html
    assert "<fieldset" in segmented
    assert 'type="radio"' in segmented
    assert "hedron-segmented-control" in segmented

    pills = render(Pills("size", "Size", [("s", "S"), ("m", "M")], value="m")).html
    assert "hedron-pills" in pills
    assert 'type="radio"' in pills


def test_color_rating_chip_menu_select_slider() -> None:
    from hedron_core import html as h

    assert 'type="color"' in render(ColorInput("c", value="#ff0000")).html

    rating = render(RatingInput("stars", "Rating", maximum=5, value=3)).html
    assert 'type="radio"' in rating
    assert "1 of 5" in rating
    assert 'name="stars"' in rating

    chips = render(ChipInput("tags", values=["alpha", "beta"])).html
    assert 'name="tags"' in chips
    assert 'value="alpha"' in chips
    assert 'value="beta"' in chips
    assert "hedron-chip-input" in chips
    assert "<ul" in chips

    menu = render(
        MenuButton(
            "Open",
            h.a("Edit", href=SafeUrl.parse("/edit", purpose=UrlPurpose.NAVIGATION)),
        )
    ).html
    assert "popovertarget" in menu
    assert "<menu" in menu
    assert "Edit" in menu

    slider = render(SelectSlider("level", [("low", "Low"), ("high", "High")], value="high")).html
    assert 'type="range"' in slider
    assert "<datalist" in slider
    assert 'name="level"' in slider


def test_carousel_timeline_nojs_markup() -> None:
    carousel = render(
        Carousel(
            [("intro", Text("One")), ("detail", Text("Two"))],
            id="demo-carousel",
        )
    ).html
    assert 'id="demo-carousel-intro"' in carousel
    assert 'id="demo-carousel-detail"' in carousel
    assert "<ul" in carousel
    assert 'href="#demo-carousel-detail"' in carousel
    assert "hedron-carousel-prev" in carousel
    assert "hedron-carousel-next" in carousel

    timeline = render(
        Timeline(
            [
                ("2026-01", "Kickoff", Text("Started")),
                ("2026-08", "Ship", Text("Done")),
            ]
        )
    ).html
    assert timeline.strip().startswith("<ol") or "<ol" in timeline
    assert "<time" in timeline
    assert "Kickoff" in timeline
    assert "hedron-timeline" in timeline


def test_context_menu_has_overflow_button_alternative() -> None:
    from hedron_core import html as h

    html = render(
        ContextMenu(
            h.a("Delete", href=SafeUrl.parse("/delete", purpose=UrlPurpose.NAVIGATION)),
            label="Actions",
            overflow_label="More actions",
        )
    ).html
    assert "hedron-context-menu-overflow" in html
    assert "More actions" in html
    assert "popovertarget" in html
    assert html.count("popovertarget=") >= 2
    assert "<menu" in html


def test_circular_progress_has_aria_and_status_text() -> None:
    determinate = render(CircularProgress(50, maximum=100, label="Halfway")).html
    assert 'role="status"' in determinate
    assert "aria-valuenow" in determinate or 'aria-valuenow="50"' in determinate
    assert "Halfway" in determinate
    assert "<progress" in determinate

    indeterminate = render(CircularProgress(indeterminate=True, label="Loading")).html
    assert 'role="status"' in indeterminate
    assert "Loading" in indeterminate
    assert 'aria-busy="true"' in indeterminate


def test_popover_docks_spacer_tooltip_help_confirm_clipboard() -> None:
    pop = render(Popover(Text("Body"), label="Open", mode="popover")).html
    assert "popovertarget" in pop
    assert 'popover="auto"' in pop

    details = render(Popover(Text("Body"), label="Open", mode="details")).html
    assert "<details" in details
    assert "<summary>" in details

    dock = render(ActionDock(Text("Save"), placement="bottom")).html
    assert "hedron-bottom-dock" in dock
    assert dock.startswith("<footer") or "<footer" in dock

    bottom = render(BottomDock(Text("Ok"))).html
    assert "hedron-bottom-dock" in bottom

    aside = render(ActionDock(Text("Side"), placement="aside")).html
    assert "<aside" in aside

    spacer = render(Spacer(size="1rem")).html
    assert "hedron-spacer" in spacer
    assert 'aria-hidden="true"' in spacer

    tip = render(Tooltip("Hint", Text("hover"))).html
    assert 'title="Hint"' in tip

    help_html = render(Help("Use a strong password", id="pw-help", for_="password")).html
    assert 'id="pw-help"' in help_html
    assert 'role="note"' in help_html

    confirm = render(ConfirmButton("Delete", confirm="Really delete?")).html
    assert "hx-confirm" in confirm
    assert 'data-confirm="Really delete?"' in confirm

    copy = render(ClipboardCopy("secret-token", label="Copy token")).html
    assert 'data-copy-text="secret-token"' in copy
    assert "hedron-clipboard-copy" in copy


def test_directory_upload_and_validation() -> None:
    markup = render(DirectoryUpload(name="docs", label="Upload folder")).html
    assert 'type="file"' in markup
    assert "webkitdirectory" in markup
    assert 'name="docs"' in markup
    assert "multiple" in markup

    ok = validate_directory_upload(
        [DirectoryUploadFile("a/b.txt", 10), ("c.txt", 5)],
        max_files=10,
        max_total_size=100,
    )
    assert len(ok) == 2

    with pytest.raises(ValueError, match="traversal|Absolute|Unsafe"):
        validate_directory_upload([("../etc/passwd", 1)], max_files=10, max_total_size=100)

    with pytest.raises(ValueError, match="traversal|Absolute|Unsafe"):
        validate_directory_upload([("/etc/passwd", 1)], max_files=10, max_total_size=100)

    for evil in (
        "%2e%2e/x",
        "..%2fsecret",
        "foo/%2e%2e/bar",
        "foo/..;/bar",
        "%2E%2E%2Fetc%2Fpasswd",
    ):
        with pytest.raises(ValueError, match="traversal|Absolute|Unsafe"):
            validate_directory_upload([(evil, 1)], max_files=10, max_total_size=100)

    with pytest.raises(ValueError, match="max_total_size"):
        validate_directory_upload([("big.bin", 50)], max_files=10, max_total_size=10)

    with pytest.raises(ValueError, match="max_files"):
        validate_directory_upload(
            [("a.txt", 1), ("b.txt", 1), ("c.txt", 1)],
            max_files=2,
            max_total_size=100,
        )
