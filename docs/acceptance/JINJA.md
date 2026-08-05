# HDJ authoring acceptance

> **Target:** phase 0.9 (**published**). `.hdj` is the optional, explicit, standards-first
> Jinja/HTML/HTMX format. Phase 0.10 closed head management, two-phase streaming, and
> version-aware HTMX reporting (`HDJ-10-*`); remaining browser-backed navigation/history/OOB
> lifecycle depth stays owned with `BROWSER-10-001` → `0.10.x`.

## Deferred ownership

Rows marked with a later phase are excluded from the 0.9 exit gate and owned here:

| Later phase | Owned HDJ work |
|---:|---|
| 0.10 (closed / follow-up) | Head management, two-phase streaming, and version-aware HTMX semantics are Verified on `v0.10.0`. Broader browser-backed navigation/history/OOB/lifecycle evidence remains Deferred with `BROWSER-10-001`. |
| 0.11 | Finite fingerprinted dynamic dependency manifests, foreign Jinja/package namespaces, native route/CSRF/context/response facades, multi-framework PAGE/FRAGMENT/forms parity, asset/CSP pipeline reconciliation, and CLI/build/Explorer production inventory. |
| 0.12 | `hedron.data`/`hedron.charts` provider parity and bounded high-volume presentation evidence. |
| 0.13 | Async filter/global I/O contracts, operation budgets, deadlines, cancellation, and tracing. **Verified** (`HDJ-DEF-013`). |
| 0.14 | Optional exact loop/macro instrumentation, contracted custom-extension/helper evidence, broader contextual analysis, and portable checker fixtures. |

## Packaging and identity

- [x] `hedron-jinja` is a separate distribution importing as `hedron_jinja`.
- [x] `hedron-core` and default `hedron` have no required Jinja/MarkupSafe dependency or eager import.
- [x] `hedron[jinja]` installs the version-matched integration package.
- [x] Documentation consistently uses `.hdj` as the versioned Hedron Jinja format while making
  clear that the template body follows normal Jinja semantics.
- [x] Metadata, typing marker, changelog, compatibility matrix, wheel/sdist clean-install rehearsal,
  and offline startup evidence pass (`PKG-09-001` / `scripts/verify_pkg_09.py`).

## Source format and feature declarations

- [x] Only UTF-8 `.hdj` sources with a byte-zero `---hdj` TOML prologue enter the HDJ loader;
  missing/unterminated prologues and unsupported versions fail with source diagnostics.
  Duplicate TOML keys follow `tomllib` semantics (last-wins); HDJ does not invent a stricter
  duplicate-key parser in format v1.
- [x] `version`, `kind`, and `profile` are required static values; unknown keys, wrong types,
  expressions, and executable values fail before Jinja compilation.
- [x] `page`, `fragment`, and `library` kinds enforce document shape and valid entry-point use;
  `TemplateSpec.mode` may assert but never override source kind.
- [x] Format-v1 `minimal`, `standard`, `full`, and `custom` profiles expand to documented exact
  feature sets independent of registry ordering.
- [x] Namespaced `features` reject unknown, unavailable, incompatible, and used-but-undeclared
  surfaces; unused declarations produce useful diagnostics rather than changing output.
- [x] Inferred browser/HTMX capabilities must be covered by `requires`; under-declaration fails,
  over-declaration warns, and neither form grants policy permission.
- [x] Prologue `assets` and `regions` merge deterministically with application contracts;
  format v1 rejects dynamic dependencies. Build/Explorer inventory wiring is **phase 0.11**.
- [x] Public immutable `TemplateDeclaration`/`describe()` exposes format version, kind, profile,
  declared/effective features, requirements, assets, regions, source digest, and body start line
  without render. Format v1 rejects dynamic dependencies rather than exposing dependency-bound
  namespaces; finite manifests are **phase 0.11**.
- [x] Source body line numbers survive prologue removal in Jinja exceptions, diagnostics, and
  traces. SARIF/Explorer wiring is **phase 0.11**; richer portable formats are **phase 0.14**.
- [x] Ordinary `.html`/`.jinja` sources stay outside the HDJ loader. **Phase 0.11:** add the finite,
  fingerprinted foreign boundary; foreign source cannot invoke Hedron tags.

## Standards-first freedom

- [x] Literal trusted source accepts standard HTML, custom elements, `data-*`, `aria-*`, CSS,
  JavaScript, and pinned HTMX attributes without requiring component wrappers.
- [x] Strict mode governs dynamic data/context and static contracts; it does not act as a reduced
  HTML grammar or silently override deployment policy.
- [x] A minimal `.hdj` file needs only three concise prologue fields before ordinary HTML/Jinja and
  renders without component wrappers or semantic changes.
- [x] `strict=False` provides conventional trusted-Jinja freedom while
  preserving secrets, loader isolation, authorization, and response-header boundaries.

## Jinja conformance

- [x] Inheritance, blocks, `super`, includes, imports, macros, `call`, filters, tests, `set`,
  namespaces, conditions, loops/recursive loops, whitespace control, and comments have fixtures.
- [x] Explicit i18n, `do`, loop-control, filter/test/global availability works when configured before
  binding; arbitrary custom-extension evidence is **phase 0.14**.
- [x] Core async rendering requires explicit `jinja.async`. I/O declarations, operation tracing,
  cancellation, and deadline policy are **phase 0.13**.
- [x] Static referenced-template analysis uses Jinja's meta API and dynamic dependencies fail.
  Exact finite candidate manifests are **phase 0.11**; namespace-only bounds are never accepted.
- [x] HDJ extension state survives Jinja environment overlays without leaking bindings or sessions;
  no environment-specific state is stored unsafely on a reusable extension instance.
- [x] Unsupported `NativeEnvironment` and direct streaming paths fail with precise alternatives.

## Public context and contracts

- [x] Implemented `HedronJinja`, `HedronJinjaExtension`, `TemplateSpec`, and `TemplateSource` expose
  the core render path.
- [x] `TemplateSpec` binds runtime view type, source namespace, strict policy, and stable identity while
  source kind/features/assets/region IDs come from the `.hdj` prologue without contradictory truth.
- [x] Immutable `HdjContext` exposes mode, fragment status, locale/theme, immutable optional HTMX
  facts, reverse URLs, asset URLs, and CSRF markup without raw request/session/container/registry
  access. Native adapter facts are **phase 0.11**; scoped-style/validated-attribute helpers are
  **phase 0.14**.
- [x] Registration is explicit, local, duplicate-safe, immutable after freeze, and rejects
  factories without inspectable contracts.
- [x] Canonical application names reject traversal and ambiguity. Installed-package namespace,
  shadowing, and override policy are **phase 0.11**.

## Components and metadata

- [x] Inline components, explicit `with body`, named slots, trusted markup, direct-render failure,
  page/fragment shape, and initial component/output budgets have focused tests.
- [x] Nested components inside inheritance/includes/macros/loops/slots preserve source order and
  complete HTML/assets/headers/identity/diagnostic/trace metadata.
- [x] Required/defaulted/unknown/deprecated/secret/identity props, literal types, and required/
  optional/many slots match component contracts statically where sound and always at runtime.
- [x] Conflicting asset/header/identity metadata fails atomically with source/component context.
- [x] Direct Python rendering and HDJ invocation have equivalent observable component output and
  metadata for core built-ins. Data/chart provider parity is **phase 0.12**.

## Hedron feature parity

- [x] **Phase 0.11:** Route/addressable reversal returns purpose-aware `SafeUrl` and never exposes a
  route merely by referencing it from a template (native FastAPI/Flask/Django facades).
- [x] **Phase 0.11:** PAGE/FRAGMENT selection, history restoration, layouts, fragment regions, and
  response adapters work identically across FastAPI, Flask, and Django.
- [x] **Phase 0.11:** Form models, typed validation errors, CSRF controls, unsafe actions, file
  uploads, and HTMX/non-HTMX error parity have representative fixtures.
- [x] **Phase 0.11:** Static page and conditional fragment assets, scoped-style symbols, theme
  variables, browser modules, and Web Components merge into the normal fingerprinted asset and CSP
  pipeline.
- [x] Icons, content helpers, cache/job status, and utility components retain their contracts when
  invoked from HDJ. Data-table/editor/chart provider parity is **phase 0.12**.
- [x] **Phase 0.11:** Explorer displays template/Jinja/Hedron/HTMX graphs and redacted
  trace/policy information.

## CSS and JavaScript

- [x] Literal inline CSS/JS, ordinary links/scripts, registered local assets, permitted remote
  assets, ES modules, and custom elements are covered without weakening dynamic-value safety.
- [x] `TemplateSpec.assets`, prologue page assets, and conditional fragment `{% hedron_asset %}`
  declarations deduplicate in first-use order and fail on unknown/conflicting IDs.
- [x] Format v1 rejects conditional page assets. Registered fragment head management and two-phase
  head/stream behavior are **phase 0.10**.
- [ ] **Phase 0.10:** browser modules initialize idempotently on HTMX load/swap, clean up before
  removal, and strip transient third-party DOM mutations before history snapshots when required.
- [x] Dynamic JSON uses a correct `tojson` context; dynamic CSS/script/event/srcdoc/tag/attribute
  sources require explicit advanced trust or fail with remediation.

## HTMX attribute surface

- [x] All pinned HTMX 2 request verbs and URL-bearing attributes accept static allowed URLs and
  purpose-compatible dynamic `SafeUrl` values.
- [x] Locally provable trigger/filter/eval capabilities have parser diagnostics. Browser race,
  cancellation, and behavioral fixtures are **phase 0.10**.
- [ ] **Phase 0.10:** targets, swaps/OOB, focus, View Transitions, stable IDs, boost/history,
  cache-hit/miss, copied-URL, and no-JavaScript behavior pass browser tests.
- [ ] **Phase 0.10:** include/params/vals/headers/encoding/request/confirm/prompt/indicator/disabled/
  validation and inheritance/disinheritance have representative semantic diagnostic coverage.
- [ ] **Phase 0.10:** unknown future `hx-*` attributes are reported against the installed HTMX
  version but are not stripped or blocked as HDJ grammar errors.

## HTMX response and extension surface

- [x] **Phase 0.11:** portable request facts include target, trigger/name, current URL, prompt, boost, and history
  restore without exposing a raw framework request.
- [x] **Phase 0.11:** `InteractionResult` accepts HDJ render output without re-rendering or metadata loss and covers
  retarget/reselect/reswap, navigation, refresh, triggers, status, cache, OOB, and regions.
- [x] **Phase 0.11:** approved response headers and direct template OOB markup share the same authorization and
  selector/URL validation path.
- [x] **Phase 0.11:** managed HTMX configuration reconciles eval/script processing/history/CSP
  defaults with the format-v1 capability report.
- [ ] **Phase 0.14:** core and community extensions require registered version/digest/CSP/load-order metadata;
  writing `hx-ext` alone never installs an extension.
- [x] SSE/WebSocket syntax composes without HDJ changes when phase 0.10 transport contracts ship.

## Security and capability reporting

- [x] Autoescape, `StrictUndefined`, `Secret`, `TrustedHtml`, `SafeUrl`, `tojson`, context checks,
  malicious Markup producers, and exception redaction pass adversarial tests.
- [x] Format-v1 capability reports cover inline script/style, obvious HTMX eval, response script
  tags, purpose-specific literal/registered remote origins, and fragment head work. Integrity,
  extension, dynamic-dependency, and broader raw-context evidence belongs to **0.11/0.14**.
- [x] **Phase 0.11:** SecurityPolicy/CSP mismatches fail with a precise source span and never inject nonces,
  `unsafe-inline`, `unsafe-eval`, remote origins, or permissive HTMX settings silently.
- [x] **Phase 0.11:** CSRF, authorization, fragment-region, approved-header, cache, and route-exposure policies
  remain authoritative under strict and unchecked template modes.
- [x] Documentation states that templates are trusted application code and sandboxing is not a
  hostile-author product boundary.

## Limits, tooling, and operations

- [x] Static dependency depth, components, chunk-consumed output, metadata, and shared Hedron
  node/depth limits fail atomically. Exact loop/macro accounting is **phase 0.14** and async
  operation budgets are **phase 0.13**.
- [x] **Phase 0.11:** `hedron check`, `dev`, and `build` implement dependency/capability checking, incremental
  invalidation, and portable production inventory.
- [x] **Phase 0.11:** production rejects missing/stale/shadowed/incompatible templates, bindings, assets,
  extensions, policies, and dynamic dependency bounds.
- [x] Format-v1 diagnostics contain stable codes, explanations, remediations, and available source
  spans. Rich include/macro/attribute paths and portable formats are **phase 0.14**; Explorer wiring
  is **phase 0.11**.
- [x] Warm render, component call, async work, cold start, memory, dependency graph, installed size,
  and resource-limit budgets have retained evidence (resource-limit fixtures in `tests/jinja`).

## Accessibility and usability

- [ ] **Phase 0.14:** static checks cover the sound HTML/form/landmark/ID/ARIA/focus subset without claiming proof.
- [ ] **Phase 0.10:** page, accessible form/error, repeated data/status, history/OOB, custom CSS, and browser-module
  examples pass keyboard, focus, announcements, contrast, zoom/reflow, reduced motion, and
  no-JavaScript evidence.
- [x] Progressive examples teach plain HTML first, then Jinja, components, HTMX, and browser modules.
- [x] Python-first and HTML-oriented authors complete representative tasks; findings improve names,
  diagnostics, examples, and defaults without weakening trust boundaries.

## HDN removal

- [x] HDN runtime, discovery, artifacts, registry/manifest fields, public APIs, CLI/Explorer paths,
  examples, and tests are removed.
- [x] No compatibility mode, converter, or legacy package ships; 0.8 is the final capable line.

## Release evidence

- [x] Every required row is Verified or explicitly Deferred with owner, destination phase, and
  stability impact.
- [x] No critical/high security findings remain open.
- [x] Clean wheels, supported Python/Jinja/MarkupSafe/HTMX matrices, offline startup, upgrade,
  rollback, SBOM/license/provenance, and reference applications pass from built artifacts
  (`scripts/verify_pkg_09.py`; public-index verify remains a post-publish cut step).
