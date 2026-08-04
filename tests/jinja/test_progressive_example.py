"""Evidence that progressive HDJ examples remain runnable."""

from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "examples" / "hdj-progressive" / "app.py"


def test_progressive_hdj_example_renders() -> None:
    namespace = runpy.run_path(str(APP))
    templates = namespace["bind"]()
    minimal = templates.render("01_minimal.hdj", {})
    assert "Hello from a minimal HDJ template" in minimal.html

    greeting = templates.render(
        namespace["TemplateSpec"]("02_jinja.hdj", view_type=namespace["GreetingView"]),
        namespace["GreetingView"](name="Ada"),
    )
    assert "Hello, Ada" in greeting.html

    dashboard = templates.render(
        namespace["TemplateSpec"]("03_components.hdj", view_type=namespace["DashboardView"]),
        namespace["DashboardView"](
            heading="Ops",
            status="Ready",
            detail_url=namespace["SafeUrl"].parse(
                "/ops", purpose=namespace["UrlPurpose"].NAVIGATION
            ),
        ),
    )
    assert "Ops" in dashboard.html
    assert 'href="/ops"' in dashboard.html
