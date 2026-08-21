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
pip install "hedron[sanitize]>=0.56.0,<0.59"
# or
pip install "hedron[markdown]>=0.56.0,<0.59"
```

Missing nh3 raises `HED-SEC-0020` with that remediation. Integrations with supported sanitizers may provide equivalent named constructors that record a policy/version.

Only the dedicated `hedron.html.raw(...)` primitive accepts `TrustedHtml`. Wrapping a value does not sanitize it (except via `TrustedHtml.nh3`), weaken Content Security Policy, permit unregistered scripts/assets, or authorize its source. Ordinary strings always render as escaped text.

## `SafeUrl` and `UrlPurpose`

`SafeUrl.parse(value, *, purpose, allow_external=False)` validates and normalizes a URL for one of the initial purposes: `NAVIGATION`, `ASSET`, `FORM_ACTION`, or `REDIRECT`. Relative same-origin URLs are the default. HTTP(S) external URLs require `allow_external=True`; `mailto` and `tel` are allowed only for an explicitly supported navigation context. Dangerous, ambiguous, credential-bearing, control-character, Unicode format/bidi/ZWSP/BOM-smuggled, or policy-incompatible schemes fail validation (`HED-SEC-0001`).

URL-bearing HTML attributes—including `href`, `src`, `action`, `srcset`, `ping`, and HTMX URL attrs such as `hx-get` / `hx-push-url` / `hx-replace-url`—require `SafeUrl` (or a validated `srcset` string whose candidates pass `SafeUrl` checks). Local HTMX path strings starting with `/` may be coerced at construction for HTMX attrs.

A `SafeUrl` remains subject to the final rendering or redirect context policy. Application helpers `redirect_local` and `redirect_external` enforce the same local-vs-external split; `redirect_external` is disabled unless the security policy sets `allow_external_redirects=True`.

## `SecurityPolicy` and `SecurityProfile`

FastAPI apps select a named profile (`"development"` \| `"standard"` \| `"strict"`) or pass
an explicit `SecurityPolicy` to `Hedron(security=...)`. Profiles are frozen dataclasses —
mutate by constructing a new policy, not by assigning fields.

| Field | Type | Default (standard) | Notes |
|---|---|---|---|
| `profile` | `SecurityProfile` | `STANDARD` | Named preset used to build the policy |
| `version` | `int` | `1` | Policy schema version |
| `csrf_enabled` | `bool` | `True` | Validate CSRF on unsafe methods |
| `csrf_cookie_name` | `str` | `"hedron_csrf"` | Cookie set on safe GETs |
| `csrf_header_name` | `str` | `"X-CSRF-Token"` | Preferred header for HTMX / fetch |
| `csrf_form_field` | `str` | `"csrf_token"` | Hidden form field name |
| `private_authenticated_cache` | `bool` | `True` | Adds `Cache-Control: private, no-store` when authenticated |
| `security_headers` | `SecurityHeadersPolicy` \| `bool` \| `Literal["app"]` | `True` | `True` emits profile headers (XFO / CTO / Referrer-Policy / CSP). Pass `SecurityHeadersPolicy(...)` to merge/override per header. `False` or `"app"` skips Hedron headers (host owns them). See [CSRF composition](CSRF_COMPOSITION.md). |
| `content_security_policy` | `str` \| `None` | standard CSP string | `None` in development; stricter in `strict` |
| `frame_options` | `str` | `"DENY"` | `X-Frame-Options` |
| `content_type_options` | `str` | `"nosniff"` | `X-Content-Type-Options` |
| `referrer_policy` | `str` | `"no-referrer"` | `Referrer-Policy` |
| `explorer_enabled` | `bool` | `False` | Development profile may enable Explorer |
| `allow_external_redirects` | `bool` | `False` | Required for `redirect_external` |
| `findings` | `tuple[str, …]` | profile notes | Advisory strings for diagnostics / check |

| Profile | CSRF | CSP | Explorer | External redirects |
|---|---|---|---|---|
| `development` | on | none | may mount | off |
| `standard` | on | default-src self (+ limited inline style) | off | off |
| `strict` | on | tighter CSP, `frame-ancestors 'none'` | off | off |

```python
from hedron import Hedron
from hedron.security.policy import SecurityPolicy

app = Hedron(title="App", security="standard", session_secret="replace-in-production")
# or:
policy = SecurityPolicy.from_name("strict")
app = Hedron(title="App", security=policy, session_secret="replace-in-production")
```

CSRF cookie/header/form field names on `SecurityPolicy` are in the small **stable** API
tier — see [STABILITY.md](STABILITY.md). Full guide: [Security](../guides/security.md).

Composition (strategies, header merge, `CsrfField`) — shipped on **0.22**:
[CSRF and SecurityPolicy composition](CSRF_COMPOSITION.md).

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
| Missing nh3 for `TrustedHtml.nh3` | `HED-SEC-0020` | `pip install "hedron[sanitize]>=0.56.0,<0.59"` (or `[markdown]`) |
| Secret leaked via str/repr | Redacted | Call `reveal()` only in trusted application code |
| `html.raw(...)` without `TrustedHtml` | Rejected | Wrap reviewed markup with `TrustedHtml.reviewed` / `.nh3` |
| External redirect without policy | Rejected | Set `allow_external_redirects=True` on an explicit `SecurityPolicy` |

Adding a URL purpose or trusted constructor is a public API change. See
[Security guide](../guides/security.md) and [Error codes](../guides/error-codes.md).
