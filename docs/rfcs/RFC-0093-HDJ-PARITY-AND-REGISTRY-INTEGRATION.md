# RFC-0093: HDJ parity and registry integration

**Status:** Accepted / implemented and verified
**Phase:** 0.66  
**Decision:** D-111  
**Contract refine:** D-112  
**Baseline:** `v0.65.0`

## Summary

Phase 0.66 restores `hedron-jinja` as a real consumer of Hedron's portable contracts and owns the
open defect and presentation backlog captured during phase intake. HDJ keeps
ordinary Jinja/HTML semantics and gains one frozen, app-scoped binding that projects trusted core
registry facts, live handles explicitly supplied by the application, portable request facts,
providers, themes, assets, and redacted application-style metadata.

This phase corrects coordinated-train drift: a package version bump is not evidence that Jinja
implements a core feature. Every 0.66 claim requires an HDJ render-path test or an explicit
Progressive/Deferred disposition.

The HDJ foundation and all thirteen issue-owned gates are implemented and verified in-tree. The
[open-issue inventory](../acceptance/open-issues-066.toml) records the completed evidence.

## Problem

After phase 0.48, most `hedron-jinja` releases changed only dependency/version metadata. The package
could still render explicitly bound components, but it had no application identity, registry
snapshot, application-style projection, generic provider binding, or request HTMX facts. Catalog
logical IDs resolved to descriptors rather than usable live handles. Dynamic/package namespaces
were described inconsistently: manifest types existed while the render path rejected them.

## Contract

### `JinjaBinding`

`JinjaBinding` is immutable and owns exactly one non-empty `app_id`. It may contain:

- explicitly trusted component aliases and live handle objects;
- application-approved public asset URLs, registry theme names, and redacted
  application-style facts;
- explicit provider manifests; and
- a deterministic fingerprint used in render traces and deployment comparison.

`JinjaBinding.from_registry()` consumes only `hedron-core` public registry contracts. Component
metadata may be imported only from the trusted registered module/name pair and must resolve to a
`Component` subclass. Live handles are never reconstructed from manifests or descriptors; the
application must supply them explicitly and their `app_id` must match.

Core `AssetMeta.path` values are source/package locations, not public URLs. Registry assets enter
the binding only through the application's explicit `asset_hrefs` mapping; source paths never enter
the HDJ environment.

### Template helpers

An app-bound environment installs `h_view`, `h_command_form`, `h_catalog_facts`, `h_type_schema`, and
`h_feature_bundles`. View and command helpers resolve an app-scoped logical ID to the explicitly
bound live object, render it through the active HDJ `RenderSession`, and preserve assets, headers,
identity, diagnostics, and traces. Raw manifest dictionaries remain non-executable.

### `HdjContext`

The immutable `hdj` facade adds application identity, binding fingerprint, registered theme names,
redacted application-style facts, provider facts, and explicit portable HTMX request facts. It never
contains a raw request, session, container, registry builder, absolute stylesheet path, secret, or
handler callable.

### Providers and feature checking

Data, charts, maps, elements, and extras use the same `ProviderManifest` shape. In an app-bound
environment, declaring a provider feature requires that exact provider in the binding. Static
analysis recognizes app-bound interaction, TypeSchema, feature-bundle, and application-style helper
use. Provider declarations do not install packages, register routes, or grant policy.

## Security and authority

- The core registry remains the metadata authority; Jinja receives a frozen projection.
- Live handles remain application-supplied capabilities and are app-ID checked.
- Catalog and TypeSchema facts are read-only; templates cannot execute descriptors or manifests.
- Application-style facts omit source paths and file contents.
- HTMX facts are bounded portable values and never a framework request.
- Existing strict sink checks, autoescape, CSP reconciliation, secrets, URL purposes, and render
  budgets remain mandatory.

## Compatibility

Existing `HedronJinja(environment, components=..., assets=...)` construction remains supported.
`binding=` and `app_id=` are additive. Existing direct helper functions retain their legacy behavior;
logical-ID rendering requires a `JinjaBinding` containing the live handle.

HDJ format v1 remains the write format. `jinja.dynamic-dependencies`, `jinja.foreign`, and package
template execution remain Deferred: 0.66 documents the rejection honestly and does not pretend that
inventory-only manifest types are a loader implementation.

## Non-goals

- a second component, catalog, theme, styling, security, or interaction registry;
- evaluating Python annotations or importing the flagship/framework adapters;
- reconstructing executable handles from portable manifests;
- exposing raw framework requests or mutable registries to templates;
- making Jinja a hostile-author sandbox;
- HDJ v2 or dynamic/package template execution.

## Open-issue ownership

Phase intake audited every open repository issue. [#613](https://github.com/eddiethedean/hedron/issues/613)
and [#140](https://github.com/eddiethedean/hedron/issues/140) already had implementation and focused
regression evidence on `main`, so they were closed rather than assigned new phase work. The remaining
issue ownership was required 0.66 work and is now closed with regression evidence:

| Issues | Outcome | Gates |
|---|---|---|
| [#718](https://github.com/eddiethedean/hedron/issues/718), [#726](https://github.com/eddiethedean/hedron/issues/726) | Transactional audit behavior and truthful WebSocket producer failure propagation | `DATA-AUDIT-066`, `WS-PRODUCER-066` |
| [#719](https://github.com/eddiethedean/hedron/issues/719), [#720](https://github.com/eddiethedean/hedron/issues/720), [#723](https://github.com/eddiethedean/hedron/issues/723), [#724](https://github.com/eddiethedean/hedron/issues/724) | Standards-valid numeric and JSON boundaries for HTMX, maps, Altair, and Plotly | `HTMX-JSON-066`, `MAP-NUMERIC-066`, `ALTAIR-JSON-066`, `PLOTLY-JSON-066` |
| [#721](https://github.com/eddiethedean/hedron/issues/721), [#722](https://github.com/eddiethedean/hedron/issues/722), [#727](https://github.com/eddiethedean/hedron/issues/727) | Null-safe claim redaction, bounded theme archives, and finite rate-limit windows | `CLAIM-REDACT-066`, `THEME-ARCHIVE-066`, `AUTH-RATE-066` |
| [#725](https://github.com/eddiethedean/hedron/issues/725) | Valid next-major dependency ceilings in generated scaffolds | `PIN-CEILING-066` |
| [#728](https://github.com/eddiethedean/hedron/issues/728)–[#730](https://github.com/eddiethedean/hedron/issues/730) | Bounded typography measure, safe effects, and contextual presentation variants | `TYPE-MEASURE-066`, `TYPE-EFFECT-066`, `CONTEXT-PRESENT-066` |

## Release gates

`CONTRACT-066`, `BINDING-066`, `REGISTRY-066`, `INTERACTION-066`, `CONTEXT-066`, `PROVIDER-066`,
`STYLE-066`, `SECURITY-066`, `COMPAT-066`, `DOCS-066`, `PKG-066`, and `REGRESS-066` establish the
verified HDJ foundation. Every gate in `open-issues-066.toml` is also Verified, every listed issue
is closed with regression evidence, and there are zero undocumented Deferred rows for the phase cut.
