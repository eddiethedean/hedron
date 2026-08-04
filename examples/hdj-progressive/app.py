"""Progressive HDJ authoring examples for phase 0.9.

Templates live under ``templates/`` and demonstrate:

1. minimal three-field prologue + plain HTML
2. Jinja composition with a typed view
3. Hedron components, slots, and SafeUrl filters
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from hedron_core import Badge, Card, Model, SafeUrl, UrlPurpose
from hedron_jinja import HedronJinja, TemplateSpec

ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"


class GreetingView(Model):
    name: str


class DashboardView(Model):
    heading: str
    status: str
    detail_url: SafeUrl


def bind() -> HedronJinja:
    environment = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(("hdj",)),
    )
    return HedronJinja(
        environment,
        components={"Badge": Badge, "Card": Card},
        allowed_capabilities=(),
    )


def main() -> None:
    templates = bind()
    minimal = templates.render("01_minimal.hdj", {})
    greeting = templates.render(
        TemplateSpec("02_jinja.hdj", view_type=GreetingView),
        GreetingView(name="Ada"),
    )
    dashboard = templates.render(
        TemplateSpec("03_components.hdj", view_type=DashboardView),
        DashboardView(
            heading="Ops",
            status="Ready",
            detail_url=SafeUrl.parse("/ops", purpose=UrlPurpose.NAVIGATION),
        ),
    )
    print(minimal.html)
    print(greeting.html)
    print(dashboard.html)


if __name__ == "__main__":
    main()
