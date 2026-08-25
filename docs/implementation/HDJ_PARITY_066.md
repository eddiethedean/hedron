# Phase 0.66 implementation: HDJ parity and registry integration

**Authority:** [RFC-0093](../rfcs/RFC-0093-HDJ-PARITY-AND-REGISTRY-INTEGRATION.md)  
**Decisions:** D-111 / D-112  
**Baseline:** `v0.65.0`

## Delivered HDJ foundation

1. `JinjaBinding` provides immutable application identity and a deterministic registry projection.
2. Registry capture imports trusted registered components, application-approved public asset URLs,
   theme names, and redacted application-style facts without depending on `hedron`.
3. App-bound logical IDs resolve to explicit live handles and render through the active HDJ metadata
   session; cross-app handles fail before environment construction.
4. Catalog facts, registered TypeSchema, and included FeatureBundle facts are app-scoped globals.
5. `HdjContext` carries bounded HTMX request facts plus theme/style/provider/binding facts.
6. Provider manifests cover data, charts, maps, elements, and extras.
7. Static feature checking recognizes the new helpers and refuses undeclared custom-profile use.
8. Render traces include app identity, binding fingerprint, locale, theme, and redacted HTMX facts.

## Work packages

| Work package | Outcome | Gate |
|---|---|---|
| W0 contract and honesty | RFC, decisions, capability inventory, explicit deferrals | `CONTRACT-066` |
| W1 binding snapshot | immutable app identity, fingerprint, cross-app refusal | `BINDING-066` |
| W2 registry projection | components, approved public asset URLs, themes, redacted styles | `REGISTRY-066`, `STYLE-066` |
| W3 interactions | live logical-ID views/forms, catalog/schema/bundle facts | `INTERACTION-066` |
| W4 request context | explicit bounded HTMX facts and trace projection | `CONTEXT-066` |
| W5 providers | generic manifest parity for first-party satellites | `PROVIDER-066` |
| W6 hardening | strict sinks, no manifest execution, compatibility, typing | `SECURITY-066`, `COMPAT-066` |
| W7 docs/package | public API, examples, release/version evidence | `DOCS-066`, `PKG-066` |

## Expanded issue work packages

The phase intake added every unresolved repository issue. These packages remain Planned and block
the 0.66 cut; their authoritative per-issue rows live in
[`open-issues-066.toml`](../acceptance/open-issues-066.toml).

| Work package | Issues | Outcome | Gates |
|---|---|---|---|
| W8 strict JSON boundaries | #719, #720, #723, #724 | finite inputs and standards-valid HTMX/map/chart payloads | `HTMX-JSON-066`, `MAP-NUMERIC-066`, `ALTAIR-JSON-066`, `PLOTLY-JSON-066` |
| W9 transactional/lifecycle behavior | #718, #726 | audit-hook atomicity and producer-failure propagation | `DATA-AUDIT-066`, `WS-PRODUCER-066` |
| W10 input and security bounds | #721, #722, #727 | null-safe claims, bounded archives, finite rate windows | `CLAIM-REDACT-066`, `THEME-ARCHIVE-066`, `AUTH-RATE-066` |
| W11 packaging ceilings | #725 | valid major-version dependency range generation | `PIN-CEILING-066` |
| W12 typography presentation | #728, #729, #730 | bounded measure, safe effects, contextual variants | `TYPE-MEASURE-066`, `TYPE-EFFECT-066`, `CONTEXT-PRESENT-066` |

## Deferred boundaries

Dynamic dependencies, foreign Jinja execution, and installed-package HDJ namespaces remain
inventory-only/unsupported in the render path. They require a future loader authority and likely an
HDJ v2 source contract. They are not counted as 0.66 capabilities.

## Verification

Focused HDJ evidence lives in `tests/jinja/test_hdj_0_66.py`. The gate runner also executes the complete
Jinja suite, Ruff, Pyright, package metadata checks, and the existing adapter/component regression
paths. Those checks verify W0–W7 only. W8–W12 need focused regression tests and Verified issue gates
before release; a coordinated train changelog may claim only behavior linked from this document.
