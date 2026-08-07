# Model demo 0.18 evidence (stub)

**Maintainer exit scenario** for phase 0.18 — synthetic setup for `ModelDemo` /
`InferencePolicy` / `InferenceWorkflow`. The HTTP surface is a **stub** (text dump /
minimal predict), not a full interactive classify form.

Prefer [Model demos guide](https://hedron.readthedocs.io/en/latest/guides/model-demos/)
and [recipes](https://hedron.readthedocs.io/en/latest/examples/recipes/) when learning.

```bash
uv run uvicorn app:app --app-dir examples/model-demo-0.18 --reload
```

Open http://127.0.0.1:8000 — expect synthetic scores / workflow text, not a Gradio-like UI.
Optional Gradio interop (`hedron[gradio]`) is not required.

See [Phase evidence](https://hedron.readthedocs.io/en/latest/examples/phase-evidence/).
