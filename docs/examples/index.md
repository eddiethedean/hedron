# Examples

Ways to try Hedron — prefer a **real server** before simulated docs demos.

There is **no hosted playground**. Use Codespaces / Dev Container, a local clone, or
`pip install` + a single-file `app.py`.

1. **[Single-file apps](single-file.md)** — fastest local path: `pip install "hedron>=0.13.0"`
   and paste an `app.py` (no monorepo clone).
2. **[Try with Codespaces / Dev Container](try-it.md)** — no local Python setup
   (not a single command; needs GitHub or VS Code / Cursor).
3. **[Runnable examples](runnable.md)** — clone the repo for the reference app,
   live interaction sample, Flask/Django adapters, and HDJ sample.
4. **[CRUD tutorial](crud-tutorial.md)** — guided path through the reference app.
5. **[Simulated UI patterns](gallery.md)** — in-browser **simulations** on Read the Docs
   (not a live Hedron process). Prefer [runnable examples](runnable.md) for real HTMX/CSRF.

!!! note "Live interaction sample"

    [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction)
    covers poll, token stream, SSE ping, Job SSE, page/session WebSocket accept, and
    navigation preload (FastAPI). Prefer polling behind load balancers until you have your
    own ops proof for SSE/WebSocket — see [What's ready](../guides/whats-ready.md).

Start with the [reference app walkthrough](reference-app.md) when you want CRUD,
CSRF, and HTMX in one place. Replace demo credentials and secrets before any deploy.
