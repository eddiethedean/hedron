# Learn Hedron

**Ordered curriculum (source of truth):** [Learning path](learning-path.md).

**Start now:** [Build your first app](quickstart.md) — scaffold → Hello → Refresh → edit
(~5–10 minutes after Python + uv/pip are ready).

| Step | Page |
|---|---|
| 1. First app | [Build your first app](quickstart.md) |
| 2. HTMX mental model | [What is HTMX?](what-is-htmx.md) |
| 3. Second region | [HTMX interactions](../guides/htmx-interactions.md) |
| 4. Form + CSRF | [Minimal form](../guides/minimal-form.md) |
| 5. Continue | [Learning path](learning-path.md) |

Installation extras and adapters (as needed): [Installation](installation.md).
Help: [FAQ](../guides/faq.md) · [Troubleshooting](../guides/troubleshooting.md).

Evaluating production use? [What’s ready](../guides/whats-ready.md) ·
[Why Hedron](../guides/why-hedron.md) · [Evaluate Hedron](../guides/evaluate.md) ·
[Maturity labels](how-to-read.md).

## Other hosts

- [Flask](flask.md) — `hedron new --flask` then `hedron-flask` (no FastAPI)
- [Django](django.md) — `hedron new --django` then `hedron-django` (Django `>=5.2,<6`)
- [Plain FastAPI](../guides/plain-fastapi.md) — mount Hedron beside an existing FastAPI app

FastAPI remains the default `hedron new` path. Full cloud env (slow first boot):
[Try with Codespaces](../examples/try-it.md).
