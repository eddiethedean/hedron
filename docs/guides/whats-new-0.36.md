# What’s new in 0.36

**Published** as `v0.36.0`. Pin `hedron>=0.36.0,<0.37`.

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
python -m pip install -U "hedron>=0.36.0,<0.37"
python -m pip install "hedron[elements]>=0.36.0,<0.37"
```

## Notes

- Live SSE/WS remain experimental; polling stays the Supported production story.
- `hedron-elements` is Alpha / incubator until phase **0.41**.

## See also

[RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) ·
[RELEASE_0_36](../acceptance/RELEASE_0_36.md) ·
[What’s ready](whats-ready.md) ·
[Upgrade](upgrade.md)
