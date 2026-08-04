# Security controls implementation

## Central policy

A versioned `SecurityPolicy` supplies escaping, URL schemes, attributes, CSRF integration, redirect, cache, header, asset, Explorer, and strict-mode decisions. Subsystems query narrow policy interfaces instead of duplicating rules.

## Enforcement points

- Model creation: reject unsupported fields and install redaction metadata.
- Jinja checking and CSS compilation: reject unsafe constructs with source diagnostics.
- Routing: require explicit addressability and preserve dependencies.
- Serialization: contextually escape and require trusted types.
- Actions/forms: enforce unsafe-method and CSRF policy.
- Caches: incorporate declared security/tenant/locale dimensions.
- Assets: restrict roots, schemes, MIME types, and executable content.
- Explorer/logging: sanitize through shared redaction before storage or transmission.

Hedron integrates framework or application CSRF, authentication, and authorization where authoritative. It supplies a default CSRF mechanism only for supported cookie-authenticated Hedron actions lacking one.

## Verification

Maintain a threat model and adversarial fixtures for XSS contexts, CSRF, SSRF-like URLs, open redirects, path traversal, cache confusion, mass assignment, forged DataEditor changes, secret leakage, component-route exposure, plugin assets, and Explorer access. Security diagnostics use stable codes and support SARIF.
