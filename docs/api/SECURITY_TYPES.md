# Security boundary types

**Status:** Accepted

`Secret`, `TrustedHtml`, and `SafeUrl` make security-sensitive intent visible to typing, rendering, diagnostics, and review.

```python
from hedron import SafeUrl, Secret, TrustedHtml, UrlPurpose

token = Secret("deployment-token")
profile = SafeUrl.parse("/users/42", purpose=UrlPurpose.NAVIGATION)
body = TrustedHtml.reviewed(sanitized_html, source="application-sanitizer:v1")
```

## `Secret[T]`

`Secret(value)` stores a typed sensitive value. Its string conversion, representation, serialization, examples, diagnostics, traces, identities, and Explorer display are redacted. `reveal()` is the explicit application-only access operation; Hedron never reveals a secret implicitly to props, markup, URLs, cache-key text, logs, or browser metadata.

## `TrustedHtml`

`TrustedHtml.reviewed(value, *, source)` creates an immutable raw-markup value at an explicit trust boundary. `source` is non-secret provenance for audit and diagnostics. The direct constructor is not public. Integrations with supported sanitizers may provide equivalent named constructors that record a policy/version.

Only the dedicated `hedron.html.raw(...)` primitive accepts `TrustedHtml`. Wrapping a value does not sanitize it, weaken Content Security Policy, permit unregistered scripts/assets, or authorize its source. Ordinary strings always render as escaped text.

## `SafeUrl` and `UrlPurpose`

`SafeUrl.parse(value, *, purpose, allow_external=False)` validates and normalizes a URL for one of the initial purposes: `NAVIGATION`, `ASSET`, `FORM_ACTION`, or `REDIRECT`. Relative same-origin URLs are the default. HTTP(S) external URLs require `allow_external=True`; `mailto` and `tel` are allowed only for an explicitly supported navigation context. Dangerous, ambiguous, credential-bearing, control-character, or policy-incompatible schemes fail validation.

A `SafeUrl` remains subject to the final rendering or redirect context policy. It is not an authorization decision, open-redirect bypass, signature, or proof that a remote resource is trusted. Registered application asset references remain preferable to arbitrary asset URLs.

## Stability and errors

These values are immutable and safe to compare, but their representations never expose secret content. Validation errors use stable security diagnostics and include the purpose and remediation without echoing sensitive input. Adding a URL purpose or trusted constructor is a public API change.
