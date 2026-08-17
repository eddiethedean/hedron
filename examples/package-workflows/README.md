# Package workflows (0.46)

Reference FastAPI app combining `DataWorkspace`, `ChartInteraction`, and
`ActionHandle.form(enhance="elements")`.

```bash
uv sync
uv run uvicorn app:app --app-dir examples/package-workflows --reload
```

Open http://127.0.0.1:8000. The orders table comes from
`app.include_feature(orders)`; chart selection posts to `filter_orders`.
