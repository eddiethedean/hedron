# Changelog

## [0.9.0] - 2026-08-04

### Removed

- The experimental HDN parser, evaluator, formatter, render program, discovery metadata, and
  public APIs.

### Changed

- Build manifests use format 2 and no longer contain HDN program entries.

## [0.8.0] - 2026-08-03

### Added

- Public stability catalog, deprecation/semver policy, upgrade guide, and threat model.
- Performance budgets with enforcement tests; three-engine browser HTMX matrix scaffolding.
- SBOM, license inventory, browser-asset audit, and release evidence bundle scripts.
- Flask/Django hardening suites and Django Supported floor `>=5.2,<6`.

### Changed

- Feature freeze: no new subsystems, adapters, or transports on the 0.8 train.
- Use the canonical `template.hdn` filename during component discovery.

## [0.7.0] — 2026-08-03

- Phase 0.7 portable adapters, operations, and jobs train.


All notable changes to `hedron-core` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with the Hedron coordinated release train (`0.N.0` for phase `0.N`).

## [0.6.0] - 2026-08-03

Visualization contracts, trusted content boundaries, and Auto chart hooks for phase 0.6.

### Added

- `VisualizationAdapter`, `ChartOutput`, `ChartAccessibility`, and `VisualizationLimits`.
- Trusted icon/SVG registry (`register_icon`, `get_icon`, `trusted_svg`).
- `TrustedHtml.nh3(...)` sanitizer constructor (optional `nh3`).
- Auto chart-stub remediation points at `hedron-charts` (no longer “phase 0.6”).

### Security

- Icon SVG registration rejects script URLs and common event-handler / `foreignObject` patterns.

### Changed

- Default plugin `hedron_version` gate is `>=0.6,<0.7`.

## [0.5.0] - 2026-08-03

Data application foundations in core: `Auto()` renderer registry, cache protocols,
utility components, and ColorMode.

### Added

- `Auto`, renderer registry, and bounded Data Intelligence inspection.
- Cache protocols, in-memory backend, key builder, single-flight, and Explorer traces.
- Utility built-ins: Metric, CodeViewer, JSONViewer, Progress, Status, Toast,
  Expander, Tabs, Sidebar.
- `ColorMode`, `ColorModeToggle`, `color_mode_script`, and `resolve_color_mode`.
- `Page(data_theme=...)` for explicit `data-theme` on `<html>`.

### Fixed

- Theme CSS: system dark uses `:root:not([data-theme="light"])`; explicit light preference
  overrides system dark.
- Cache single-flight keeps results until waiters finish (no waiter `KeyError` race).
- `Sidebar` uses `aria={"label": ...}` (render no longer crashes).
- `ColorModeToggle` emits a hidden `csrf_token` when provided.
- Native attributes match HTMX 2: `hx-disinherit`, `hx-inherit`, and `hx-validate` are accepted;
  removed `hx-sse` / `hx-ws` and non-core `hx-href` are rejected.

## [0.4.0] - 2026-08-03

Developer platform: JSON/SARIF diagnostics, suppressions, source spans, and plugin
metadata contracts in core.

### Added

- `Diagnostic.as_json`, `diagnostics_to_sarif`, `Suppression`, `SourceSpan`,
  `apply_suppressions`, `meets_severity_threshold`.
- Framework-neutral plugin metadata and Explorer panel registration helpers.

### Fixed / hardened

- Suppression scopes use exact or PurePath prefix matching (suffixes like `.css` no longer match).
- SARIF `tool.driver.version` comes from package `__version__`.
- Registry builder snapshot/restore helpers for plugin rollback.

## [0.3.0] - 2026-08-03

Authoring, scoped styles, themes, and assets for the phase 0.3 release train.

### Added

- HDN lexer/parser/expression engine, typed render programs, formatter, and
  source maps (`compile_hdn`, `format_hdn`, `run_program`).
- Scoped CSS AST compiler with stable symbols, `:global(...)`, keyframes,
  cascade layers, and typed `styles` bindings.
- `Theme` API with required accessibility tokens, light/dark modes, and token
  CSS emission into the `tokens` cascade layer.
- Fingerprinted asset pipeline and versioned build/CSS/asset manifests.
- Component-folder discovery for colocated HDN, CSS, and browser modules.
- Web Component registration metadata and custom-element HTML support.

### Fixed / hardened

- Compile-time rejection of arbitrary HDN calls; `{#for}` / expression failures
  raise `HedronError`; `??` rewrite respects parentheses/calls/indexes and strings,
  and chains (`a ?? b ?? c`) rewrite recursively without treating call commas as
  operands.
- CSS URL policy resolves registered roots, rejects empty-root relative URLs,
  absolute/`file:` paths, missing files (`HED-ASSET-0004`), symlinks, and remote URLs
  when disallowed; ERROR diagnostics fail `compile_css`; declarations without trailing
  `;` are preserved.
- Discovery uses `cls.distribution` when present; browser-only folders register a
  component stub; duplicate browser-module registration warns.
- Unknown configured themes fail build with `HED-THEME-0001`.
- `write_json_atomic` uses a unique same-directory temp file + `os.replace`.
- `RenderProgram.from_dict` / `load_hdn_program` validate format (`HED-HDN-0008`);
  digests include style-symbol maps.
- Production compile gate on `compile_hdn`/`compile_css` (`HED-BUILD-0004`) with
  force-allow for `hedron build`.

[0.4.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.4.0
[0.3.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.3.0

## [0.2.0] - 2026-08-03

Framework-neutral support for the FastAPI MVP release train.

### Added

- `@addressable` and immutable `AddressableDescriptor` for reusable resource
  factories that remain unreachable until explicitly exposed.
- Registry kinds for addressable factories and adapter-populated `RouteMeta`
  entries shared by routing, OpenAPI, CLI, and Explorer.
- Public exports: `addressable`, `AddressableDescriptor`, `AddressableMeta`,
  `RouteMeta`, `register_addressable`, and `register_route`.

### Fixed / hardened

- Render cycle detection uses component instance identity so nested same-type
  composition is valid; `__hedron_node__` / `ComponentNode` are honored by `render`.
- URL attrs `srcset`, `ping`, `hx-push-url`, and `hx-replace-url` require SafeUrl
  policy (with validated `srcset` candidates).
- `FormField` binds controls without mutating shared props; Checkbox aria lands on
  the input; `Secret[T]` validates the inner type `T`.

## [0.1.0] - 2026-08-03

Initial public release of the framework-neutral typed rendering core.

### Added

- `Model`, `Props`, `FormModel`, `EventPayload`, and `Field` with construction-time
  validation and supported-annotation guardrails.
- Trust boundary types: `Secret`, `TrustedHtml`, `SafeUrl`, and `UrlPurpose`.
- Component protocol, children/slots/fragments, deterministic identity, and sealable
  registry.
- Private context-aware HTML serializer with XSS-hardening defaults (blocked active
  tags/attrs, SafeUrl purpose checks, unknown-attribute rejection).
- `render(...) -> RenderResult` with PAGE and FRAGMENT modes and frozen result maps.
- Phase 0.1 built-ins for document, content, forms, layout, landmarks, surfaces,
  and controls, including FormField accessibility contracts.
- Typed package marker (`py.typed`) and offline reference-app static rendering proof.

### Security

- Contextual escaping for text and attributes.
- Secret redaction in diagnostics and identity records.
- Adversarial escaping corpus covering XSS smuggling paths exercised in CI.

[0.2.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.2.0
[0.1.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.1.0

[0.5.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.5.0

[0.6.0]: https://github.com/eddiethedean/hedron/releases/tag/v0.6.0
