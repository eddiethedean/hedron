# Map policy and security

`MapPolicy.allowed_origins` is an exact HTTPS origin list. Compilation derives remaining
resource origins from templates, TileJSON, and style graphs.

- Reject credentials/userinfo, protocol-relative URLs, and unsafe schemes.
- Popup content is Hedron nodes or text. GeoJSON is sanitized with
  `hedron_core.sanitize_geojson` (keep `HED-MAP-0001`–`0004`).
- Optional same-origin proxy (`hedron_maps.proxy.assert_ssrf_safe`) revalidates origins,
  DNS, redirects, and response/time bounds. Private/loopback/link-local addresses fail.
- CSP facts on `MapPlan.csp` are for Explorer/deployment composition, not a product SLA.

Maintainer threat review: `docs/acceptance/security-review-047/`.
