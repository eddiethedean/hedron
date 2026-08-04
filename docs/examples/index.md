# Examples

Ways to try Hedron — prefer a **real server** before simulated docs demos.

There is **no hosted try-it without cloning** (or Codespaces / Dev Container). Use
[Try in one command](try-it.md) or a local clone.

1. **[Try in one command](try-it.md)** — Dev Container / Codespaces.
2. **[Runnable examples](runnable.md)** — clone the repo for the reference app,
   live interaction sample, Flask/Django adapters, and HDJ sample.
3. **[Single-file apps](single-file.md)** — `pip install "hedron>=0.10.1"` and paste an
   `app.py` (no monorepo clone).
4. **[CRUD tutorial](crud-tutorial.md)** — guided path through the reference app.
5. **[Simulated UI patterns](gallery.md)** — in-browser **simulations** on Read the Docs
   (not a live Hedron process). Prefer [runnable examples](runnable.md) for real HTMX/CSRF.

!!! note "Live interaction sample coverage"

    [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction)
    demonstrates **poll + token stream + minimal SSE**. Job SSE, WebSocket channels, and
    navigation preload are documented in the [live interaction guide](../guides/live-interaction.md)
    (API Supported on FastAPI) but are not in that sample yet.

Start with the [reference app walkthrough](reference-app.md) when you want CRUD,
CSRF, and HTMX in one place. Replace demo credentials and secrets before any deploy.
