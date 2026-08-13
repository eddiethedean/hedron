# Theme gallery

Visual QA fixture for Hedron's built-in themes. It composes five common product
interfaces—dashboard, settings, orders, support, and component states—and can
switch between Default and Aurora while forcing either palette independently of
the operating-system preference.

```bash
uv run uvicorn --app-dir examples/theme-gallery app:app --reload
```

Open <http://127.0.0.1:8000/> and use the Default, Aurora, Light, and Dark controls
in the header.
The gallery intentionally uses Hedron built-ins without an application
stylesheet, so visual regressions point back to the shared theme.
