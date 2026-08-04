# HDJ authoring acceptance

> **Target:** phase 0.9. `.hdj` is the optional, explicit, standards-first Jinja/HTML/HTMX format.

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
- [ ] Prologue `assets`, `regions`, and bounded `dynamic_dependencies` merge deterministically with
  application contracts and appear in build/Explorer inventory.
- [ ] Public immutable `TemplateDeclaration`/`describe()` exposes format version, kind, profile,
  declared/effective features, requirements, assets, regions, and dependency bounds without render.
- [ ] Source body line numbers survive prologue removal in Jinja exceptions, diagnostics, traces,
  SARIF, and Explorer.
- [ ] Ordinary `.html`/`.jinja` sources stay outside the HDJ loader unless `jinja.foreign` and a
  namespaced foreign loader are explicitly configured; foreign source cannot invoke Hedron tags.

## Standards-first freedom

- [ ] Literal trusted source accepts standard HTML, custom elements, `data-*`, `aria-*`, CSS,
  JavaScript, and pinned HTMX attributes without requiring component wrappers.
- [ ] Strict mode governs dynamic data/context and static contracts; it does not act as a reduced
  HTML grammar or silently override deployment policy.
- [ ] A minimal `.hdj` file needs only three concise prologue fields before ordinary HTML/Jinja and
  renders without component wrappers or semantic changes.
- [ ] `strict=False` and named check exceptions provide conventional trusted-Jinja freedom while
  preserving secrets, loader isolation, authorization, and response-header boundaries.

## Jinja conformance

- [ ] Inheritance, blocks, `super`, includes, imports, macros, `call`, filters, tests, `set`,
  namespaces, conditions, loops/recursive loops, whitespace control, and comments have fixtures.
- [ ] i18n, `do`, loop-control, application extension, custom filter/test/global, bytecode-cache,
  and precompile paths work when configured before binding.
- [ ] Async filters/globals/includes/iterables work only through `render_async`, are declared and
  traced, and obey cancellation/deadline policy.
- [ ] Static referenced-template and undeclared-variable analysis uses Jinja's meta API; dynamic
  dependencies require explicitly declared bounded loader namespaces.
- [ ] HDJ extension state survives Jinja environment overlays without leaking bindings or sessions;
  no environment-specific state is stored unsafely on a reusable extension instance.
- [ ] Unsupported `NativeEnvironment` and direct streaming paths fail with precise alternatives.

## Public context and contracts

- [x] Implemented `HedronJinja`, `HedronJinjaExtension`, `TemplateSpec`, and `TemplateSource` expose
  the core render path.
- [ ] `TemplateSpec` binds view type, source namespace, strict policy, and stable identity while
  source kind/features/assets/region IDs come from the `.hdj` prologue without contradictory truth.
- [ ] Immutable `HdjContext` exposes mode, fragment status, locale/theme, portable HTMX facts,
  reverse URLs, asset URLs, scoped styles, validated attributes, and CSRF markup without raw
  request/session/container/registry access.
- [ ] Registration is explicit, local, duplicate-safe, immutable after freeze, and rejects
  factories without inspectable contracts.
- [ ] Canonical application/package loader namespaces reject traversal, shadowing, ambiguity, and
  undeclared sources.

## Components and metadata

- [x] Inline components, explicit `with body`, named slots, trusted markup, direct-render failure,
  page/fragment shape, and initial component/output budgets have focused tests.
- [ ] Nested components inside inheritance/includes/macros/loops/slots preserve source order and
  complete HTML/assets/headers/identity/diagnostic/trace metadata.
- [ ] Required/defaulted/unknown/deprecated/secret/identity props, literal types, and required/
  optional/many slots match component contracts statically where sound and always at runtime.
- [ ] Conflicting asset/header/identity metadata fails atomically with source/component context.
- [ ] Direct Python rendering and HDJ invocation have equivalent observable component output and
  metadata for built-ins, data, charts, forms, icons, and third-party components.

## Hedron feature parity

- [ ] Route/addressable reversal returns purpose-aware `SafeUrl` and never exposes a route merely by
  referencing it from a template.
- [ ] PAGE/FRAGMENT selection, history restoration, layouts, fragment regions, and response adapters
  work identically across FastAPI, Flask, and Django.
- [ ] Form models, typed validation errors, CSRF controls, unsafe actions, file uploads, and
  HTMX/non-HTMX error parity have representative fixtures.
- [ ] Template/component assets, scoped-style symbols, theme variables, browser modules, and Web
  Components merge into the normal fingerprinted asset and CSP pipeline.
- [ ] Icons, content helpers, data tables/editors, charts, cache/job status, and utility components
  retain their normal props, accessibility, asset, trace, and optional-dependency behavior.
- [ ] Explorer displays template/Jinja/Hedron/HTMX graphs and redacted trace/policy information.

## CSS and JavaScript

- [ ] Literal inline CSS/JS, ordinary links/scripts, registered local assets, permitted remote
  assets, ES modules, and custom elements are covered without weakening dynamic-value safety.
- [ ] `TemplateSpec.assets` and conditional `{% hedron_asset %}` declarations deduplicate in
  first-use order, fingerprint correctly, and fail on unknown/conflicting IDs.
- [ ] Fragment asset policy proves preloaded assets, registered head management, and unsupported
  late requirements fail predictably.
- [ ] Browser modules initialize idempotently on HTMX load/swap, clean up before removal, and strip
  transient third-party DOM mutations before history snapshots when required.
- [ ] Dynamic JSON uses a correct `tojson` context; dynamic CSS/script/event/srcdoc/tag/attribute
  sources require explicit advanced trust or fail with remediation.

## HTMX attribute surface

- [ ] All pinned HTMX 2 request verbs and URL-bearing attributes accept static allowed URLs and
  purpose-compatible dynamic `SafeUrl` values.
- [ ] Trigger events, polling, delay/throttle/queue/filter modifiers, and `hx-sync` strategies have
  parser, race, cancellation, and bounded-work fixtures.
- [ ] Targets, swaps/modifiers, selection, OOB, preserve, focus, scroll, View Transitions, and
  stable-ID behavior pass browser tests.
- [ ] Boost/history/push/replace/history-elt/history-sensitive-region behavior passes navigation,
  cache-hit, cache-miss, copied-URL, and no-JavaScript tests.
- [ ] Include/params/vals/headers/encoding/request/confirm/prompt/indicator/disabled/validation and
  inheritance/disinheritance have representative forms and diagnostic coverage.
- [ ] Unknown future `hx-*` attributes are reported against the installed HTMX version but are not
  stripped or blocked as HDJ grammar errors.

## HTMX response and extension surface

- [ ] Portable request facts include target, trigger/name, current URL, prompt, boost, and history
  restore without exposing a raw framework request.
- [ ] `InteractionResult` accepts HDJ render output without re-rendering or metadata loss and covers
  retarget/reselect/reswap, navigation, refresh, triggers, status, cache, OOB, and regions.
- [ ] Approved response headers and direct template OOB markup share the same authorization and
  selector/URL validation path.
- [ ] Managed HTMX configuration keeps eval/script processing/history/CSP defaults; explicit eval,
  inline-event, response-script, and remote-extension capabilities are accurately reported.
- [ ] Core and community extensions require registered version/digest/CSP/load-order metadata;
  writing `hx-ext` alone never installs an extension.
- [ ] SSE/WebSocket syntax composes without HDJ changes when phase 0.10 transport contracts ship.

## Security and capability reporting

- [ ] Autoescape, `StrictUndefined`, `Secret`, `TrustedHtml`, `SafeUrl`, `tojson`, context checks,
  malicious Markup producers, and exception redaction pass adversarial tests.
- [ ] Capability reports cover inline script/style, HTMX eval/event filters, response script tags,
  remote origins/integrity, extensions, dynamic dependencies, raw contexts, and fragment head work.
- [ ] SecurityPolicy/CSP mismatches fail with a precise source span and never inject nonces,
  `unsafe-inline`, `unsafe-eval`, remote origins, or permissive HTMX settings silently.
- [ ] CSRF, authorization, fragment-region, approved-header, cache, and route-exposure policies
  remain authoritative under strict and unchecked template modes.
- [ ] Documentation states that templates are trusted application code and sandboxing is not a
  hostile-author product boundary.

## Limits, tooling, and operations

- [ ] Include depth, macro recursion, loop work, async work, components, output, metadata, and shared
  Hedron node/depth limits fail atomically with redacted diagnostics.
- [ ] `hedron check`, `dev`, and `build` implement dependency/capability/HTMX checking, incremental
  invalidation, and portable production inventory.
- [ ] Production rejects missing/stale/shadowed/incompatible templates, bindings, assets,
  extensions, policies, and dynamic dependency bounds.
- [ ] Diagnostics contain template span, include/macro stack, component/attribute path, capability,
  explanation, and remediation in text, JSON, SARIF, and Explorer.
- [ ] Warm render, component call, async work, cold start, memory, dependency graph, installed size,
  and resource-limit budgets have retained evidence.

## Accessibility and usability

- [ ] Static checks cover the sound HTML/form/landmark/ID/ARIA/focus subset without claiming proof.
- [ ] Page, accessible form/error, repeated data/status, history/OOB, custom CSS, and browser-module
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
