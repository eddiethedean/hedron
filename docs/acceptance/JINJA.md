# HDJ authoring acceptance

> **Target:** phase 0.9. `.hdj` is the optional, explicit, standards-first Jinja/HTML/HTMX format.

## Deferred ownership

Rows marked with a later phase are excluded from the 0.9 exit gate and owned here:

| Later phase | Owned HDJ work |
|---:|---|
| 0.10 | Registered fragment head management, two-phase template streaming, version-aware HTMX semantics, and browser-backed navigation/history/OOB/lifecycle evidence. |
| 0.11 | Finite fingerprinted dynamic dependency manifests, foreign Jinja/package namespaces, native route/CSRF/context/response facades, and CLI/build/Explorer production inventory. |
| 0.12 | `hedron.data`/`hedron.charts` provider parity and bounded high-volume presentation evidence. |
| 0.13 | Async filter/global I/O contracts, operation budgets, deadlines, cancellation, and tracing. |
| 0.14 | Optional exact loop/macro instrumentation, contracted custom-extension/helper evidence, broader contextual analysis, and portable checker fixtures. |

## Packaging and identity

- [x] `hedron-jinja` is a separate distribution importing as `hedron_jinja`.
- [x] `hedron-core` and default `hedron` have no required Jinja/MarkupSafe dependency or eager import.
- [x] `hedron[jinja]` installs the version-matched integration package.
- [ ] Documentation consistently uses `.hdj` as the versioned Hedron Jinja format while making
  clear that the template body follows normal Jinja semantics.
- [ ] Metadata, typing marker, changelog, compatibility matrix, wheel/sdist clean install, and
  offline startup evidence pass.

## Source format and feature declarations

- [ ] Only UTF-8 `.hdj` sources with a byte-zero `---hdj` TOML prologue enter the HDJ loader;
  missing/duplicate/unterminated prologues and unsupported versions fail with source diagnostics.
- [ ] `version`, `kind`, and `profile` are required static values; unknown keys, wrong types,
  duplicate TOML keys, expressions, and executable values fail before Jinja compilation.
- [ ] `page`, `fragment`, and `library` kinds enforce document shape and valid entry-point use;
  `TemplateSpec.mode` may assert but never override source kind.
- [ ] Format-v1 `minimal`, `standard`, `full`, and `custom` profiles expand to documented exact
  feature sets independent of registry ordering.
- [ ] Namespaced `features` reject unknown, unavailable, incompatible, and used-but-undeclared
  surfaces; unused declarations produce useful diagnostics rather than changing output.
- [ ] Inferred browser/HTMX capabilities must be covered by `requires`; under-declaration fails,
  over-declaration warns, and neither form grants policy permission.
- [ ] Prologue `assets` and `regions` merge deterministically with application contracts and appear
  in build/Explorer inventory; format v1 rejects dynamic dependencies.
- [ ] Public immutable `TemplateDeclaration`/`describe()` exposes format version, kind, profile,
  declared/effective features, requirements, assets, regions, and dependency bounds without render.
- [ ] Source body line numbers survive prologue removal in Jinja exceptions, diagnostics, traces,
  SARIF, and Explorer.
- [ ] Ordinary `.html`/`.jinja` sources stay outside the HDJ loader. **Phase 0.11:** add the finite,
  fingerprinted foreign boundary; foreign source cannot invoke Hedron tags.

## Standards-first freedom

- [ ] Literal trusted source accepts standard HTML, custom elements, `data-*`, `aria-*`, CSS,
  JavaScript, and pinned HTMX attributes without requiring component wrappers.
- [ ] Strict mode governs dynamic data/context and static contracts; it does not act as a reduced
  HTML grammar or silently override deployment policy.
- [ ] A minimal `.hdj` file needs only three concise prologue fields before ordinary HTML/Jinja and
  renders without component wrappers or semantic changes.
- [ ] `strict=False` provides conventional trusted-Jinja freedom while
  preserving secrets, loader isolation, authorization, and response-header boundaries.

## Jinja conformance

- [ ] Inheritance, blocks, `super`, includes, imports, macros, `call`, filters, tests, `set`,
  namespaces, conditions, loops/recursive loops, whitespace control, and comments have fixtures.
- [ ] Explicit i18n, `do`, loop-control, filter/test/global availability works when configured before
  binding; arbitrary custom-extension evidence is **phase 0.14**.
- [ ] Core async rendering requires explicit `jinja.async`. I/O declarations, operation tracing,
  cancellation, and deadline policy are **phase 0.13**.
- [ ] Static referenced-template analysis uses Jinja's meta API and dynamic dependencies fail.
  Exact finite candidate manifests are **phase 0.11**; namespace-only bounds are never accepted.
- [ ] HDJ extension state survives Jinja environment overlays without leaking bindings or sessions;
  no environment-specific state is stored unsafely on a reusable extension instance.
- [ ] Unsupported `NativeEnvironment` and direct streaming paths fail with precise alternatives.

## Public context and contracts

- [x] Implemented `HedronJinja`, `HedronJinjaExtension`, `TemplateSpec`, and `TemplateSource` expose
  the core render path.
- [ ] `TemplateSpec` binds runtime view type, source namespace, strict policy, and stable identity while
  source kind/features/assets/region IDs come from the `.hdj` prologue without contradictory truth.
- [ ] Immutable `HdjContext` exposes mode, fragment status, locale/theme, immutable optional HTMX
  facts, reverse URLs, asset URLs, and CSRF markup without raw request/session/container/registry
  access. Native adapter facts are **phase 0.11**; scoped-style/validated-attribute helpers are
  **phase 0.14**.
- [ ] Registration is explicit, local, duplicate-safe, immutable after freeze, and rejects
  factories without inspectable contracts.
- [ ] Canonical application names reject traversal and ambiguity. Installed-package namespace,
  shadowing, and override policy are **phase 0.11**.

## Components and metadata

- [x] Inline components, explicit `with body`, named slots, trusted markup, direct-render failure,
  page/fragment shape, and initial component/output budgets have focused tests.
- [ ] Nested components inside inheritance/includes/macros/loops/slots preserve source order and
  complete HTML/assets/headers/identity/diagnostic/trace metadata.
- [ ] Required/defaulted/unknown/deprecated/secret/identity props, literal types, and required/
  optional/many slots match component contracts statically where sound and always at runtime.
- [ ] Conflicting asset/header/identity metadata fails atomically with source/component context.
- [ ] Direct Python rendering and HDJ invocation have equivalent observable component output and
  metadata for core built-ins. Data/chart provider parity is **phase 0.12**.

## Hedron feature parity

- [ ] Route/addressable reversal returns purpose-aware `SafeUrl` and never exposes a route merely by
  referencing it from a template.
- [ ] PAGE/FRAGMENT selection, history restoration, layouts, fragment regions, and response adapters
  work identically across FastAPI, Flask, and Django.
- [ ] Form models, typed validation errors, CSRF controls, unsafe actions, file uploads, and
  HTMX/non-HTMX error parity have representative fixtures.
- [ ] Static page and conditional fragment assets, scoped-style symbols, theme variables, browser modules, and Web
  Components merge into the normal fingerprinted asset and CSP pipeline.
- [ ] Icons, content helpers, cache/job status, and utility components retain their contracts.
  Data-table/editor/chart provider parity is **phase 0.12**.
- [ ] Explorer displays template/Jinja/Hedron/HTMX graphs and redacted trace/policy information.

## CSS and JavaScript

- [ ] Literal inline CSS/JS, ordinary links/scripts, registered local assets, permitted remote
  assets, ES modules, and custom elements are covered without weakening dynamic-value safety.
- [ ] `TemplateSpec.assets`, prologue page assets, and conditional fragment `{% hedron_asset %}`
  declarations deduplicate in first-use order and fail on unknown/conflicting IDs.
- [ ] Format v1 rejects conditional page assets. Registered fragment head management and two-phase
  head/stream behavior are **phase 0.10**.
- [ ] **Phase 0.10:** browser modules initialize idempotently on HTMX load/swap, clean up before
  removal, and strip transient third-party DOM mutations before history snapshots when required.
- [ ] Dynamic JSON uses a correct `tojson` context; dynamic CSS/script/event/srcdoc/tag/attribute
  sources require explicit advanced trust or fail with remediation.

## HTMX attribute surface

- [ ] All pinned HTMX 2 request verbs and URL-bearing attributes accept static allowed URLs and
  purpose-compatible dynamic `SafeUrl` values.
- [ ] Locally provable trigger/filter/eval capabilities have parser diagnostics. Browser race,
  cancellation, and behavioral fixtures are **phase 0.10**.
- [ ] **Phase 0.10:** targets, swaps/OOB, focus, View Transitions, stable IDs, boost/history,
  cache-hit/miss, copied-URL, and no-JavaScript behavior pass browser tests.
- [ ] **Phase 0.10:** include/params/vals/headers/encoding/request/confirm/prompt/indicator/disabled/
  validation and inheritance/disinheritance have representative semantic diagnostic coverage.
- [ ] **Phase 0.10:** unknown future `hx-*` attributes are reported against the installed HTMX
  version but are not stripped or blocked as HDJ grammar errors.

## HTMX response and extension surface

- [ ] **Phase 0.11:** portable request facts include target, trigger/name, current URL, prompt, boost, and history
  restore without exposing a raw framework request.
- [ ] **Phase 0.11:** `InteractionResult` accepts HDJ render output without re-rendering or metadata loss and covers
  retarget/reselect/reswap, navigation, refresh, triggers, status, cache, OOB, and regions.
- [ ] **Phase 0.11:** approved response headers and direct template OOB markup share the same authorization and
  selector/URL validation path.
- [ ] **Phase 0.11:** managed HTMX configuration reconciles eval/script processing/history/CSP
  defaults with the format-v1 capability report.
- [ ] **Phase 0.14:** core and community extensions require registered version/digest/CSP/load-order metadata;
  writing `hx-ext` alone never installs an extension.
- [ ] SSE/WebSocket syntax composes without HDJ changes when phase 0.10 transport contracts ship.

## Security and capability reporting

- [ ] Autoescape, `StrictUndefined`, `Secret`, `TrustedHtml`, `SafeUrl`, `tojson`, context checks,
  malicious Markup producers, and exception redaction pass adversarial tests.
- [ ] Format-v1 capability reports cover inline script/style, obvious HTMX eval, response script
  tags, purpose-specific literal/registered remote origins, and fragment head work. Integrity,
  extension, dynamic-dependency, and broader raw-context evidence belongs to **0.11/0.14**.
- [ ] **Phase 0.11:** SecurityPolicy/CSP mismatches fail with a precise source span and never inject nonces,
  `unsafe-inline`, `unsafe-eval`, remote origins, or permissive HTMX settings silently.
- [ ] **Phase 0.11:** CSRF, authorization, fragment-region, approved-header, cache, and route-exposure policies
  remain authoritative under strict and unchecked template modes.
- [ ] Documentation states that templates are trusted application code and sandboxing is not a
  hostile-author product boundary.

## Limits, tooling, and operations

- [ ] Static dependency depth, components, chunk-consumed output, metadata, and shared Hedron
  node/depth limits fail atomically. Exact loop/macro accounting is **phase 0.14** and async
  operation budgets are **phase 0.13**.
- [ ] **Phase 0.11:** `hedron check`, `dev`, and `build` implement dependency/capability checking, incremental
  invalidation, and portable production inventory.
- [ ] **Phase 0.11:** production rejects missing/stale/shadowed/incompatible templates, bindings, assets,
  extensions, policies, and dynamic dependency bounds.
- [ ] Format-v1 diagnostics contain stable codes, explanations, remediations, and available source
  spans. Rich include/macro/attribute paths and portable formats are **phase 0.14**; Explorer wiring
  is **phase 0.11**.
- [ ] Warm render, component call, async work, cold start, memory, dependency graph, installed size,
  and resource-limit budgets have retained evidence.

## Accessibility and usability

- [ ] **Phase 0.14:** static checks cover the sound HTML/form/landmark/ID/ARIA/focus subset without claiming proof.
- [ ] **Phase 0.10:** page, accessible form/error, repeated data/status, history/OOB, custom CSS, and browser-module
  examples pass keyboard, focus, announcements, contrast, zoom/reflow, reduced motion, and
  no-JavaScript evidence.
- [ ] Progressive examples teach plain HTML first, then Jinja, components, HTMX, and browser modules.
- [ ] Python-first and HTML-oriented authors complete representative tasks; findings improve names,
  diagnostics, examples, and defaults without weakening trust boundaries.

## HDN removal

- [x] HDN runtime, discovery, artifacts, registry/manifest fields, public APIs, CLI/Explorer paths,
  examples, and tests are removed.
- [x] No compatibility mode, converter, or legacy package ships; 0.8 is the final capable line.

## Release evidence

- [ ] Every required row is Verified or explicitly Deferred with owner, destination phase, and
  stability impact.
- [ ] No critical/high security findings remain open.
- [ ] Clean wheels, supported Python/Jinja/MarkupSafe/HTMX matrices, offline startup, upgrade,
  rollback, SBOM/license/provenance, and reference applications pass from built artifacts.
