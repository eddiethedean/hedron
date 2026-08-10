# Interactive model demo

Runnable synthetic classifier using `ModelDemo`, `InferencePolicy`,
`InferenceWorkflow`, feedback policy, interaction recording, a CSRF-protected form,
and rendered prediction scores. It is deterministic and performs no network calls, so
you can inspect the entire model/UI boundary locally.

Prefer [Model demos guide](https://hedron.readthedocs.io/en/latest/guides/model-demos/)
and [recipes](https://hedron.readthedocs.io/en/latest/examples/recipes/) when learning.

```bash
uv run uvicorn app:app --app-dir examples/model-demo-0.18 --reload
```

Open http://127.0.0.1:8000, enter text, and choose **Classify**. Cat-related words score
as cat; all other inputs score as dog. The intentionally simple classifier keeps the
example focused on the application workflow rather than a model download.
Optional Gradio interop (`hedron[gradio]`) is not required.

See the [model demos guide](https://hedron.readthedocs.io/en/latest/guides/model-demos/).
