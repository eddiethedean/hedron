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
5. **[Notes list tutorial](crud-tutorial.md)** — in-memory create/list/delete (+ optional update);
   for full admin CRUD see the [reference app](reference-app.md).
6. **[Single-file apps](single-file.md)** — alternate paste-an-`app.py` path with Hello +
   Refresh. Prefer `hedron new` when you want the scaffold and learning-path deltas.
7. **[Phase evidence](phase-evidence.md)** — maintainer exit stubs (not product recipes);
   listed under **Maintainer evidence** in the nav.
8. **[Simulated UI patterns](gallery.md)** — in-browser **simulations** on Read the Docs
   (not a live Hedron process). Prefer [runnable examples](runnable.md) for real HTMX/CSRF.

After Hello + Refresh, prefer [recipes](recipes/index.md) before the kitchen-sink
[reference app walkthrough](reference-app.md). Replace demo credentials and secrets
before any deploy.
