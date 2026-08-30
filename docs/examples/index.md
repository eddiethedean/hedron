# Examples

<!-- hedron-release-status -->

These examples target the stable **1.0** API. Version and support details:
[Current release](../guides/current-release.md).

Choose an example by outcome. Prefer a **real server** before simulated documentation demos.

| Outcome | Layer | Difficulty | Time | Start |
|---|---|---:|---:|---|
| Complete page-oriented application | Edron | Beginner | 5 min | [Edron quick start](../getting-started/edron-quickstart.md) |
| FastAPI-native component application | Hedron | Beginner | 10 min | [Hedron quick start](../getting-started/quickstart.md) |
| Persistent notes application | Hedron | Intermediate | 30 min | [Notes with SQLAlchemy](notes-sqlalchemy.md) |
| Session-protected application | Hedron | Intermediate | 25 min | [Session authentication](session-auth.md) |
| Production architecture survey | Hedron | Advanced | 60+ min | [Reference app](reference-app.md) |

See the [Edron example catalog](edron.md) for dashboard, CRUD, task, and migration scaffolds.

There is **no hosted playground**. Use Codespaces / Dev Container, a local clone, or
`hedron new` from [Build your first app](../getting-started/quickstart.md).

1. **[Build your first app](../getting-started/quickstart.md)** — **canonical fastest path:**
   `hedron new` → Hello → **Refresh status** (no monorepo clone required).
2. **[Build a notes app](build-notes-app.md)** — progressive path from Hello through a form,
   persistence, authentication, and deployment checks.
3. **[Try with Codespaces / Dev Container](try-it.md)** — remote path with no local Python
   (needs GitHub Codespaces or VS Code / Cursor Dev Container).
4. **[Recipes](recipes/index.md)** — notes + SQLAlchemy, session auth, file upload, jobs poll.
5. **[Runnable examples](runnable.md)** — clone the repo for the reference app, live
   interaction sample, Flask/Django adapters, and HDJ sample.
6. **[Notes list tutorial](crud-tutorial.md)** — in-memory create/list/delete (+ optional update);
   for full admin CRUD see the [reference app](reference-app.md).
7. **[Single-file apps](single-file.md)** — alternate paste-an-`app.py` path with Hello +
   Refresh. Prefer `hedron new` when you want the scaffold and learning-path deltas.
8. **[Simulated UI patterns](gallery.md)** — in-browser **simulations** on Read the Docs
   (not a live Hedron process). Prefer [runnable examples](runnable.md) for real HTMX/CSRF.

After Hello + Refresh, prefer [recipes](recipes/index.md) before the kitchen-sink
[reference app walkthrough](reference-app.md). Replace demo credentials and secrets
before any deploy.
