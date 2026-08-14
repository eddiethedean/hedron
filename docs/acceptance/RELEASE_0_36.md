# Hedron `v0.36` Web Component ABI / lifecycle foundation acceptance

**Status:** Stage 0 refined (2026-08-13). **Not Published.** Living tip remains
`v0.35.0` / pin `hedron>=0.35.0,<0.36` until cut.

Phase 0.36 establishes one versioned, framework-neutral Web Component ABI and ships Alpha
`hedron-elements` with SSR/native HTML as the canonical fallback and HTMX as the request
layer. Baseline: Published `v0.35.0`. Evidence is indexed by
[`release-gate-0.36.toml`](release-gate-0.36.toml). **Zero Deferred:** every 0.36-owned gate
must be Verified at cut.

Owning decision: [D-064](../DECISIONS.md). Design:
[RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) (**Accepted** 2026-08-13).
Implementation: [HEDRON_ELEMENTS_036](../implementation/HEDRON_ELEMENTS_036.md). Tracking:
[#92](https://github.com/eddiethedean/hedron/issues/92). Program acceptance checklist:
[WEB_COMPONENT_PLATFORM.md](WEB_COMPONENT_PLATFORM.md).

## Release contract

- Coordinated train cut `hedron` / `hedron-core` (and adapters as required) `0.36.0`.
- New Alpha distribution **`hedron-elements` `0.36.0`** (pin `>=0.36.0,<0.37`), depends on
  `hedron-core` only; no FastAPI/Flask/Django imports; no application Node.js.
- Reference element: light-DOM **`hedron-example`** (controlled `status` + disposable local UI;
  not form-associated).
- Fleet inventory amendment at cut: register `hedron-elements` with owner, Alpha channel,
  compatibility range, and production-grade destination at **0.41** without reopening
  `FLEET-035` (append-only inventory row + disposition `incubator` until 0.41).
- Python 3.11–3.14 remain the supported interpreter matrix.
- Browser floor: Playwright Chromium / Firefox / WebKit
  (`tests/browser/test_browser_matrix.py`).
- This phase is **not** production-grade Web Components, not `stable` tag/event promotion, and
  **not** Hedron `1.0`.

## Entry criteria

- [x] `v0.35.0` published; D-063 Accepted; #91 closed
- [x] D-064 Accepted; RFC-0060 Accepted; open questions resolved
- [x] Tracking issue #92 bound to phase 0.36 gate IDs
- [x] Planned release-gate rows and checker ownership reviewed
- [x] Implementation plan present; Stage 0 forbids package bootstrap

## Exact cut matrix

| Lane | Topology | Required evidence |
|---|---|---|
| ABI registry | Schema fixtures + conflict diagnostics | `check_abi_036.py` / ABI fixtures |
| Package wheel | Framework-neutral `hedron-elements` | `check_elements_036.py` |
| Lifecycle | Connect/disconnect + HTMX/history races | `check_lifecycle_036.py` + browser corpus |
| SSR / ownership | JS-off / failed upgrade / DOM regions | `check_ssr_036.py` |
| State ownership | Controlled/local/draft/preference | `check_state_036.py` |
| Security | CSP / Trusted Types / event adversarial | `check_security_036.py` |
| Accessibility | Pre/upgraded/failed/swap/history | `check_a11y_036.py` |
| Browser / perf | Three engines; 100 **instances**; bridge ≤12 KiB gzip | `check_browser_036.py` |
| Packaging | Docs, manifests, SBOM/provenance, verifier | `verify_pkg_36.py` |
| Upgrade path | From `v0.35.0` | [`upgrade-fixtures-036.md`](upgrade-fixtures-036.md) |

## Locked evidence gates

| Gate | Owner | Verified means |
|---|---|---|
| `ABI-036` | `hedron` | Registry schema, naming, version negotiation, conflicts, fixtures, `HED-ELEMENT-*` |
| `ELEMENTS-036` | `hedron` | Framework-neutral wheel + `hedron-example` across FastAPI/Flask/Django/Explorer |
| `LIFECYCLE-036` | `hedron` | Connect/reconnect/disconnect, HTMX/history/OOB races, cleanup, leak corpus |
| `SSR-036` | `hedron` | Pre-upgrade/JS-off/failure fallback, structured-input bounds, DOM ownership |
| `STATE-036` | `hedron` | Ownership modes, reflection, conflict, persistence, `HED-ELEMENT-STATE-*` |
| `SECURITY-036` | `hedron` | CSP/Trusted Types/event adversarial suite |
| `A11Y-036` | `hedron` | Fallback/upgraded accessibility state matrix |
| `BROWSER-036` | `hedron` | Three engines; 100 upgrade/swap **instances**; budgets |
| `PKG-036` | `hedron` | Manifests, supply evidence, docs, release verifier; zero Deferred 0.36 rows |

## Cut verification

At `v0.36.0` cut (future):

```bash
python scripts/verify_pkg_36.py
python scripts/check_release_gate.py 0.36.0 --execute-verified
```

During packet refine (Stage 0):

```bash
python scripts/verify_pkg_36.py --allow-planned
```

## Exit

- [ ] Exact cut matrix has no `TBD` on Supported lanes
- [x] RFC-0060 Accepted and implementation plan matches it
- [ ] Every 0.36-owned release-gate row Verified with zero Deferred
- [ ] `hedron-elements` published Alpha `0.36.0`; fleet inventory amended
- [ ] Close #92 after release assets are published on GitHub/PyPI
