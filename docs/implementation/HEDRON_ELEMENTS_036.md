# Phase 0.36 implementation plan: Web Component ABI / lifecycle foundation

This plan turns [RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) into reviewable work for
phase **0.36** only. It is not authorization to cut until every gate row is Verified.
RFC-0060 is **Accepted** (D-064); later phases (0.37–0.41) keep their own Stage 0 packets.

## Outcome

Publish `v0.36.0` with Alpha `hedron-elements` `0.36.0`, one public element ABI, SSR/HTMX
lifecycle proof for `hedron-example`, and portable browser/security/a11y/packaging evidence.
This phase is **not** production-grade Web Components and **not** Hedron `1.0`.

The phase is complete only when every row in
[`release-gate-0.36.toml`](../acceptance/release-gate-0.36.toml) is Verified.

## Decisions already locked

| Topic | Decision |
|---|---|
| Primary scope | Element ABI + lifecycle foundation (D-064) |
| Gate IDs | `ABI-036` … `PKG-036` (nine distinct rows; no `PRESENT-036`) |
| Reference element | `hedron-example` (not form-associated) |
| Package | Alpha `hedron-elements` `0.36.0`, train-aligned pin |
| Browser floor | Playwright Chromium / Firefox / WebKit |
| “100 elements” | 100 upgrade/swap **instances** of the reference element |
| Baseline | Published `v0.35.0` |
| Tracking | [#92](https://github.com/eddiethedean/hedron/issues/92) |
| Non-goals | No hydration/VDOM/global store/app Node build; no forms/`InteractionState`/gestures; no tip bump in Stage 0 |

## Stage 0 — contract refine (no behavior change)

**Goal:** locked cut matrix, Accepted RFC, gate manifest (Planned), acceptance packet.

Deliverables:

- Accepted RFC-0060, D-064, this plan
- `release-gate-0.36.toml` with Planned rows
- `RELEASE_0_36.md` acceptance skeleton
- `upgrade-fixtures-036.md`, `security-review-036/BRIEF.md`
- Tracking [#92](https://github.com/eddiethedean/hedron/issues/92) synced to 0.36 gates
- Spec tighten: frozen markup, diagnostic catalog, 0.36/0.37 boundaries

**Explicitly forbidden in Stage 0:**

- Creating `packages/hedron-elements/` or adding a uv workspace member
- Adding `hedron[elements]` extras or bumping the living tip off `0.35.x`
- Implementing browser modules, registry runtime, or host mounts

**Exit:** `python scripts/verify_pkg_36.py --allow-planned` green.

## Stage 1 — gate plumbing (post-refine)

Flesh out `scripts/check_*_036.py` beyond Stage 0 stubs; keep Planned until evidence exists.
Wire CI jobs (`test` / `browser` / `packaging`) to the gate commands.

## Stage 2 — package bootstrap (`ELEMENTS-036`)

- Add `packages/hedron-elements` (framework-neutral; depends on `hedron-core` only)
- Asset/build policy: repo tooling → shipped fingerprinted modules + source maps
- Register Alpha row in fleet inventory (append-only; do not reopen `FLEET-035`)
- Optional `docs/packages/hedron-elements.md`

## Stage 3 — ABI + state fixtures (`ABI-036`, `STATE-036`)

- Registry schema + naming/conflict fixtures
- Frozen markup encoding fixtures
- `ElementStateOwnership` corpus + `HED-ELEMENT-*` / `HED-ELEMENT-STATE-*` diagnostics

## Stage 4 — SSR + lifecycle (`SSR-036`, `LIFECYCLE-036`)

- Pre-upgrade / JS-off / failed-module fallback
- Connect/disconnect, HTMX cleanup, ≥100 instance swap/history leak corpus

## Stage 5 — security, a11y, browser (`SECURITY-036`, `A11Y-036`, `BROWSER-036`)

- CSP / Trusted Types / event adversarial suite
- Accessibility state matrix
- Three-engine matrix; bridge ≤12 KiB gzip; load budgets

## Stage 6 — cut (`PKG-036`)

- Flip gates to Verified; `verify_pkg_36.py` without `--allow-planned`
- Bump train to `0.36.0`; publish Alpha `hedron-elements`; close #92

## Cut verification

At `v0.36.0` cut:

```bash
python scripts/verify_pkg_36.py
python scripts/check_release_gate.py 0.36.0 --execute-verified
```

During packet refine:

```bash
python scripts/verify_pkg_36.py --allow-planned
```
