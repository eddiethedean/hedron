# HDJ authoring

Optional HTML-first templates (`.hdj`) over Jinja, HTML, and HTMX. Install
`hedron[jinja]` / `hedron-jinja`.

This page is the Guides entry point. The full API contract (setup, sinks, streaming,
security) lives in the [HDJ (Jinja) API](../api/JINJA.md).

## When to use HDJ

- You want ordinary Jinja inheritance/includes with typed Hedron components in the same
  template.
- You are migrating HTML/Jinja apps and want progressive adoption.

Prefer typed Python components (`Page`, `Stack`, …) for new FastAPI apps unless you
already have a Jinja codebase.

## Quick install

```bash
pip install "hedron[jinja]>=0.32.0,<0.33"
```

Then follow [HDJ API — Setup](../api/JINJA.md#setup).

## See also

[What’s ready](whats-ready.md) · [Runnable HDJ example](../examples/runnable.md)
