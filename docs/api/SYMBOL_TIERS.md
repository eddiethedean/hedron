# Symbol tiers (1.0 API honesty foundation)

**Status:** Living machine-checked inventory for the flagship root facade on the
**0.60.x** train. This is a foundation for an honest 1.0 freeze — it does **not**
schedule `1.0`
([D-038](https://github.com/eddiethedean/hedron/blob/main/docs/DECISIONS.md)).

## Why

`hedron.__all__` is much broader than the locked [stable facade](STABLE_FACADE.md).
Supported capability ≠ `stable` API. Before any public major, every root export must
carry an explicit tier so adopters and CI agree.

## Levels

| Tier | Meaning |
|---|---|
| `stable` | Compatibility-protected throughout `1.x` (see [STABILITY](STABILITY.md) / FACADE-023) |
| `beta` | May revise at minor boundaries with changelog/migration evidence |
| `experimental` | May change/remove without major; must stay labeled |
| `internal` | Not a public contract (should not appear on root long-term) |

## Inventory

Machine-checked file: [`export_tiers.toml`](export_tiers.toml)

- `[hedron]` — every name in `packages/hedron/src/hedron/__init__.py` `__all__`
- `[hedron.experimental_shims]` — root `__getattr__` compat aliases that re-export
  `hedron.experimental` (emit `DeprecationWarning`). **Remove before 1.0 freeze.**

Checker: `python scripts/check_symbol_tiers.py` (wired into `scripts/ci_checks.sh`
quality / core-neutral).

## Related

- [Public 1.0 readiness](../guides/one-point-zero-readiness.md)
- [STABLE_FACADE](STABLE_FACADE.md)
- [STABILITY](STABILITY.md)
- [LIVE_DISPOSITION](LIVE_DISPOSITION.md)
