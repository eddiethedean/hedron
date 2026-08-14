# Hedron `v0.37` form-associated elements and interactive primitives acceptance

**Status:** **Published** as `v0.37.0` (2026-08-14; commit-based cut; GitHub Release / PyPI tag
are post-cut maintainer assets). Living tip is **`v0.38.0`** / pin `hedron>=0.38.0,<0.39`.

Phase 0.37 ships form-associated custom elements, `InteractionState`, semantic interactive
primitives, and `GestureOverlayCatalog` contracts on the published 0.36 ABI without splitting
ordinary HTML navigation, HTMX submission, server validation, or accessible fallback into
separate models. Baseline: Published **`v0.36.0`**. Evidence is indexed by
[`release-gate-0.37.toml`](release-gate-0.37.toml). **Zero Deferred:** every 0.37-owned gate
is Verified at cut.

Owning decision: [D-065](../DECISIONS.md). Design:
[RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) (**Accepted**; extends D-064).
Implementation: [HEDRON_ELEMENTS_037](../implementation/HEDRON_ELEMENTS_037.md). Tracking:
[#93](https://github.com/eddiethedean/hedron/issues/93). High-severity remediations (D-065
amendment; issue bodies remain normative):
[#230](https://github.com/eddiethedean/hedron/issues/230),
[#231](https://github.com/eddiethedean/hedron/issues/231),
[#232](https://github.com/eddiethedean/hedron/issues/232),
[#233](https://github.com/eddiethedean/hedron/issues/233),
[#234](https://github.com/eddiethedean/hedron/issues/234),
[#235](https://github.com/eddiethedean/hedron/issues/235),
[#236](https://github.com/eddiethedean/hedron/issues/236),
[#237](https://github.com/eddiethedean/hedron/issues/237).
Program acceptance checklist: [WEB_COMPONENT_PLATFORM.md](WEB_COMPONENT_PLATFORM.md).

## Release contract (at cut)

- Coordinated train cut `hedron` / `hedron-core` (and adapters as required) `0.37.0`.
- Alpha **`hedron-elements` `0.37.0`** (pin `>=0.37.0,<0.38`), depends on `hedron-core` only.
- Reference elements: **`hedron-field-text`**, **`hedron-field-choice`**, **`hedron-field-file`**
  (form association); **`hedron-disclosure`**, **`hedron-dialog`** (primitive catalog);
  **`hedron-action-async`** (`InteractionState`). **`hedron-example`** remains non-form.
- Fleet inventory amendment at cut: update `hedron-elements` pin/compatibility in
  `production-grade-inventory-037.toml` without reopening `FLEET-035`.
- Browser floor: Playwright Chromium / Firefox / WebKit
  (`tests/browser/test_browser_matrix.py`).
- This phase is **not** production-grade Web Components, not `stable` tag/event promotion, and
  **not** Hedron `1.0`.

## Outcome

Supported rich controls submit and validate as real forms with and without HTMX/upgrade. Selected
primitives share focus, lifecycle, and failure contracts — no separate ad hoc loader, focus,
event, or cleanup protocol.

## Non-goals

- Reimplementing native controls for visual consistency alone.
- Client-owned business validation, authorization, CSRF, form persistence, or upload authority.
- Hiding an inaccessible upgraded control behind an accessible but non-equivalent fallback.
- High-fidelity charts (0.38), `OptimisticMutation` / rich surfaces (0.39), React bridge (0.40),
  draft transfer (0.41), and production-grade graduation (0.42).

## Entry criteria

- [x] `v0.36.0` published; D-064 Verified; #92 closed
- [x] D-065 Accepted; RFC-0060 D-065 resolved questions present
- [x] Tracking issue #93 bound to phase 0.37 gate IDs
- [x] Open high-severity issues #230–#237 bound to 0.37 (`REGRESS-037`)
- [x] Planned release-gate rows and checker ownership reviewed
- [x] Implementation plan present; Stage 0 forbids runtime form/gesture implementation

## Exact cut matrix

| Lane | Topology | Required evidence |
|---|---|---|
| Form parity | Native + HTMX submission across hosts | `check_form_037.py` |
| Validity | ElementInternals, fallback, CSRF, server errors | `check_validity_037.py` |
| Primitives | Locked catalog, keyboard/focus, native-first | `check_primitive_037.py` |
| InteractionState | Async state, concurrency, cancel/retry/job | `check_actionstate_037.py` |
| Gestures/overlays | Catalog matrices, top-layer, cleanup | `check_interact_037.py` |
| HTMX | Swap/422/history/duplicate/slow/cancel | `check_htmx_037.py` |
| Human AT | Keyboard + screen-reader form/primitives packet | `check_at_037.py` |
| Regression | Cross-host/browser/security/perf/docs; high-severity #230–#237 closed | `check_regress_037.py` |
| Packaging | Manifests, supply evidence, verifier | `verify_pkg_37.py` |
| Upgrade path | From `v0.36.0` | [`upgrade-fixtures-037.md`](upgrade-fixtures-037.md) |

## Locked evidence gates

| Gate | Owner | Verified means |
|---|---|---|
| `FORM-037` | `hedron` | Native and HTMX submissions match across controls, hosts, reset/restore, and error states |
| `VALIDITY-037` | `hedron` | ElementInternals/native fallback, constraint/server validation, labels/errors, and CSRF pass |
| `PRIMITIVE-037` | `hedron` | Locked catalog passes semantic fallback, keyboard/focus, lifecycle, and native-first review |
| `ACTIONSTATE-037` | `hedron` | Common async state/concurrency/progress/retry/cancel/job/late-response and accessible fallback pass |
| `INTERACT-037` | `hedron` | Gesture and overlay catalog passes pointer/keyboard/touch/focus/top-layer/security/swap/cleanup matrices |
| `HTMX-037` | `hedron` | Swap/422/history/duplicate/slow/cancel matrices preserve values, errors, focus, and authority |
| `AT-037` | `hedron` | Representative keyboard and human screen-reader form/primitives packet is dispositioned |
| `REGRESS-037` | `hedron` | Cross-host/browser/security/performance/compatibility/docs suites pass; high-severity issues #230–#237 closed |
| `PKG-037` | `hedron` | Clean wheels, manifests, SBOM/provenance/licenses, docs, release verifier; zero Deferred 0.37 rows |

## High-severity remediations (normative)

Issue bodies remain normative for `v0.37.0`. `REGRESS-037` is Verified only when every row is
closed. Mapped gates below are the primary evidence home; they do not split ownership away from
0.37. [#244](https://github.com/eddiethedean/hedron/issues/244) is a closed post-cut follow-on
to #237 (remaining active-content in attribute values).

| Issue | Defect | Primary gate |
|---|---|---|
| [#230](https://github.com/eddiethedean/hedron/issues/230) | HTMX `data-hx-*` aliases bypass EVAL-020 and SafeUrl gates | `HTMX-037` |
| [#231](https://github.com/eddiethedean/hedron/issues/231) | HedronFlask production session cookies omit Secure and SameSite | `REGRESS-037` |
| [#232](https://github.com/eddiethedean/hedron/issues/232) | MCP Streamable HTTP skips Origin checks when `allowed_origins` is None | `REGRESS-037` |
| [#233](https://github.com/eddiethedean/hedron/issues/233) | MCP `max_request_bytes` is checked after the body is fully buffered | `REGRESS-037` |
| [#234](https://github.com/eddiethedean/hedron/issues/234) | `validate_directory_upload` accepts raw NUL in paths | `VALIDITY-037` |
| [#235](https://github.com/eddiethedean/hedron/issues/235) | SelectSlider submits option indexes instead of option values | `FORM-037` |
| [#236](https://github.com/eddiethedean/hedron/issues/236) | Redis idempotency pointer delete is not atomic | `ACTIONSTATE-037` |
| [#237](https://github.com/eddiethedean/hedron/issues/237) | `render_element_markup` still emits `hx-on`, `js:` values, and `javascript:` URLs | `HTMX-037` |
| [#244](https://github.com/eddiethedean/hedron/issues/244) | `render_element_markup` still allows `style=`, `vbscript:`, and `data:` URLs (follow-on to #237) | `HTMX-037` |

## Cut verification

At Published `v0.37.0`:

```bash
python scripts/verify_pkg_37.py
python scripts/check_release_gate.py 0.37.0 --execute-verified
```

During packet refine / mid-implementation:

```bash
python scripts/verify_pkg_37.py --allow-planned
```

## Exit (at cut)

- [x] Exact cut matrix has no `TBD` on Supported lanes
- [x] RFC-0060 D-065 table matches this packet
- [x] Every 0.37-owned release-gate row Verified with zero Deferred
- [x] `hedron-elements` Alpha `0.37.0`; fleet inventory-037 amended
- [x] Tip/SSOT honesty for Published `0.37.0` (STATUS / RELEASE / adopter hubs)
- [x] High-severity issues #230–#237 closed
- [x] Close #93 after release assets are published on GitHub/PyPI

### Post-cut follow-on

- [x] [#244](https://github.com/eddiethedean/hedron/issues/244) closed (`style=` / `vbscript:` /
  `data:` in `render_element_markup`; same frozen ABI path as #237)
- [ ] `git tag` / push `v0.37.0`, PyPI publish, GitHub Release
