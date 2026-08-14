# What’s new in 0.36

**Published** as `v0.36.0`. Historical pin: `hedron>=0.36.0,<0.37`.
For new apps, use `hedron>=0.40.0,<0.41`; see [What’s new in 0.39](whats-new-0.40.md).

Phase 0.36 establishes the Web Component ABI foundation (RFC-0060 / D-064): a versioned
element registry, SSR/HTMX lifecycle rules, and `ElementStateOwnership`. This is **not**
production-grade Web Components and **not** Hedron `1.0`.

## Highlights

- **Web Component ABI foundation** (RFC-0060 / D-064): versioned element registry,
  SSR/HTMX lifecycle rules, and `ElementStateOwnership`.
- New Alpha package **`hedron-elements`** with shared bridge and reference element
  **`hedron-example`** (not form-associated; forms arrive in 0.37).
- Diagnostic families `HED-ELEMENT-*` and `HED-ELEMENT-STATE-*`.

## Install

```bash
# Historical 0.36 environment only; new apps should use the 0.39 pin above.
python -m pip install "hedron>=0.36.0,<0.37" "hedron[elements]>=0.36.0,<0.37"
```

## Notes

- Live SSE/WS remain experimental; polling stays the Supported production story.
- `hedron-elements` is Alpha / incubator until phase **0.42** (rephased by D-066).

## See also

[RFC-0060](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) ·
[RELEASE_0_36](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_36.md) ·
[What’s ready](whats-ready.md) ·
[Upgrade](upgrade.md)
