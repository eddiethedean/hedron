# Analysis workbench example (0.16)

Minimal FastAPI app composing `hedron-extras` workbench surfaces while the same domain
action remains available through ordinary HTTP form posts.

```bash
uv sync
uv run uvicorn examples.data_app_0_16.app:app --reload
```

Open http://127.0.0.1:8000/
