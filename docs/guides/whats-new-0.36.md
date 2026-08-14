# What’s new in 0.36

**Published** as `v0.36.0` (in-tree tip; PyPI/GitHub Release pending tag). Pin
`hedron>=0.36.0,<0.37`.

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
- Closing the 0.36 tracking issue awaits the tagged PyPI/GitHub release assets.
