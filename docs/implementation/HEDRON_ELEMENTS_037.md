# Phase 0.37 implementation plan: form-associated elements and interactive primitives

This plan turns [RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) D-065 scope into
reviewable work for phase **0.37** only. It is not authorization to cut until every gate row is
Verified. RFC-0060 remains **Accepted** (D-064); this phase extends it under D-065.

## Outcome

Publish `v0.37.0` with Alpha `hedron-elements` `0.37.0`, form-associated reference controls,
`InteractionState`, semantic interactive primitives, and `GestureOverlayCatalog` proof on the
published 0.36 ABI. This phase is **not** production-grade Web Components and **not** Hedron
`1.0`.

The phase is complete only when every row in
[`release-gate-0.37.toml`](../acceptance/release-gate-0.37.toml) is Verified.

## Decisions already locked

| Topic | Decision |
|---|---|
| Primary scope | Form association, InteractionState, primitives, gestures/overlays (D-065) |
| Gate IDs | `FORM-037` … `PKG-037` (nine distinct rows) |
| Form references | `hedron-field-text`, `hedron-field-choice`, `hedron-field-file` |
| Primitive references | `hedron-disclosure`, `hedron-dialog` (+ tabs/menu/selection/upload in catalog) |
| InteractionState reference | `hedron-action-async` |
| Non-form ABI reference | `hedron-example` (unchanged; must not regress 0.36 gates) |
| Package | Alpha `hedron-elements` cut target `0.37.0`, train-aligned pin at cut |
| Browser floor | Playwright Chromium / Firefox / WebKit |
| Baseline | Published `v0.36.0` |
| Tracking | [#93](https://github.com/eddiethedean/hedron/issues/93); high-severity #230–#237 |
| Non-goals | No high-fidelity charts (0.38), OptimisticMutation (0.39), React bridge (0.40), draft transfer (0.41), production-grade graduation (0.42); no tip bump in Stage 0 |

## Stage 0 — contract refine (no behavior change)

**Goal:** locked cut matrix, D-065 Accepted, gate manifest (Planned), acceptance packet.

Deliverables:

- D-065, RFC-0060 D-065 resolved questions, this plan
- `release-gate-0.37.toml` with Planned rows
- `RELEASE_0_37.md` acceptance skeleton
- `upgrade-fixtures-037.md`, `security-review-037/BRIEF.md`
- `production-grade-inventory-037.toml` (baseline `v0.36.0`)
- Tracking [#93](https://github.com/eddiethedean/hedron/issues/93) synced to 0.37 gates
- High-severity remediations #230–#237 bound to `REGRESS-037` (D-065 amendment)
- Spec tighten: `form_contract` 0.37+ fields, 0.36/0.37 boundary, diagnostic names

**Explicitly forbidden in Stage 0:**

- No `ElementInternals` runtime, no new shipped form/gesture modules beyond planning docs
- No workspace version bump to `0.37.0`
- No flip of any 0.37 gate to Verified
- No adopter-facing “0.37 Published” wording in STATUS/RELEASE/release-notes

**Exit:** `python scripts/verify_pkg_37.py --allow-planned` green.

## Stage 1 — gate plumbing (post-refine)

Flesh out `scripts/check_*_037.py` beyond Stage 0 stubs; add empty/xfail test modules; wire CI
jobs (`test` / `browser` / `packaging`) to the gate commands. Keep Planned until evidence exists.

## Stage 2 — registry / `form_contract` (`FORM-037` prep)

Populate registry `form_contract` fields (association mode, value encoding, reset/restore,
validation mapping, fallback tag). Extend ABI fixtures without breaking 0.36 consumers.

## Stage 3 — `InteractionState` bridge (`ACTIONSTATE-037`)

Shared idle/pending/success/error/canceled machine in the bridge; derive transitions from HTMX
and registered job/polling lifecycles; concurrency policies (drop/replace/queue/parallel).

## Stage 4 — form-associated references (`FORM-037`, `VALIDITY-037`)

Implement `hedron-field-text`, `hedron-field-choice`, `hedron-field-file` with native fallback,
host matrices (FastAPI/Flask/Django), CSRF and server-validation integration.

## Stage 5 — semantic primitives (`PRIMITIVE-037`)

Lock catalog entries for disclosure, dialog, tabs, menu/popover, selection, bounded upload;
native-first review; keyboard/focus/lifecycle fixtures.

## Stage 6 — `GestureOverlayCatalog` (`INTERACT-037`)

Gesture and overlay contracts per
[WEB_COMPONENT_INTERACTION_CONTRACTS.md](WEB_COMPONENT_INTERACTION_CONTRACTS.md) §2–4;
pointer/keyboard equivalence, allowlists, top-layer, disconnect cleanup.

## Stage 7 — HTMX matrices (`HTMX-037`)

Inner/outer/OOB swaps, 422 validation fragments, duplicate submission, history restore,
slow/canceled requests — values, errors, focus, and authority preserved.

## Stage 8 — AT + security review (`AT-037`, security-review-037)

Representative keyboard and human screen-reader sessions; independent review packet with
redacted report and disposition ledger.

## Stage 9 — cut (`PKG-037`, `REGRESS-037`)

Flip gates to Verified; `verify_pkg_37.py` without `--allow-planned`; bump train to `0.37.0`;
publish Alpha `hedron-elements`; close #93 and high-severity #230–#237 when GitHub/PyPI
release artifacts are attached and those issues are fixed.

## Cut verification

At `v0.37.0` cut:

```bash
python scripts/verify_pkg_37.py
python scripts/check_release_gate.py 0.37.0 --execute-verified
```

During packet refine:

```bash
python scripts/verify_pkg_37.py --allow-planned
```
