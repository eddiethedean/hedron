# Model demo 0.18

Synthetic reference for phase 0.18: fail-closed `ModelDemo`, `ExampleSet`, presentation
builtins, `InferencePolicy`, governed feedback, `InferenceWorkflow`, and `InteractionRecorder`.

```bash
uv run uvicorn app:app --app-dir examples/model-demo-0.18 --reload
```

Open http://127.0.0.1:8000 — you should see synthetic scores and a published workflow revision.
Optional Gradio interop (`hedron[gradio]`) is not required to run this example.
