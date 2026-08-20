# HedronPosit deployment lifecycle (`v0.52`)

**Status:** Stage 1 Implemented / Verified. Living tip `v0.54.0`
(in-tree Published; tag/PyPI deferred).<br>
**Tracking:** [#522](https://github.com/eddiethedean/hedron/issues/522)<br>
**Related:** [#508](https://github.com/eddiethedean/hedron/issues/508)–[#513](https://github.com/eddiethedean/hedron/issues/513)<br>
**Decision/RFC:** D-089, refined by D-090 /
[RFC-0079](../rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md)<br>
**Planning baseline:** Published in-tree `v0.51.2`<br>
**Target:** Hedron `v0.52.0` (in-tree cut; do not tag yet)

## Consume shipped, do not fork

- `HedronPosit` helpers: `href` / `href_for`, `redirect` / `redirect_for`,
  `browser_url` / `browser_url_for`, `external_url` / `durable_url`
- `CookieRegistry` + set/delete lifecycle; `cookie_path_for_mount` and
  `workbenchify` owned-cookie Path repair
- Request-bound `PositContext` / `posit_for(request)`
- Opt-in `hands_off` URL / redirect adaptation (validated same-app paths only)
- `ConnectCookieMode.NATIVE` Supported; authenticated-header bridge stays
  `drop_supported`
- CLI `hedron-posit check` / `run` / `doctor` / `check --matrix`
- Proactive `PositDiagnostic` codes (never log cookie values)
- Named-route query/fragment/durable parity across href/redirect families
- Do **not** restore Supported Connect cookie bridge
- Do **not** reopen `polling_only`, `MORPH-048`, Explorer 0.50, 0.51 extras,
  0.53, 0.54, or `SR-021`

## Architecture

```text
hedron-posit           cookie registry, PositContext, hands_off, matrix, diagnostics
       │
       ├── root / Workbench / Connect mounts
       ├── URL helpers (href_for parity under ROUTEURL-052)
       └── doctor / check --matrix (MATRIX-052)
```

1. Apps stop computing cookie paths — use `CookieRegistry`.
2. `PositContext` is request-bound; no `request.app` cast.
3. Hands-off rewrites only validated same-app paths.
4. Diagnostics never log cookie values.
5. Conformance authority is a sibling workstream — see
   [CONFORMANCE_052](CONFORMANCE_052.md).
