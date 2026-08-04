# What’s ready today

Operator-facing snapshot of the published **0.10.0** train. For evidence rows and
Deferred ownership, see [STATUS](../STATUS.md).

## Ship with confidence (Beta)

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

Pin versions in production. Breaking changes may still land on `0.x` under the
[compatibility policy](../COMPATIBILITY.md).

## Treat as Alpha / more volatile

- `hedron-charts` and chart backends
- `hedron-sample-kit` (plugin sample)

## Deferred (do not market as Supported)

- First-party dedicated live-transport sample app → owned `0.10.x` Deferred (`EXAMPLES-10-001`);
  use the copy-paste apps in [live interaction](live-interaction.md) until it ships
- Django QuerySet as a first-party DataSource → planned **0.11**
- Hedron-owned Django forms depth → **0.11**
- First-party camera/microphone capture UI → **0.15**
- Official HTMX SSE on Flask/Django (use polling) → see live guide
- Full multi-engine live browser matrix and some Explorer live traces → owned `0.10.x` Deferred rows in STATUS

## Recommended install

```bash
pip install "hedron>=0.10.0"
# or
hedron new my-app
```

Extras: `"hedron[data]"`, `"hedron[charts]"`, `"hedron[jinja]"`, `"hedron[dev]"`.

## Next reading

- [How to read Hedron docs](../getting-started/how-to-read.md)
- [What’s new in 0.10](whats-new-0.10.md) · [Upgrade](upgrade.md)
- [Support](support.md) (no commercial SLA)
