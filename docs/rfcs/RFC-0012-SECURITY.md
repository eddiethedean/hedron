# RFC-0012: Security

**Status:** Accepted

## Principle

Security is part of every model, component, route, action, form, asset, cache, integration, and developer tool. Hedron automates secure mechanics only when the interpretation is unambiguous; it never infers authorization or trust.

## Baseline controls

- Context-aware escaping for text, attributes, URLs, CSS, and JSON.
- `TrustedHtml`, `SafeUrl`, and `Secret` typed boundaries.
- Forbidden extra model fields by default.
- Explicit addressability and framework-native dependencies.
- CSRF protection for unsafe cookie-authenticated actions.
- GET remains safe and idempotent by contract.
- Safe local redirects; external redirects are explicit.
- Private, no-store defaults for authenticated fragments.
- Strict asset roots, fingerprinted local assets, and CSP-compatible output.
- Explorer disabled in production by default with pervasive redaction.
- CI diagnostics with stable codes and SARIF output.

Hedron does not implement cryptography, sanitization, identity, or authorization policy. It integrates maintained libraries and preserves host-framework mechanisms.

## Profiles

Development permits local diagnostics without exposing secrets. Standard production enables secure headers, escaping, CSRF, explicit exposure, and private caching. Strict mode rejects raw HTML, inline scripts/styles, remote assets, and selected warnings.

## Acceptance criteria

- The security acceptance suite includes XSS contexts, CSRF, route exposure, cache leakage, redirects, assets, secrets, Explorer access, and forged DataEditor changes.
- Security failures include remediation without echoing sensitive values.

