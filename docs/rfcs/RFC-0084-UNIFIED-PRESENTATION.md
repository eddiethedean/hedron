# RFC-0084: Unified presentation and zero-application-CSS

**Status:** Accepted  
**Target phase:** 0.57 (`v0.57.0`)  
**Decision:** D-099  
**Stage 0 contract refine:** D-100  
**Published predecessor:** `v0.56.0`  
**Refine baseline:** in-tree `0.56.1`  
**Tracking:** [#558](https://github.com/eddiethedean/hedron/issues/558)–[#570](https://github.com/eddiethedean/hedron/issues/570)

**Revision:** 2026-08-21 — ownership and Stage 0 contract locked. This revision changes
contracts and acceptance artifacts only; it adds no runtime API and does not change versions.

## Summary

Phase 0.57 makes Hedron's existing presentation vocabulary real across built-ins and closes the
remaining application-CSS gaps exposed by a production Data Mover-class workspace. Values are
finite, semantic, theme-token-driven, strict-CSP compatible, and represented by stable
`data-hedron-*` markers. Existing calls keep their markup and visual defaults unless an explicit
compatibility diagnostic and migration path says otherwise.

## Goals

- One shared appearance authority for controls, fields, statuses, navigation, surfaces, and chrome.
- CSP-safe spacing, responsive tracks/spans, minimum sizing, wrapping, truncation, and line clamp.
- Typed surfaces, application chrome, static data/resource rows, avatar/identity, upload, and
  process-flow presentation.
- A representative authenticated workspace with no application-owned component/layout CSS.
- Three-engine browser, keyboard, screen-reader semantics, forced-colors, reduced-motion, RTL,
  print, long-content, narrow viewport, and 200% zoom evidence.

## Non-goals

- A free-form CSS/property DSL, arbitrary runtime stylesheet generation, or an `unsafe-inline`
  requirement.
- Replacing application domain semantics, authorization, content policy, brand assets, or bespoke
  layouts.
- Visual DOM reordering, inaccessible priority hiding, implicit sensitive text in `title`, or color
  and animation as the only state signal.
- Replacing `DataEditor`, adding client-side data management, changing upload security budgets, or
  reopening 0.54–0.56 workflow/security scope.
- Runtime symbols, numeric breakpoints/limits, version bumps, registry claims, or a 1.0 schedule
  during Stage 0.

## Shared authority and marker contract

The existing `hedron_core.builtins.appearance` module remains the authority. Stage 1 may extend its
closed enums but must not create component-local synonyms. The shared vocabulary is:

- `size`: `sm | md | lg`
- `density`: `compact | comfortable | spacious`
- `appearance`: family-scoped values drawn from `solid | outline | soft | ghost | plain | raised`
- `emphasis`: `primary | secondary | neutral | danger`
- `tone`: existing semantic tones; never the only state signal
- `width`: `content | field | full`
- `padding`, `shape`, `elevation`: closed token names, not lengths or CSS fragments

Supported values emit normalized `data-hedron-size`, `data-hedron-density`,
`data-hedron-appearance`, `data-hedron-emphasis`, `data-hedron-tone`, and family-specific bounded
markers. Invalid values or combinations raise the shared presentation diagnostic before render.
Theme/container defaults may cascade, but explicit component values win predictably.

## CSP-safe layout contract

- Standard and strict `style-src 'self'` are reference policies. Supported layout values compile to
  first-party stylesheet selectors; public APIs do not require inline style attributes.
- `Grid` and `FormGrid` share the existing breakpoint vocabulary. Responsive maps are normalized,
  ordered, finite, and serializable.
- Tracks use named sizes and bounded ratios. `GridItem` spans/order cannot change semantic DOM,
  reading, or tab order.
- Flex/grid containers own required `min-width: 0` and overflow containment.
- Custom CSS lengths are outside the Supported 0.57 API. Existing accepted length-like values use a
  documented compatibility path and may diagnose rather than silently fall back.

## Content and interaction invariants

1. Truncated or priority-hidden important content has an explicit full-content path. Hedron never
   copies potentially sensitive values into `title` automatically.
2. Linked resource rows cannot contain illegal nested interactive controls; an action-bearing row
   uses separate link/action targets and valid keyboard order.
3. Decorative connectors, activity dots, and motion are never the accessible source of truth.
4. Reduced motion produces a static equivalent; forced colors retains boundaries and states.
5. Print expands bounded scroll/truncation where feasible and never silently clips authoritative
   table/resource content.
6. Fragment replacement needs no custom client lifecycle to restore component presentation.
7. FileUpload display limits are derived from the same `UploadField`/budget authority that enforces
   them; validated HTMX hooks reuse existing allowlists.

## Locked component families

| Family | Stage 1 contract | Issues |
|---|---|---|
| Shared controls | Adopt shared size/density/appearance/emphasis/width | #568 |
| Layout/content | CSP-safe spacing; responsive tracks/spans; overflow contract | #558, #559, #562 |
| Surfaces/chrome | Surface/Card/Section plus typed Brand, AccountSummary, EnvironmentBanner, NavStatus, footer | #560, #564 |
| Data/identity | Static Table policy, ResourceList/ResourceRow, Avatar, Identity | #566, #567, #569 |
| Workflow | FileUpload, compact/activity Status, typed ProcessFlow steps/connectors | #561, #563, #565 |
| Integration | Authenticated zero-application-CSS reference workspace | #570 |

`AvatarGroup` is not required for 0.57. `Section` remains a semantic landmark; a generic `Surface`
owns purely visual grouping if appearance would otherwise overload landmark semantics.

## Gate plan

| Gate | Verified means |
|---|---|
| `CONTRACT-057` | RFC/decisions, schemas, vocabulary, marker and diagnostic locks |
| `CSP-057` | Requested and computed layout values under strict CSP; invalid-value diagnostics |
| `LAYOUT-057` | Grid/FormGrid/overflow evidence across responsive and international modes |
| `SURFACE-057` | Surface and typed AppShell chrome snapshots and semantics |
| `DATA-057` | Table/resource/identity semantics, responsive policy, full-content paths |
| `WORKFLOW-057` | Upload/status/process-flow state, keyboard, swaps, motion and color independence |
| `REGRESS-057` | 0.56 security/CSP plus 0.54–0.55 composition/workflow compatibility |
| `ZERO-CSS-057` | Reference workspace has no application component/layout CSS |
| `PKG-057` | Wheels, docs, exports, migration, inventories, metadata, and release rehearsal |

## Package ownership

- `hedron-core`: vocabulary, validation, markers, CSS assets, portable components and render tests.
- `hedron`: FastAPI composition, safe HTMX/upload integration, reference workspace and migration.
- `hedron-elements`: matching browser behavior where a component owns client lifecycle.
- `hedron-conformance`: portable marker/semantic fixtures and adapter-independent schemas.
- `hedron-sim`, sample kit, Explorer, adapters, and extras consume public contracts only and prove
  declared parity; they do not fork the vocabulary.

## Compatibility and testing

The source fixture is published `v0.56.0`, supplemented by the in-tree `0.56.1` hardening state.
Golden fixtures cover existing default markup, presentation diagnostics, and explicit migration.
Browser evidence runs Chromium, Firefox, and WebKit. Geometry evidence records requested markers and
computed results rather than treating serialized inline markup as proof.

All new public presentation APIs begin `beta`. Cut requires every 0.57 row Verified with zero
Deferred and no unresolved #558–#569 scope without an accepted destination and compatibility note.

## Resolved questions (D-099 / D-100)

1. **Authority?** Existing `hedron_core.builtins.appearance`, extended rather than forked.
2. **Custom lengths/CSS?** Not Supported; finite token/ratio values compile to first-party CSS.
3. **Surface semantics?** `Section` stays semantic; `Surface` may own visual-only grouping.
4. **Responsive order?** DOM/reading/tab order remains authoritative.
5. **Truncation disclosure?** Explicit caller/component full-content path; never implicit `title`.
6. **Upload limits?** One authority shared with 0.55/0.56 enforcement.
7. **Baseline?** Published `v0.56.0` plus in-tree `0.56.1`; target `v0.57.0`.
8. **Stage 0 runtime/version changes?** None.
