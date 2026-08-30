# Edron Showcase

A complete Edron operations workspace built with Edron's public class-oriented API.

The source intentionally imports only `edron`. It demonstrates pages, sidebar composition,
layouts, metrics, cards, fragments, actions, tables, charts, tabs, status outcomes, and a named
Edron theme without using Hedron escape hatches.

Run it from the repository root:

```bash
uv sync
uv run edron run app:app --app-dir examples/edron-showcase --reload
```

Open <http://127.0.0.1:8000/>. The data is synthetic and local; the routes, rendering lifecycle,
CSRF boundary, and Edron-to-runtime lowering are real.

Edron's generated theme includes coordinated light/dark palettes that follow the browser
preference, and its shell and column layouts collapse cleanly on narrow screens.

The documentation preview is generated from this same application with `edron-sim`; it does not
maintain a second hand-authored simulator. The preview clock is intentionally fixed so generated
docs remain reproducible.
