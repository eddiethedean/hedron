---
type: security
title: Security and request boundaries
description: Hedron's security model defaults to CSRF, hardened headers, local redirects, escaped HTML, declared HTMX targets, and explicit opt-ins for trusted markup or broader capabilities.
tags: [security, csrf, html, htmx]
verified:
  - by: openwiki/0.5.2
    at: 2026-09-19T19:14:00.347Z
sources:
  - id: openwiki-source-722de2944b74ef973aa48cbf
    resource: repo://packages/hedron-core/src/hedron_core/html.py
  - id: openwiki-source-e16388f5f61e9bd0885aa56a
    resource: repo://packages/hedron-core/src/hedron_core/htmx/authorize.py
  - id: openwiki-source-77c7e52d0931db41d7101f66
    resource: repo://packages/hedron-core/src/hedron_core/htmx/policy.py
  - id: openwiki-source-d0fb08da316ee2c4e8280b1a
    resource: repo://packages/hedron-core/src/hedron_core/security_policy.py
  - id: openwiki-source-5d6ab999a4cac5ba80b9020d
    resource: repo://packages/hedron-core/src/hedron_core/security/trusted.py
  - id: openwiki-source-4ae93ccd972efe0798aa7ada
    resource: repo://packages/hedron/src/hedron/security/csrf.py
  - id: openwiki-source-81a7d0d6e32c7a45e3acfbb4
    resource: repo://packages/hedron/src/hedron/security/headers.py
  - id: openwiki-source-6a256703c22c172748acb275
    resource: repo://packages/hedron/src/hedron/security/redirects.py
  - id: openwiki-source-67cdc1d6d9d91e0b10c11909
    resource: repo://tests/integration/test_fastapi_mvp.py
  - id: openwiki-source-d0ccdbe9aae4a3e316d8f890
    resource: repo://tests/security/test_security_046.py
generated: { by: "codex", at: "2026-09-19T15:43:01.076Z" }
---

# Security and request boundaries

Hedron treats browser requests, rendered HTML, redirects, and optional integrations as explicit capability boundaries. Defaults are intentionally conservative; an opt-in should be visible in application configuration or a typed trust/authorization API. The [requests and partial-page interactions](/openwiki/architecture/requests-and-interactions.md) page explains where these checks sit in the route lifecycle.

## Security profiles and headers

`SecurityPolicy` is a versioned, adapter-shared policy. Its defaults enable CSRF and security headers, keep authenticated responses private, deny external redirects, deny HTMX evaluation, and deny egress by default. The standard profile supplies same-origin CSP/resource defaults, request budgets, and HTMX browser hardening; the strict profile adds a tighter CSP, disables Explorer, requires intent/posture controls, and keeps history/evaluation hardening enabled. Development may expose Explorer, but it still keeps HTMX evaluation disabled.

The generated HTMX configuration denies eval and script tags, requires same-origin requests, and—outside the development profile—disables the history cache. `SecurityHeadersMiddleware` applies policy headers, forces authenticated cache directives to private/no-store, and prevents HTMX responses from remaining publicly cacheable. Hosts can explicitly take ownership of headers by disabling policy header emission or using the per-header override structure.

## CSRF and request provenance

With the default cookie-backed strategy, pages and `ensure_csrf_cookie()` share one token, and unsafe requests validate the configured header or form token. Cookie security follows the strict/production/TLS boundary; forwarded HTTPS is honored only when the connecting peer is in the trusted-proxy allowlist. Missing or invalid tokens are audited and return HTTP 403, and malformed form parsing fails closed rather than accepting an absent token.

## HTML and navigation trust

Native `html.*` elements reject executable/active tags such as script, reject unknown non-custom tags, and normalize attributes through the HTML policy. `html.raw()` accepts only a `TrustedHtml` value; ordinary strings cannot cross that boundary. `TrustedHtml` has no public constructor: callers must use `TrustedHtml.reviewed(value, source=...)` or the optional `TrustedHtml.nh3()` sanitizer, which records provenance.

Local redirects are the default navigation path and reject non-local URLs. External redirects validate scheme, host syntax, whitespace, credentials, and control characters, then fail closed unless `SecurityPolicy.allow_external_redirects` is explicitly enabled. The [rendering and component model](/openwiki/architecture/rendering-and-components.md) therefore treats raw markup and response mode as separate policy decisions rather than implicit string behavior.

## HTMX targets and capabilities

Declared `FragmentRegion` values authorize request targets and response selectors; undeclared HTMX targets are rejected by default. Error responses use framework-owned sinks instead of reflecting a rejected client target. A bundle ID is not an authorization capability, and consuming a disabled MCP projection does not enable it: authorization and integration enablement must be explicit.

The focused tests are useful security references: a reviewed script value still fails the fragment asset boundary with `HED-EXT-0011`, unsafe actions reject missing CSRF and succeed with the seeded token, and bundle/projection identifiers do not infer authorization or enable MCP. See [quality and release contracts](/openwiki/operations/quality-and-release.md) for the security test lane.
