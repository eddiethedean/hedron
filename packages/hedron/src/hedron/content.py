"""Content extras: Markdown, code highlighting, images, email validation."""

from __future__ import annotations

from typing import Any

from hedron_core.auto import RendererSpec, register_renderer
from hedron_core.component import Component
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import TrustedHtml

__all__ = [
    "Markdown",
    "highlight_code",
    "process_image",
    "register_content_renderers",
    "validate_email_address",
]


class MarkdownProps(Props):
    source: str = ""


class Markdown(Component[MarkdownProps]):
    """Secure Markdown → sanitized TrustedHtml."""

    logical_name = "Markdown"
    distribution = "hedron"

    def __init__(self, source: str, **kwargs: Any) -> None:
        super().__init__(MarkdownProps(source=source, **kwargs))

    def render(self) -> Any:
        try:
            import markdown as md
        except ImportError as exc:
            raise error(
                "HED-CONTENT-0001",
                title="markdown extra not installed",
                explanation="Markdown requires the markdown package.",
                remediation='Install with: pip install "hedron[markdown]"',
            ) from exc
        rendered = md.markdown(self.props.source, extensions=["fenced_code", "tables"])
        trusted = TrustedHtml.nh3(rendered)
        return html.div(
            html.raw(trusted),
            class_="hedron-markdown",
        )


def highlight_code(code: str, *, lexer: str = "python") -> TrustedHtml:
    try:
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import get_lexer_by_name, guess_lexer
    except ImportError as exc:
        raise error(
            "HED-CONTENT-0002",
            title="code extra not installed",
            explanation="Syntax highlighting requires Pygments.",
            remediation='Install with: pip install "hedron[code]"',
        ) from exc
    try:
        lex = get_lexer_by_name(lexer)
    except Exception:
        lex = guess_lexer(code)
    formatter = HtmlFormatter(nowrap=False)
    html_out = highlight(code, lex, formatter)
    if not _nh3_available():
        import html as html_stdlib

        escaped = html_stdlib.escape(code)
        return TrustedHtml.reviewed(
            f'<pre class="hedron-code"><code>{escaped}</code></pre>',
            source="pygments-fallback",
        )
    return TrustedHtml.nh3(html_out)


def _nh3_available() -> bool:
    from importlib.util import find_spec

    return find_spec("nh3") is not None


def process_image(
    path_or_bytes: str | bytes,
    *,
    max_width: int = 1600,
    format: str = "PNG",
) -> bytes:
    try:
        from io import BytesIO

        from PIL import Image
    except ImportError as exc:
        raise error(
            "HED-CONTENT-0003",
            title="images extra not installed",
            explanation="Image processing requires Pillow.",
            remediation='Install with: pip install "hedron[images]"',
        ) from exc
    if isinstance(path_or_bytes, bytes):
        img = Image.open(BytesIO(path_or_bytes))
    else:
        img = Image.open(path_or_bytes)
    img = img.convert("RGBA") if format.upper() == "PNG" else img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / float(img.width)
        img = img.resize((max_width, int(img.height * ratio)))
    out = BytesIO()
    img.save(out, format=format)
    return out.getvalue()


def validate_email_address(value: str) -> str:
    try:
        from email_validator import EmailNotValidError, validate_email
    except ImportError as exc:
        raise error(
            "HED-CONTENT-0004",
            title="email extra not installed",
            explanation="Email validation requires email-validator.",
            remediation='Install with: pip install "hedron[email]"',
        ) from exc
    try:
        result = validate_email(value, check_deliverability=False)
    except EmailNotValidError as exc:
        raise error(
            "HED-CONTENT-0005",
            title="Invalid email address",
            explanation=str(exc),
            remediation="Provide a valid email address.",
        ) from exc
    return str(result.normalized)


def register_content_renderers() -> None:
    register_renderer(
        RendererSpec(
            name="markdown",
            priority=850,
            predicate=lambda v: isinstance(v, str) and v.lstrip().startswith("#"),
            optional_package="hedron[markdown]",
            explanation="Markdown-looking strings → Markdown component",
            factory=lambda v: Markdown(v if isinstance(v, str) else str(v)),
        )
    )
