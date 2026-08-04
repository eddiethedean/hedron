# What’s ready today

Operator-facing snapshot of published **0.10.0**. Maintainer evidence tables live in
the repository [`docs/STATUS.md`](https://github.com/eddiethedean/hedron/blob/main/docs/STATUS.md).

## Supported capabilities (Beta packages)

Hedron **0.10.0** packages are **Beta**. Capabilities listed as **Supported** below
are intended for production use with pinned versions. **Deferred** items are
documented and must not be treated as ready. There is no scheduled 1.0; expect
occasional breaking changes on `0.x` under the
[compatibility policy](../COMPATIBILITY.md).

| Capability | Package / surface |
|---|---|
| Typed pages, fragments, built-ins | `hedron` + `hedron-core` |
| FastAPI routing, CSRF profiles, CLI, testing helpers | `hedron` |
| HTMX fragment loops, `InteractionResult` | `hedron` |
| Live interaction: SSE, streaming, WebSocket channels, Chat/Dialog, opt-in preload | `hedron` (FastAPI flagship) |
| Flask / Django adapters (Supported matrix) | `hedron-flask`, `hedron-django` |
| Optional HDJ (`.hdj`) templates | `hedron[jinja]` |
| Auto (inspectable object rendering) | Core (`hedron`) — no extra |
| DataTable / DataEditor | `hedron[data]` |
| Component Explorer (dev) | `hedron[dev]` |

## Supported examples

- Live interaction sample (poll + stream learning path):
  [`examples/live-interaction`](https://github.com/eddiethedean/hedron/tree/main/examples/live-interaction)
  — see also the [live interaction guide](live-interaction.md)
- FastAPI / Flask / Django reference apps — [runnable examples](../examples/runnable.md)

## Treat as Alpha / more volatile

- `hedron-charts` and chart backends
- `hedron-sample-kit` (plugin sample)

## Deferred (do not market as Supported)

- Django QuerySet as a first-party DataSource → planned **0.11**
- Hedron-owned Django forms depth → **0.11**
- First-party camera/microphone capture UI → **0.15**
- Official HTMX SSE on Flask/Django (use polling) → see live guide
- Full multi-engine live browser matrix and some Explorer live traces → owned `0.10.x` Deferred rows in STATUS

## Recommended install

```bash
pip install "hedron>=0.10.0"
hedron new my-app
cd my-app
pip install -e .   # or: uv sync
uvicorn app:app --reload
```

Extras: `"hedron[data]"`, `"hedron[charts]"`, `"hedron[jinja]"`, `"hedron[dev]"`.

## Next reading

- [Evaluate Hedron](evaluate.md) · [How to read Hedron docs](../getting-started/how-to-read.md)
- [What’s new in 0.10](whats-new-0.10.md) · [Upgrade](upgrade.md)
- [Support](support.md) (no commercial SLA)
