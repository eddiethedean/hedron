# CRUD tutorial (reference app)

End-to-end CRUD, CSRF, and auth live in the FastAPI **reference application**—the
supported multi-day learning track after the quickstart.

## What you will learn

1. Project layout and `Hedron(...)` security defaults
2. Pages, fragments, and HTMX updates
3. Forms with CSRF and validation
4. Session login / gated routes
5. Optional data and chart extras

## Run the walkthrough

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
uv run uvicorn app:app --app-dir examples/reference-app --reload
```

Open <http://127.0.0.1:8000/>. Default demo credentials: `admin` / `secret`
(development only).

Follow the annotated tour:

- [Reference app walkthrough](reference-app.md)
- Source: [`examples/reference-app`](https://github.com/eddiethedean/hedron/tree/main/examples/reference-app)

## Suggested reading order

1. [Quickstart](../getting-started/quickstart.md)
2. [HTMX interactions](../guides/htmx-interactions.md) → [Minimal form](../guides/minimal-form.md)
3. This reference app (CRUD + auth)
4. [Live interaction sample](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction)
5. [Deployment](../guides/deployment.md)
