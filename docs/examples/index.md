# Examples

Ways to try Hedron — prefer a **real server** before simulated docs demos.

There is **no hosted playground**. Use Codespaces / Dev Container, a local clone, or
`pip install` + a single-file `app.py`.

1. **[Single-file apps](single-file.md)** — fastest local path: `pip install "hedron>=0.18.0"`
   and paste an `app.py` (no monorepo clone).
2. **[Try with Codespaces / Dev Container](try-it.md)** — remote path with no local Python
   (needs GitHub Codespaces or VS Code / Cursor Dev Container).
3. **[Recipes](notes-sqlalchemy.md)** — notes + SQLAlchemy, [session auth](session-auth.md),
   [file upload](file-upload.md).
4. **[Runnable examples](runnable.md)** — clone the repo for the reference app, live
   interaction sample, Flask/Django adapters, and HDJ sample.
5. **[CRUD tutorial](crud-tutorial.md)** — guided path through the reference app.
6. **[Phase evidence](phase-evidence.md)** — version-stamped exit scenarios (0.15–0.18).
7. **[Simulated UI patterns](gallery.md)** — in-browser **simulations** on Read the Docs
   (not a live Hedron process). Prefer [runnable examples](runnable.md) for real HTMX/CSRF.

Start with the [reference app walkthrough](reference-app.md) when you want CRUD,
CSRF, and HTMX in one place. Replace demo credentials and secrets before any deploy.
