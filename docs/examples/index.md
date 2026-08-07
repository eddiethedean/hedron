# Examples

Ways to try Hedron — prefer a **real server** before simulated docs demos.

There is **no hosted playground**. Use Codespaces / Dev Container, a local clone, or
`hedron new` from [Build your first app](../getting-started/quickstart.md).

1. **[Build your first app](../getting-started/quickstart.md)** — **canonical fastest path:**
   `hedron new` → Hello → **Refresh status** (no monorepo clone required).
2. **[Try with Codespaces / Dev Container](try-it.md)** — remote path with no local Python
   (needs GitHub Codespaces or VS Code / Cursor Dev Container).
3. **[Recipes](recipes/index.md)** — notes + SQLAlchemy, session auth, file upload, jobs poll.
4. **[Runnable examples](runnable.md)** — clone the repo for the reference app, live
   interaction sample, Flask/Django adapters, and HDJ sample.
5. **[CRUD tutorial](crud-tutorial.md)** — guided path through the reference app.
6. **[Single-file apps](single-file.md)** — alternate paste-an-`app.py` path (static Hello;
   no Refresh panel — use the scaffold when you want the interactive proof).
7. **[Phase evidence](phase-evidence.md)** — maintainer exit scenarios (0.15–0.18), not
   product recipes.
8. **[Simulated UI patterns](gallery.md)** — in-browser **simulations** on Read the Docs
   (not a live Hedron process). Prefer [runnable examples](runnable.md) for real HTMX/CSRF.

After Hello + Refresh, prefer [recipes](recipes/index.md) before the kitchen-sink
[reference app walkthrough](reference-app.md). Replace demo credentials and secrets
before any deploy.
