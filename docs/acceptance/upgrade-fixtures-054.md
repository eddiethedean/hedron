# Phase 0.54 upgrade and rollback fixtures

**Status:** Verified at Published in-tree `v0.54.0` (D-093 / D-094)<br>
**Planning baseline:** Published in-tree `v0.53.0`<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.53.0`<br>
**Target:** Hedron `v0.54.0`<br>
**Decision/RFC:** D-093 / D-094 / [RFC-0081](../rfcs/RFC-0081-AUTHORING-LOOP-AND-CHROME.md)<br>
**Tracking:** [#538](https://github.com/eddiethedean/hedron/issues/538)–[#543](https://github.com/eddiethedean/hedron/issues/543)

PKG-054 upgrade source is **0.53**, not 0.52. Living tip is `v0.54.0` (tag/PyPI deferred).

## 0.53.0 install fixtures

1. Application DX: assets, diagnostics, routes, workflow, testgen, theme,
   discovery, fleet doctor (`hedron fleet`; `package_doctor: False`).
2. Sample kit Callout plugin and Explorer panel.
3. Simulator `SimApp` / subset helpers.
4. Notebook `start_preview` / token gate / localhost defaults.
5. Theme / AppShell / layout builtins.

## Honesty fixtures (Stage 1 migration)

1. Package doctor validates packages under authorship; it does not replace fleet.
2. Simulator unsupported features fail visibly; no silent parity.
3. Notebook remains non-production; non-loopback rejected by default.
4. Shared schema is imported from `hedron_conformance.authoring_loop` only.
5. Rollback to 0.53.0 restores repository-only Stage 0 seams without Stage 1
   contract symbols.
