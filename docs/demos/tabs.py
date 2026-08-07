"""Format Demo / Code tabs for hedron-sim documentation islands."""

from __future__ import annotations

from .runnable_code import runnable_source

__all__ = ["format_demo_code_tabs"]


def _indent(text: str, spaces: int = 4) -> str:
    pad = " " * spaces
    lines = text.splitlines()
    return "\n".join(f"{pad}{line}" if line else "" for line in lines)


def format_demo_code_tabs(
    sim_id: str,
    *,
    demo_blurb: str = "Docs simulation — no live server.",
    code_blurb: str = (
        "Minimal runnable `app.py` that reproduces this demo (real Hedron, not the docs simulator):"
    ),
) -> str:
    """Return Material tabbed markdown with a sim island and full app source."""
    code = runnable_source(sim_id).rstrip() + "\n"
    fence = _indent(f'```python title="app.py"\n{code}```')
    return (
        f'=== "Demo"\n'
        f"\n"
        f"{_indent(demo_blurb)}\n"
        f"\n"
        f"{_indent(f'<!-- hedron-sim:{sim_id} -->')}\n"
        f"\n"
        f'=== "Code"\n'
        f"\n"
        f"{_indent(code_blurb)}\n"
        f"\n"
        f"{fence}\n"
    )
