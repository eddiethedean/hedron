# What’s new in Hedron 0.22

!!! note "Current train is 0.51"

    Pin `hedron>=0.51.0,<0.52` for new apps. The pin below is historical for this train only.
    See [What’s new in 0.51](whats-new-0.51.md).


**Published** as `v0.22.0`. Historical pin: `hedron>=0.22.0,<0.23`.

Phase **0.22** ships CSRF and SecurityPolicy composition (D-051):

- **Pluggable CSRF strategies** — `DoubleSubmitCookieCsrf` (default) and
  `SessionTokenCsrf(get_expected=...)` for DB-backed / app-owned tokens without Starlette
  cookie sessions (`CSRF-022`).
- **Composable security headers** — `SecurityHeadersPolicy` merge/override per header without
  turning Hedron headers entirely off (`HEADERS-022`).
- **`CsrfField` + `Form(hx=Hx(...))`** — first-class CSRF field and HTMX kwargs (`FORM-022`).

Contract: [CSRF composition](../api/CSRF_COMPOSITION.md). Acceptance:
[RELEASE_0_22](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_22.md).

Human AT sessions (`SR-021` / …) remain Planned / not Supported. Next: stable-tier expansion
(**0.23**).
