# Analysis workbench example (0.16)

Minimal Hedron app composing `hedron-extras` workbench surfaces while the same domain
action remains available through ordinary HTTP form posts.

```bash
uv sync
uv run uvicorn app:app --app-dir examples/data-app-0.16 --reload
```

Open http://127.0.0.1:8000/
