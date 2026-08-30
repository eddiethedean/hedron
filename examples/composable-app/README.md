# Composable app

A runnable Hedron app split into importable component modules. It uses only
Hedron's built-in styling—there is no application CSS.

```text
composable-app/
├── app.py
├── custom_css.py
├── pyproject.toml
├── styles.css
└── components/
    ├── __init__.py
    ├── activity.py
    ├── deployments.py
    ├── metrics.py
    └── status.py
```

Run it from the repository root:

```bash
uv run uvicorn --app-dir examples/composable-app app:app --reload
```

`app.py` owns routes and application data. Each component module accepts explicit
inputs and returns a Hedron component tree. `components/__init__.py` is the small,
intentional import surface used by the app.

The default app uses only Hedron's built-in styling. An alternate version registers
ordinary, scoped application CSS:

```bash
cd examples/composable-app
uv sync
uv run python -m hedron.cli --app custom_css:app build --dev
uv run uvicorn custom_css:app --reload
```
