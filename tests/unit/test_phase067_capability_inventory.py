"""Executable disposition and sink coverage for the Phase 0.67 Alpine surface."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hedron_core import AlpineAttrs, AlpineDirective, AlpineExpression, BrowserFeaturePlan


def test_every_frozen_core_directive_has_a_typed_construction_path() -> None:
    name = AlpineExpression.name("open")
    directives = (
        AlpineDirective("x-data", json.dumps({"open": False})),
        AlpineDirective("x-init", name),
        AlpineDirective("x-show", name),
        AlpineDirective("x-bind:disabled", name),
        AlpineDirective("x-on:click", name),
        AlpineDirective("x-text", name),
        AlpineDirective("x-model", "open"),
        AlpineDirective("x-for", "item in items"),
        AlpineDirective("x-transition"),
        AlpineDirective("x-effect", name),
        AlpineDirective("x-ref", "panel"),
        AlpineDirective("x-if", name),
        AlpineDirective("x-id", json.dumps(["panel"])),
    )
    attrs = AlpineAttrs(directives=directives, source="tests:capabilities")
    assert {directive.name for directive in attrs.directives} == {
        directive.name for directive in directives
    }
    assert {"data", "show", "bind", "on", "model", "for", "text", "effect", "id"}.issubset(
        set(attrs.features)
    )


def test_progressive_and_bounded_directives_are_explicit() -> None:
    attrs = AlpineAttrs(
        directives=(
            AlpineDirective("x-modelable", "value"),
            AlpineDirective("x-teleport", json.dumps("body")),
            AlpineDirective("x-ignore"),
            AlpineDirective("x-cloak"),
        ),
        source="tests:progressive",
    )
    assert {"modelable", "teleport", "ignore", "cloak"}.issubset(set(attrs.features))
    with pytest.raises(ValueError, match="x-html"):
        AlpineDirective("x-html", "content")


def test_unsafe_reactive_sinks_and_shorthand_are_rejected() -> None:
    with pytest.raises(ValueError, match="safe sink"):
        AlpineDirective("x-bind:href", AlpineExpression.name("url"))
    with pytest.raises(ValueError, match="safe sink"):
        AlpineDirective("x-bind:class", AlpineExpression.name("classes"))
    with pytest.raises(ValueError):
        AlpineDirective("@click", AlpineExpression.name("open"))
    with pytest.raises(ValueError):
        AlpineDirective("x-on:click.debounce.5000ms", AlpineExpression.name("open"))


def test_composition_rejects_duplicate_writers_and_plan_derives_assets() -> None:
    first = AlpineAttrs.data({"open": False}, source="tests:first")
    with pytest.raises(ValueError, match="conflicting Alpine state writer"):
        first.merge(AlpineAttrs.data({"open": True}, source="tests:second"))
    plan = BrowserFeaturePlan.from_demands(tuple(first.demands()))
    assert "/hedron-static/alpine/csp-3.16.3.js" in plan.assets
    assert "/hedron-static/hedron-alpine.mjs" in plan.assets


def test_machine_disposition_covers_the_frozen_surface() -> None:
    packet = Path("docs/acceptance/alpine-capability-dispositions-067.toml").read_text(
        encoding="utf-8"
    )
    for token in (
        '"x-data"',
        '"x-html"',
        '"$dispatch"',
        '"Alpine.data"',
        '"anchor"',
        '"morph"',
        'essential_x_cloak = false',
    ):
        assert token in packet
