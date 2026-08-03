# Changelog

All notable changes to `hedron-core` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with the Hedron coordinated release train (`0.N.0` for phase `0.N`).

## [0.2.0] - 2026-08-03

Framework-neutral support for the FastAPI MVP release train.

### Added

- `@addressable` and immutable `AddressableDescriptor` for reusable resource
  factories that remain unreachable until explicitly exposed.
- Registry kinds for addressable factories and adapter-populated `RouteMeta`
  entries shared by routing, OpenAPI, CLI, and Explorer.
- Public exports: `addressable`, `AddressableDescriptor`, `AddressableMeta`,
  `RouteMeta`, `register_addressable`, and `register_route`.

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
