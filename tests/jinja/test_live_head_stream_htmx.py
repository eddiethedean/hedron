"""HDJ phase 0.10 head / stream / HTMX evidence."""

from __future__ import annotations

from jinja2 import DictLoader, Environment

from hedron_core import Model
from hedron_jinja import HedronJinja, TemplateKind, TemplateSpec
from hedron_jinja.source import _htmx_local_diagnostics, parse_hdj_source


def _hdj(
    body: str,
    *,
    kind: str = "fragment",
    profile: str = "standard",
    declarations: str = "",
) -> str:
    extra = f"{declarations.rstrip()}\n" if declarations else ""
    return f'---hdj\nversion = 1\nkind = "{kind}"\nprofile = "{profile}"\n{extra}---\n{body}'


class MsgView(Model):
    msg: str


def test_two_phase_stream_metadata_first() -> None:
    env = Environment(loader=DictLoader({"card.hdj": _hdj("<p>{{ view.msg }}</p>")}))
    hdj = HedronJinja(env)
    stream = hdj.two_phase_stream(
        TemplateSpec("card.hdj", view_type=MsgView),
        MsgView(msg="hi"),
        body_chunk_size=4,
    )
    phases = list(stream.iter_phases())
    assert phases[0][0] == "metadata"
    assert phases[0][1].html
    assert any(p[0] == "body" for p in phases)


def test_fragment_head_mutation_capability() -> None:
    source = _hdj(
        '<div class="frag">{{ view.title }}</div>',
        declarations='requires = ["browser.head-mutation"]\nassets = ["app.css"]\n',
    )
    parsed = parse_hdj_source("frag.hdj", source)
    assert parsed.declaration.kind is TemplateKind.FRAGMENT
    assert "browser.head-mutation" in parsed.declaration.requires
    assert "app.css" in parsed.declaration.assets


def test_unknown_htmx_attribute_warned() -> None:
    body = '<div hx-get="/x" hx-future-thing="1"></div>'
    source = _hdj(body)
    parsed = parse_hdj_source("x.hdj", source)
    diags = _htmx_local_diagnostics(parsed, body, body)
    codes = {d.code for d in diags}
    assert "HED-JINJA-0027" in codes
