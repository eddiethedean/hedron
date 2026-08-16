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
pip install "hedron[jinja]>=0.44.0,<0.45"
```

Then follow [HDJ API — Setup](../api/JINJA.md#setup).

## Element declarations (0.40)

HDJ prologues may declare custom-element metadata that must stay aligned with the
registry:

```toml
elements = ["ext-probe"]
element_abi = { "ext-probe" = 1 }
element_modules = { "ext-probe" = "my-plugin:probe.mjs" }
element_events = { "ext-probe" = ["hedron:ready"] }
```

Undeclared hyphenated tags and ABI/module mismatches fail closed when validated against
a registry. Theme compatibility can require declared `parts` / `slots` / `tokens` on
element definitions.

## See also

[What’s ready](whats-ready.md) · [Runnable HDJ example](../examples/runnable.md) ·
[What’s new in 0.40](whats-new-0.41.md) · [HDJ API](../api/JINJA.md)
