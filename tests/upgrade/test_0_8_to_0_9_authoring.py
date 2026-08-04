"""Manual 0.8 → 0.9 authoring upgrade fixture (no HDN converter)."""

from __future__ import annotations

from jinja2 import DictLoader, Environment

from hedron_core import Badge, Model, SafeUrl, UrlPurpose
from hedron_jinja import HedronJinja, TemplateSpec


class StatusView(Model):
    label: str
    href: SafeUrl


def test_hdn_concepts_rewrite_to_hdj_without_converter() -> None:
    """Prove the documented rewrite table against a runnable HDJ template.

    HDN 0.8 (removed) conceptual source::

        <section>
          <Badge text={label} />
          <a href={href}>Open</a>
        </section>

    HDJ 0.9 body uses ``view`` + filters + ``{% hedron %}``.
    """
    source = (
        "---hdj\n"
        "version = 1\n"
        'kind = "fragment"\n'
        'profile = "standard"\n'
        "---\n"
        "<section>\n"
        '  {% hedron "Badge" text=view.label %}\n'
        '  <a href="{{ view.href|hedron_nav_url }}">Open</a>\n'
        "</section>\n"
    )
    templates = HedronJinja(
        Environment(loader=DictLoader({"status.hdj": source})),
        components={"Badge": Badge},
    )
    result = templates.render(
        TemplateSpec("status.hdj", view_type=StatusView),
        StatusView(
            label="Ready",
            href=SafeUrl.parse("/status", purpose=UrlPurpose.NAVIGATION),
        ),
    )
    assert "hedron-badge" in result.html
    assert 'href="/status"' in result.html
    assert "Ready" in result.html
