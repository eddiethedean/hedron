# Security review brief — phase 0.47 first-class maps

**Cut targets:** Hedron `v0.47.0`; `hedron-maps` `0.1.0`  
**Owning RFC / decision:** RFC-0074 / D-078 / D-082  
**Tracking:** [#350](https://github.com/eddiethedean/hedron/issues/350)  
**Primary gates:** `SPEC-047`, `PROVIDER-047`, `OFFLINE-047`, `RENDER-047`, `INTERACT-047`,
`SECURITY-047`, `PKG-047`

## Review scope

- MapSpec parsing, prototype-pollution keys, origin/template closure, credentials/userinfo,
  protocol-relative and unsafe schemes, HTTPS-only remotes.
- Style-graph closure for sprites/glyphs/sources; locked layer types; no callbacks/eval.
- `sanitize_geojson` reuse; popup limited to Hedron nodes or text.
- Optional proxy SSRF: origin allowlist, DNS revalidation, private/loopback/link-local denial,
  redirect/response/time bounds.
- MBTiles construction-time path, parameterized XYZ, no request filesystem path, no SQL concat.
- `hedron-map` lifecycle, CSP worker, HTMX dispose, duplicate-mount guard.
- MapInteraction payloads as untrusted Pydantic input to registered ActionHandles.

## Required adversarial cases

1. Credentialed, protocol-relative, javascript:, and HTTP tile templates.
2. `__proto__` style/spec keys and unsafe GeoJSON properties.
3. Request-derived MBTiles paths and SQL concatenation attempts.
4. Proxy to 127.0.0.1 / link-local / metadata IPs.
5. Oversized GeoJSON, plans, and event payloads.

This packet is a maintainer threat review, not a product WCAG/SLA claim. `SR-021` stays open.
