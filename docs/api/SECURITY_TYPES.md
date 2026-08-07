---
status: shipped
---

# Security boundary types


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Accepted

`Secret`, `TrustedHtml`, and `SafeUrl` make security-sensitive intent visible to typing, rendering, diagnostics, and review.

```python
from hedron import SafeUrl, Secret, TrustedHtml, UrlPurpose

token = Secret("deployment-token")
profile = SafeUrl.parse("/users/42", purpose=UrlPurpose.NAVIGATION)
body = TrustedHtml.reviewed(sanitized_html, source="application-sanitizer:v1")
```

## `Secret[T]`

`Secret(value)` stores a typed sensitive value. When used in Hedron/Pydantic models as `Secret[T]`, the inner value is validated against `T` (for example `Secret[str]` rejects an `int`). Its string conversion, representation, serialization, examples, diagnostics, traces, identities, and Explorer display are redacted. `reveal()` is the explicit application-only access operation; Hedron never reveals a secret implicitly to props, markup, URLs, cache-key text, logs, or browser metadata.

## `TrustedHtml`

`TrustedHtml.reviewed(value, *, source)` creates an immutable raw-markup value at an explicit trust boundary. `source` is non-secret provenance for audit and diagnostics. The direct constructor is not public.

`TrustedHtml.nh3(value, *, tags=None)` sanitizes HTML with [nh3](https://github.com/messense/nh3) and records `source` as `nh3:<version>`. Requires the optional dependency:

```bash
pip install "hedron[sanitize]"
# or
pip install "hedron[markdown]"
```

Missing nh3 raises `HED-SEC-0020` with that remediation. Integrations with supported sanitizers may provide equivalent named constructors that record a policy/version.

Only the dedicated `hedron.html.raw(...)` primitive accepts `TrustedHtml`. Wrapping a value does not sanitize it (except via `TrustedHtml.nh3`), weaken Content Security Policy, permit unregistered scripts/assets, or authorize its source. Ordinary strings always render as escaped text.

## `SafeUrl` and `UrlPurpose`

`SafeUrl.parse(value, *, purpose, allow_external=False)` validates and normalizes a URL for one of the initial purposes: `NAVIGATION`, `ASSET`, `FORM_ACTION`, or `REDIRECT`. Relative same-origin URLs are the default. HTTP(S) external URLs require `allow_external=True`; `mailto` and `tel` are allowed only for an explicitly supported navigation context. Dangerous, ambiguous, credential-bearing, control-character, Unicode format/bidi/ZWSP/BOM-smuggled, or policy-incompatible schemes fail validation (`HED-SEC-0001`).

URL-bearing HTML attributes—including `href`, `src`, `action`, `srcset`, `ping`, and HTMX URL attrs such as `hx-get` / `hx-push-url` / `hx-replace-url`—require `SafeUrl` (or a validated `srcset` string whose candidates pass `SafeUrl` checks). Local HTMX path strings starting with `/` may be coerced at construction for HTMX attrs.

A `SafeUrl` remains subject to the final rendering or redirect context policy. Application helpers `redirect_local` and `redirect_external` enforce the same local-vs-external split; `redirect_external` is disabled unless the security policy sets `allow_external_redirects=True`.

## `csrf_token_for_request`

Public FastAPI helper (re-exported from `hedron` and `hedron.security`) that returns the
CSRF token for the current request under the app’s `SecurityPolicy`. Use it to seed
hidden form fields or headers after a safe GET — see
[Minimal form POST](../guides/minimal-form.md).

```python
from hedron import csrf_token_for_request

token = csrf_token_for_request(request, request.app.state.hedron_security)
```

## Stability and errors

These values are immutable and safe to compare, but their representations never expose secret content.

## Errors

| Situation | Code / behavior | What to do |
|---|---|---|
| Invalid / dangerous URL | `HED-SEC-0001` (and related) | Use `SafeUrl.parse` with the correct `UrlPurpose`; avoid `javascript:` and credentialed URLs |
| URL purpose mismatch for attribute | `HED-SEC-0006` | Match purpose to the attribute (`NAVIGATION`, `ASSET`, `FORM_ACTION`, `REDIRECT`) |
| Missing nh3 for `TrustedHtml.nh3` | `HED-SEC-0020` | `pip install "hedron[sanitize]>=0.18.0"` (or `[markdown]`) |
| Secret leaked via str/repr | Redacted | Call `reveal()` only in trusted application code |
| `html.raw(...)` without `TrustedHtml` | Rejected | Wrap reviewed markup with `TrustedHtml.reviewed` / `.nh3` |

Adding a URL purpose or trusted constructor is a public API change. See
[Security guide](../guides/security.md) and [Error codes](../guides/error-codes.md).
