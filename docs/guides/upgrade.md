# Upgrade to Hedron 0.41

This guide covers an application upgrade onto the **0.42.x** train
(current tip **`v0.42.0`**). New applications should use
[Build your first app](../getting-started/quickstart.md).

## Summary

Hedron 0.42.x ships allowlisted typed browser composition, subject-bound draft transfer,
progressive navigation/restoration, content-free traces, and element/region failure
isolation (D-069 / RFC-0060):

- Allowlisted typed composition with schema / authz / bounds / fallback
- Draft-only `sessionStorage` transfer with subject namespace and single-consume clearing
- Native/HTMX navigation ownership with deterministic title/focus/scroll/popstate behavior
- Content-free traces and per-element/region failure containment
- Regression packet for the locked 0.41 issue list

Prior trains remain in force: Web Component authoring kit (0.40), rich data /
OptimisticMutation (0.39), high-fidelity charts (`hedron-charts` `0.2.x`, 0.38), Alpha
`hedron-elements` form/primitives (0.37), Web Component ABI (0.36), MCP
(`hedron-mcp` `0.2.x`), Workbench ASGI (`fastapi-workbench` `1.x`), and Posit
(`hedron[posit]` / `HedronPosit`). Polling remains the production recommendation for live
status. SSE, WebSocket, streaming, and navigation preload remain experimental. Optional
preload / View Transitions never affect correctness.

## Before upgrading

1. Commit or back up your lockfile.
2. Confirm you are on a recent pin (`hedron>=0.29.0,<0.30` through `>=0.40.0,<0.41`,
   or the tip pin already).
3. If you rely on client composition or draft restore, review the allowlist / subject /
   fallback contracts — see [What's new in 0.41](whats-new-0.41.md).
4. If you use editable grids or charts, keep `hedron[data]` / `hedron[charts]` on the
   tip pin (or `hedron-charts>=0.2.0,<0.3`).
5. If you use Posit Workbench or Connect, prefer `hedron[posit]` / `HedronPosit`.
6. Optional: keep `hedron[elements]` for Alpha form-associated hosts from 0.37+.

## Install

```bash
python -m pip install -U "hedron>=0.42.0,<0.43"
python -m pip install -U "hedron[data]>=0.42.0,<0.43"
python -m pip install -U "hedron[charts]>=0.42.0,<0.43"
# independent charts satellite:
python -m pip install -U "hedron-charts>=0.2.0,<0.3"
# optional Alpha elements:
python -m pip install -U "hedron[elements]>=0.42.0,<0.43"
```

## Behavioral notes (0.40 → 0.41)

1. **Composition** is allowlisted `CustomEvent` → registered action / `InteractionGraph`
   only; event details are untrusted and bounded, with an ordinary form/link or
   full-fragment fallback on every graph.
2. **Draft transfer** is opt-in, same-origin `sessionStorage` only, namespaced by
   application + route family + element contract + schema + authenticated subject
   fingerprint, with mandatory clearing on logout / subject change / submit / discard /
   expiry / incompatibility / rollback.
3. **Navigation** remains server-authoritative; optional preload / View Transitions never
   affect correctness and honor reduced motion.
4. **Rollback** from 0.41 tip: pin `hedron>=0.40.0,<0.41` (and keep charts on
   `hedron-charts>=0.2.0,<0.3` if needed).

## After upgrading

- Smoke any composition graphs and draft-restore flows against ordinary form/link fallbacks.
- Confirm logout / subject change clears draft transfer state.
- Re-run your app's critical paths on Chromium; Firefox/WebKit remain in the CI matrix.

## See also

- [What's new in 0.41](whats-new-0.41.md)
- [What's new in 0.40](whats-new-0.40.md)
- [Release notes](release-notes.md)
- [upgrade-fixtures-041](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/upgrade-fixtures-041.md)
- [COMPATIBILITY](../COMPATIBILITY.md)
- [RELEASE_0_41](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_41.md)
