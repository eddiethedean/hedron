# Jinja integration acceptance

> **Target:** phase 0.11 experimental implementation; beta promotion no earlier than phase 0.12.

## Packaging and boundaries

- [ ] `hedron-jinja` installs and imports independently on every supported Python version.
- [ ] `hedron-core` and default `hedron` wheels contain no required Jinja/MarkupSafe dependency or
  eager import.
- [ ] `hedron[jinja]` installs the version-matched integration package.
- [ ] Package metadata, license, typing marker, changelog, compatibility matrix, wheel/sdist install,
  and offline startup evidence pass.

## Public behavior

- [ ] `HedronJinja`, `HedronJinjaExtension`, `TemplateSpec`, and `TemplateSource` match RFC-0031 and
  `api/JINJA.md`.
- [ ] Registration is explicit, application-local, duplicate-safe, and immutable after freeze.
- [ ] Canonical template names and application/package loader namespaces reject traversal,
  ambiguity, silent shadowing, and undeclared sources.
- [ ] Sync and async rendering return the normal immutable `RenderResult`; async Jinja execution
  does not make component rendering async.
- [ ] Hedron tags fail outside the owning render session rather than returning metadata-lossy HTML.

## Grammar and component contracts

- [ ] Inline, body, named-slot, nested-component, Jinja inheritance/include/macro/condition/loop,
  whitespace-control, and source-span fixtures pass.
- [ ] Component and slot names are static; props are named; spread props and template Python imports
  are rejected.
- [ ] Required/defaulted/unknown/deprecated/secret/identity props and required/optional/many slots
  match component contracts at check and runtime boundaries.
- [ ] Typed `view.field` paths and literal types are checked statically where sound; every evaluated
  invocation still passes runtime props validation.
- [ ] Callable component factories require explicit inspectable schemas and receive no implicit
  Jinja environment, context, session, loader, request, or registry.

## Metadata and conformance

- [ ] Nested HTML, assets, approved headers, identity maps, diagnostics, and redacted traces merge
  deterministically and preserve first-use/source order where specified.
- [ ] Conflicting assets, headers, and identities fail closed with `HED-JINJA-0013`.
- [ ] Direct Python rendering and Jinja invocation have equivalent observable component output and
  metadata for shared fixtures.
- [ ] FastAPI, Flask, and Django Jinja paths pass the same page, fragment, error, headers, assets,
  HTMX, identity, and diagnostic conformance matrix.
- [ ] Concurrent sync/async requests prove render-session, view, metadata, and trace isolation.

## Security and limits

- [ ] Strict mode enforces HTML autoescape and `StrictUndefined` and rejects `safe`.
- [ ] `hedron_trusted` accepts only `TrustedHtml`; `hedron_url` accepts only purpose-compatible
  `SafeUrl`.
- [ ] Dynamic URL, style, script, event, srcdoc, tag, and attribute contexts follow RFC-0031.
- [ ] Secret conversion, lazy/unbounded iterators, loader traversal, dynamic dependencies, unsafe
  Markup producers, malicious factories, stale manifests, and exception leakage pass adversarial
  tests.
- [ ] Include depth, macro recursion, loop work, component calls, output, metadata, and shared Hedron
  render limits fail atomically with redacted diagnostics.
- [ ] Documentation and generated projects state that templates are trusted application code and
  that Jinja sandboxing does not permit hostile template authors.

## Build, tooling, and operations

- [ ] `hedron check` reports the RFC-0031 diagnostic family with exact source/include/component
  context in text, JSON, and SARIF.
- [ ] `hedron dev` invalidates only affected static dependency graphs and rebuilds atomically.
- [ ] `hedron build` records template/component/view/policy digests and dependency versions without
  source text, secrets, live objects, or absolute roots.
- [ ] Production rejects missing, stale, incompatible, dynamically unresolved, or undeclared
  template dependencies.
- [ ] Explorer source/dependency/contract/security/trace views use the normal source allowlist and
  redact sensitive values.

## Accessibility and performance

- [ ] Static checks cover the sound accessibility subset without claiming complete proof.
- [ ] Representative page, form/error, and repeated-status fixtures pass keyboard, focus,
  screen-reader semantics, announcements, contrast, zoom/reflow, reduced-motion, and non-JavaScript
  evidence.
- [ ] A template without Hedron tags stays within the greater of 10% or 100 microseconds of its
  bound-Jinja warm-render baseline.
- [ ] Component-tag, cold-start, memory, dependency-check, incremental rebuild, installed-size, and
  resource-limit budgets are retained in the phase evidence ledger.

## HDN migration

- [ ] Every HDN API, artifact, CLI/Explorer path, example, guide, and discovery use is inventoried
  and receives the phase 0.11 deprecation diagnostic.
- [ ] `hedron migrate hdn --to jinja` defaults to dry-run, emits source/destination digests and a
  machine-readable report, requires explicit writes, and retains the source.
- [ ] Static/representable fixtures convert; ambiguous expressions, access, imports, trusted
  content, HTML, and component contracts stop with `HED-JINJA-0018` and no silent semantic change.
- [ ] Phase 0.12 disables default HDN discovery behind a declared compatibility option; phase 0.13
  removal tests and documentation identify the final compatible release.

## Evidence and promotion

- [ ] Three representative applications publish Python-only and Jinja variants.
- [ ] Python-first and HTML-oriented author studies record task time, errors, readability, typing,
  diagnostics, diff quality, and preference.
- [ ] No critical/high security findings remain open and every required check has immutable evidence
  under `acceptance/EVIDENCE.md`.
- [ ] Beta promotion occurs no earlier than phase 0.12 after real-application evidence.
