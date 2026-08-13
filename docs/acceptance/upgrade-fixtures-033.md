# Upgrade fixtures for phase 0.33 (`PARITY-033` / `PKG-033`)

Baseline: Published Hedron tip `v0.32.0` with `hedron-workbench>=0.32.0,<0.33` and
`fastapi-workbench>=1.0.0,<2.0`.

## Public API continuity (through at least 0.35)

These symbols remain importable after the `hedron-posit` extraction:

- `HedronWorkbench`
- `workbenchify` (where documented)
- `hedron-workbench run` / `check` / `doctor`
- `hedron[workbench]` extra
- Existing `HEDRON_WORKBENCH_*` configuration keys

## Behavioral deltas at `0.33.0` (after Stage 1)

| Topic | `0.32.x` | `0.33.x` |
|---|---|---|
| Preferred facade | `HedronWorkbench` | `HedronPosit` (`hedron[posit]`) |
| Compat class | primary | `HedronWorkbench(HedronPosit)` thin subclass |
| Dependency graph | `hedron-workbench -> hedron + fastapi-workbench` | `hedron-workbench -> hedron-posit -> hedron + fastapi-workbench` |
| Connect cookie bridge | not a Supported product surface | Supported only if Stage 0 reproduced loss; otherwise extension-point only |
| Deprecation warning | n/a | none in 0.33 |

## Fixture expectations

1. Inactive ordinary-Hedron behavior outside Posit runtimes is unchanged.
2. Workbench pre-import discovery, mount, URL, cookie, CSRF, and WebSocket corpora remain green.
3. Clean upgrade from `hedron-workbench==0.32.0` installs `hedron-posit` transitively without a cycle.
4. Rollback / mixed-train uninstall leaves no `hedron_posit` import requirement on apps that only
   imported `hedron_workbench`.
