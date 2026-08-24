---
description: Look up stable HED diagnostic codes, severity, meaning, and remediation.
search:
  boost: 1.4
---

# Error codes

Stable `HED-*` diagnostics from `hedron_core.codes`. Prefer these codes in CI and
support reports. Full format: [Diagnostics](https://github.com/eddiethedean/hedron/blob/main/docs/DIAGNOSTICS.md).

This catalog is complete for the registered set enforced by
`scripts/check_hed_codes.py --docs-align` (`HEDDOC-017`).

`HED-TYPE-*` codes for type-driven authoring are documented under
[HED-TYPE (0.44)](#hed-type-044). FastAPI/Pydantic convergence codes are under
[HED-FP (0.49)](#hed-fp-049). Catalog/projection codes are under
[HED-CATALOG (0.45)](#hed-catalog-045) and [HED-PROJECTION (0.45)](#hed-projection-045).
Feature-bundle codes are under [HED-BUNDLE (0.46)](#hed-bundle-046). Maps families
reserved for 0.47 are listed under [HED-MAP](#hed-map).

## Common errors (what to do)

| Code | Severity | Meaning | Fix |
|---|---|---|---|
| `HED-BUILD-0003` | blocker | Production mode without a build manifest | Run `hedron build`; set `HEDRON_BUILD_DIR` if needed — [Troubleshooting](troubleshooting.md#production-startup-missing-manifest-hed-build-0003) |
| `HED-BUILD-0004` | blocker | Runtime compile refused in production | Prebuild assets; do not rely on runtime CSS compile under `HEDRON_ENV=production` |
| `HED-SEC-0001` | blocker | Dangerous or invalid URL | Use `SafeUrl.parse` with the right `UrlPurpose` |
| `HED-SEC-0006` | blocker | URL purpose mismatch for an attribute | Match purpose to `href` / `src` / `action` / redirect context |

| `HED-ELEMENT-0001` | blocker | Element tag/definition conflict | Align definitions or choose a new tag/logical id |
| `HED-ELEMENT-0002` | blocker | Incompatible element ABI pair | Align markup/module ABI majors |
| `HED-ELEMENT-0003` | blocker | First-party naming / prefix violation | Use `hedron-*` for first-party tags |
| `HED-ELEMENT-0005` | blocker | Structured input bound/encoding failure | Reduce payload size/depth |
| `HED-ELEMENT-ASSET-0001` | blocker | Packaged element asset path escape | Pass a single basename under `static/` |
| `HED-ELEMENT-ASSET-0002` | blocker | Packaged element asset missing | Use a filename that ships in the package |
| `HED-ELEMENT-AUTHOR-0001` | blocker | Incomplete third-party author metadata | Declare every required author metadata surface |
| `HED-ELEMENT-AUTHOR-0002` | blocker | Invalid author tag or a11y contract | Use a hyphenated tag and mapping `a11y_contract` |
| `HED-ELEMENT-STATE-0002` | blocker | Illegal element-owned capability | Keep capabilities server-controlled |
| `HED-ELEMENT-STATE-0006` | blocker | Draft transfer before 0.41 | Keep drafts instance-local |
| `HED-SIM-ASSET-0001` | blocker | Packaged sim asset path escape | Pass a single basename under `static/` |
| `HED-SIM-ASSET-0002` | blocker | Packaged sim asset missing | Use a filename that ships in `hedron_sim/static/` |
| `HED-SEC-0020` | blocker | `TrustedHtml.nh3` without nh3 installed | `pip install "hedron[sanitize]>=0.62.0,<0.63"` |
| `HED-RENDER-0012` | blocker | Component render cycle | Remove self-recursion; nested same-type trees are allowed |
| `HED-HTMX-*` / HTTP **403** on fragments | blocker | Unauthorized `HX-Target` / region | Declare `fragment_regions` — [Interaction API](../api/INTERACTION.md#errors) · [Troubleshooting](troubleshooting.md#htmx-403-on-fragment-request) |
| `HED-HTMX-0002` | warning | Same id in `select_oob` and `OobUpdate` | Prefer explicit `OobUpdate`; omit matching `select_oob` — [Interaction API](../api/INTERACTION.md#out-of-band-updates) |
| `HED-EXPLORER-0001` | warning | Explorer table truncated | Use `cursor` / `limit` query params; HTML banners include Next/Previous |
| `HED-EXPLORER-0002` | warning | Explorer provider timed out or crashed | Fix the panel callback; other `/packages` panels keep rendering |
| `HED-EXPLORER-0003` | warning | Explorer provider payload too large | Reduce panel output under `max_payload_bytes` |
| `HED-CAP-0001` | blocker | Capability denied / missing provider | Install a `CapabilityProvider` or remove `capability=` |
| `HED-REPLAY-0001` | blocker | Idempotency key required | Send `Idempotency-Key` header or form field |
| `HED-REPLAY-0002` | blocker | Idempotency key conflict | Use a new key for a distinct mutation |
| `HED-REPLAY-0003` | warning | Idempotency key in flight | Retry after the first request completes |
| `HED-REPLAY-0004` | blocker | Replay store misconfigured | Install a `ReplayStore` or omit `hedron_replay_store=None` |
| `HED-UPGRADE-0001` | blocker | Unsupported upgrade from_version | Use a supported `0.x` from version |
| `HED-UPGRADE-0002` | blocker | Stale upgrade baseline schema | Refresh the reviewed baseline |
| CSRF **403** on POST | blocker | Missing or mismatched CSRF token | Seed on GET; include token on POST — [Troubleshooting](troubleshooting.md#csrf-403-on-post-fastapi-flask) |
| `HED-VIEW-0003` | blocker | Unbound parameterized handle mounted | Call `handle.bind(...)` before mount |
| `HED-UPDATE-0001` | blocker | Mixed refresh and patch | Return `refresh(...)` or `patches(...)`, not both |
| `HED-CMD-0002` | blocker | Command has no ordinary HTTP fallback | Pass `fallback=` to `@app.command` |
| `HED-PLUGIN-0001` | blocker | Named plugin missing from entry points | Install the package or remove the name from `[tool.hedron].plugins` |
| `HED-PLUGIN-0002` | blocker | Plugin `hedron_version` incompatible | Upgrade/downgrade the plugin or pin Hedron into its range |
| `HED-JOB-0001` | blocker | Job observation unauthorized / unscoped | Scope jobs with `auth_subject` / `tenant_id`; use `job_authorized_http` |
| `HED-ASSET-0004` | warning | Asset missing from manifest / disk | Re-run `hedron build` or fix the asset path |
| `HED-CONTENT-0003` | blocker | Images extra missing | `pip install "hedron[images]>=0.62.0,<0.63"` |
| Mount / cookie Path mismatch | ops | App under reverse-proxy subpath | Set `HEDRON_ROOT_PATH` / ASGI `root_path` — [Mount API](../api/MOUNT.md) |

Symptom-first help: [Troubleshooting](troubleshooting.md). Full symbol index below.

## HED-ASSET

| Code | Catalog symbol |
|---|---|
| `HED-ASSET-0001` | `HED_ASSET_UNSUPPORTED_VERSION` |
| `HED-ASSET-0002` | `HED_ASSET_TRAVERSAL` |
| `HED-ASSET-0003` | `HED_ASSET_REMOTE` |
| `HED-ASSET-0004` | `HED_ASSET_MISSING` |
| `HED-ASSET-0005` | `HED_ASSET_COLLISION` |
| `HED-ASSET-0006` | `HED_ASSET_SYMLINK` |
| `HED-ASSET-0007` | `HED_ASSET_MIME` |
| `HED-ASSET-0010` | `HED_BROWSER_DUPLICATE` |
| `HED-ASSET-0011` | `HED_BROWSER_INVALID` |
| `HED-ASSET-0531` | `HED_ASSET_0531` |
| `HED-ASSET-0532` | `HED_ASSET_0532` |
| `HED-ASSET-0533` | `HED_ASSET_0533` |
| `HED-ASSET-0534` | `HED_ASSET_0534` |
| `HED-ASSET-0535` | `HED_ASSET_0535` |
| `HED-ASSET-0536` | `HED_ASSET_0536` |
| `HED-ASSET-0537` | `HED_ASSET_0537` |
| `HED-ASSET-0538` | `HED_ASSET_0538` |

## HED-AUDIT

| Code | Catalog symbol |
|---|---|
| `HED-AUDIT-0001` | `HED_AUDIT_0001` |

## HED-AUTH

| Code | Catalog symbol |
|---|---|
| `HED-AUTH-0001` | `HED_AUTH_0001` |

## HED-AUTO

| Code | Catalog symbol |
|---|---|
| `HED-AUTO-0001` | `HED_AUTO_0001` |
| `HED-AUTO-0002` | `HED_AUTO_0002` |
| `HED-AUTO-0003` | `HED_AUTO_0003` |
| `HED-AUTO-0004` | `HED_AUTO_0004` |

## HED-BUILD

| Code | Catalog symbol |
|---|---|
| `HED-BUILD-0001` | `HED_BUILD_UNSUPPORTED_VERSION` |
| `HED-BUILD-0002` | `HED_BUILD_FAILED` |
| `HED-BUILD-0003` | `HED_BUILD_MISSING_MANIFEST` |
| `HED-BUILD-0004` | `HED_BUILD_RUNTIME_COMPILE` |

## HED-CHART

| Code | Catalog symbol |
|---|---|
| `HED-CHART-0001` | `HED_CHART_0001` |
| `HED-CHART-0002` | `HED_CHART_0002` |
| `HED-CHART-0003` | `HED_CHART_0003` |
| `HED-CHART-0004` | `HED_CHART_0004` |
| `HED-CHART-0005` | `HED_CHART_0005` |
| `HED-CHART-0006` | `HED_CHART_0006` |
| `HED-CHART-0007` | `HED_CHART_0007` |
| `HED-CHART-0010` | `HED_CHART_0010` |
| `HED-CHART-0011` | `HED_CHART_0011` |
| `HED-CHART-0012` | `HED_CHART_0012` |
| `HED-CHART-0013` | `HED_CHART_0013` |
| `HED-CHART-0014` | `HED_CHART_0014` |
| `HED-CHART-0020` | `HED_CHART_0020` |
| `HED-CHART-0021` | `HED_CHART_0021` |
| `HED-CHART-0022` | `HED_CHART_0022` |
| `HED-CHART-0023` | `HED_CHART_0023` |
| `HED-CHART-0024` | `HED_CHART_0024` |
| `HED-CHART-0025` | `HED_CHART_0025` |
| `HED-CHART-0026` | `HED_CHART_0026` |
| `HED-CHART-0030` | `HED_CHART_0030` |
| `HED-CHART-0031` | `HED_CHART_0031` |
| `HED-CHART-0032` | `HED_CHART_0032` |
| `HED-CHART-0033` | `HED_CHART_0033` |
| `HED-CHART-0061` | `HED_CHART_0061` |
| `HED-CHART-0062` | `HED_CHART_0062` |
| `HED-CHART-0063` | `HED_CHART_0063` |
| `HED-CHART-0070` | `HED_CHART_0070` |
| `HED-CHART-0071` | `HED_CHART_0071` |
| `HED-CHART-0072` | `HED_CHART_0072` |
| `HED-CHART-0073` | `HED_CHART_0073` |

## HED-CMD

| Code | Catalog symbol |
|---|---|
| `HED-CMD-0001` | `HED_CMD_0001` |
| `HED-CMD-0002` | `HED_CMD_0002` |

## HED-COMPAT

| Code | Catalog symbol |
|---|---|
| `HED-COMPAT-0001` | `HED_COMPAT_0001` |
| `HED-COMPAT-0002` | `HED_COMPAT_0002` |
| `HED-COMPAT-0003` | `HED_COMPAT_0003` |

## HED-CONC

| Code | Catalog symbol |
|---|---|
| `HED-CONC-0001` | `HED_CONC_0001` |

## HED-CONFIG

| Code | Catalog symbol |
|---|---|
| `HED-CONFIG-0001` | `HED_CONFIG_UNKNOWN_KEY` |
| `HED-CONFIG-0002` | `HED_CONFIG_UNSUPPORTED_VERSION` |
| `HED-CONFIG-0003` | `HED_CONFIG_INVALID` |

## HED-CONTENT

| Code | Catalog symbol |
|---|---|
| `HED-CONTENT-0001` | `HED_CONTENT_0001` |
| `HED-CONTENT-0002` | `HED_CONTENT_0002` |
| `HED-CONTENT-0003` | `HED_CONTENT_0003` |
| `HED-CONTENT-0004` | `HED_CONTENT_0004` |
| `HED-CONTENT-0005` | `HED_CONTENT_0005` |
| `HED-CONTENT-0006` | `HED_CONTENT_0006` |
| `HED-CONTENT-0007` | `HED_CONTENT_0007` |

## HED-CSS

| Code | Catalog symbol |
|---|---|
| `HED-CSS-0001` | `HED_CSS_UNSUPPORTED_VERSION` |
| `HED-CSS-0002` | `HED_CSS_PARSE` |
| `HED-CSS-0003` | `HED_CSS_UNKNOWN_SYMBOL` |
| `HED-CSS-0004` | `HED_CSS_UNSAFE_GLOBAL` |
| `HED-CSS-0005` | `HED_CSS_REMOTE` |
| `HED-CSS-0006` | `HED_CSS_INLINE` |
| `HED-CSS-0007` | `HED_CSS_DUPLICATE` |
| `HED-CSS-0008` | `HED_CSS_UNUSED` |
| `HED-CSS-0009` | `HED_CSS_APPLICATION_AUTHORED` |

## HED-DATA

| Code | Catalog symbol |
|---|---|
| `HED-DATA-0001` | `HED_DATA_0001` |
| `HED-DATA-0002` | `HED_DATA_0002` |
| `HED-DATA-0003` | `HED_DATA_0003` |
| `HED-DATA-0004` | `HED_DATA_0004` |
| `HED-DATA-0005` | `HED_DATA_0005` |
| `HED-DATA-0006` | `HED_DATA_0006` |
| `HED-DATA-0010` | `HED_DATA_0010` |
| `HED-DATA-0011` | `HED_DATA_0011` |
| `HED-DATA-0012` | `HED_DATA_0012` |
| `HED-DATA-0013` | `HED_DATA_0013` |
| `HED-DATA-0020` | `HED_DATA_0020` |
| `HED-DATA-0025` | `HED_DATA_0025` |
| `HED-DATA-0026` | `HED_DATA_0026` |
| `HED-DATA-0027` | `HED_DATA_0027` |
| `HED-DATA-0030` | `HED_DATA_0030` |
| `HED-DATA-0031` | `HED_DATA_0031` |
| `HED-DATA-0032` | `HED_DATA_0032` |
| `HED-DATA-0033` | `HED_DATA_0033` |
| `HED-DATA-0034` | `HED_DATA_0034` |
| `HED-DATA-0040` | `HED_DATA_0040` |
| `HED-DATA-0041` | `HED_DATA_0041` |
| `HED-DATA-0050` | `HED_DATA_0050` |
| `HED-DATA-0051` | `HED_DATA_0051` |
| `HED-DATA-0060` | `HED_DATA_0060` |
| `HED-DATA-0061` | `HED_DATA_0061` |

## HED-DEMO

| Code | Catalog symbol |
|---|---|
| `HED-DEMO-0001` | `HED_DEMO_0001` |
| `HED-DEMO-0002` | `HED_DEMO_0002` |
| `HED-DEMO-0003` | `HED_DEMO_0003` |

## HED-FEEDBACK

| Code | Catalog symbol |
|---|---|
| `HED-FEEDBACK-0001` | `HED_FEEDBACK_0001` |

## HED-GRAPH

| Code | Catalog symbol |
|---|---|
| `HED-GRAPH-0001` | `HED_GRAPH_0001` |
| `HED-GRAPH-0002` | `HED_GRAPH_0002` |
| `HED-GRAPH-0003` | `HED_GRAPH_0003` |
| `HED-GRAPH-0004` | `HED_GRAPH_0004` |
| `HED-GRAPH-0005` | `HED_GRAPH_0005` |
| `HED-GRAPH-0006` | `HED_GRAPH_0006` |

## HED-HDJ

| Code | Catalog symbol |
|---|---|
| `HED-HDJ-0100` | `HED_HDJ_0100` |
| `HED-HDJ-0110` | `HED_HDJ_0110` |
| `HED-HDJ-0111` | `HED_HDJ_0111` |
| `HED-HDJ-0112` | `HED_HDJ_0112` |

## HED-HOST

| Code | Catalog symbol |
|---|---|
| `HED-HOST-0001` | `HED_HOST_0001` |

## HED-HTML

| Code | Catalog symbol |
|---|---|
| `HED-HTML-0001` | `HED_HTML_0001` |
| `HED-HTML-0002` | `HED_HTML_0002` |
| `HED-HTML-0003` | `HED_HTML_0003` |
| `HED-HTML-0004` | `HED_HTML_0004` |
| `HED-HTML-0005` | `HED_HTML_0005` |
| `HED-HTML-0006` | `HED_HTML_0006` |

## HED-HTMX

| Code | Catalog symbol |
|---|---|
| `HED-HTMX-0001` | `HED_HTMX_0001` |
| `HED-HTMX-0002` | `HED_HTMX_0002` |

## HED-EXT

| Code | Catalog symbol |
|---|---|
| `HED-EXT-0001` | `HED_EXT_0001` |
| `HED-EXT-0002` | `HED_EXT_0002` |
| `HED-EXT-0003` | `HED_EXT_0003` |
| `HED-EXT-0004` | `HED_EXT_0004` |
| `HED-EXT-0005` | `HED_EXT_0005` |
| `HED-EXT-0006` | `HED_EXT_0006` |
| `HED-EXT-0007` | `HED_EXT_0007` |
| `HED-EXT-0008` | `HED_EXT_0008` |
| `HED-EXT-0009` | `HED_EXT_0009` |
| `HED-EXT-0010` | `HED_EXT_0010` |
| `HED-EXT-0011` | `HED_EXT_0011` |

## HED-FP (0.49)

FastAPI/Pydantic convergence diagnostics (D-081 / D-084 / RFC-0076). Do not reuse
`HED-TYPE-0001`–`0010`. Public contract:
[FastAPI/Pydantic convergence](../api/FASTAPI_PYDANTIC_CONVERGENCE.md).

| Code | Catalog symbol |
|---|---|
| `HED-FP-0001` | `HED_FP_0001` |
| `HED-FP-0002` | `HED_FP_0002` |
| `HED-FP-0003` | `HED_FP_0003` |
| `HED-FP-0004` | `HED_FP_0004` |
| `HED-FP-0005` | `HED_FP_0005` |
| `HED-FP-0006` | `HED_FP_0006` |
| `HED-FP-0007` | `HED_FP_0007` |
| `HED-FP-0008` | `HED_FP_0008` |

## HED-ICON

| Code | Catalog symbol |
|---|---|
| `HED-ICON-0001` | `HED_ICON_0001` |
| `HED-ICON-0002` | `HED_ICON_0002` |
| `HED-ICON-0003` | `HED_ICON_0003` |
| `HED-ICON-0004` | `HED_ICON_0004` |

## HED-INFER

| Code | Catalog symbol |
|---|---|
| `HED-INFER-0001` | `HED_INFER_0001` |
| `HED-INFER-0002` | `HED_INFER_0002` |
| `HED-INFER-0003` | `HED_INFER_0003` |

## HED-JINJA

| Code | Catalog symbol |
|---|---|
| `HED-JINJA-0002` | `HED_JINJA_0002` |
| `HED-JINJA-0003` | `HED_JINJA_0003` |
| `HED-JINJA-0004` | `HED_JINJA_0004` |
| `HED-JINJA-0005` | `HED_JINJA_0005` |
| `HED-JINJA-0006` | `HED_JINJA_0006` |
| `HED-JINJA-0007` | `HED_JINJA_0007` |
| `HED-JINJA-0008` | `HED_JINJA_0008` |
| `HED-JINJA-0009` | `HED_JINJA_0009` |
| `HED-JINJA-0010` | `HED_JINJA_0010` |
| `HED-JINJA-0012` | `HED_JINJA_0012` |
| `HED-JINJA-0013` | `HED_JINJA_0013` |
| `HED-JINJA-0014` | `HED_JINJA_0014` |
| `HED-JINJA-0015` | `HED_JINJA_0015` |
| `HED-JINJA-0017` | `HED_JINJA_0017` |
| `HED-JINJA-0018` | `HED_JINJA_0018` |
| `HED-JINJA-0019` | `HED_JINJA_0019` |
| `HED-JINJA-0020` | `HED_JINJA_0020` |
| `HED-JINJA-0021` | `HED_JINJA_0021` |
| `HED-JINJA-0022` | `HED_JINJA_0022` |
| `HED-JINJA-0023` | `HED_JINJA_0023` |
| `HED-JINJA-0024` | `HED_JINJA_0024` |
| `HED-JINJA-0025` | `HED_JINJA_0025` |
| `HED-JINJA-0026` | `HED_JINJA_0026` |
| `HED-JINJA-0027` | `HED_JINJA_0027` |
| `HED-JINJA-0030` | `HED_JINJA_0030` |
| `HED-JINJA-0031` | `HED_JINJA_0031` |
| `HED-JINJA-0032` | `HED_JINJA_0032` |
| `HED-JINJA-0033` | `HED_JINJA_0033` |

## HED-JOB

| Code | Catalog symbol |
|---|---|
| `HED-JOB-0001` | `HED_JOB_0001` |

## HED-MAP

Shipped core map/GeoJSON codes (`HED-MAP-0001`–`0004`) remain the 0.15 compatibility surface.
Phase 0.47 assigns the following families:

| Code | Catalog symbol |
|---|---|
| `HED-MAP-0001` | `HED_MAP_0001` |
| `HED-MAP-0002` | `HED_MAP_0002` |
| `HED-MAP-0003` | `HED_MAP_0003` |
| `HED-MAP-0004` | `HED_MAP_0004` |
| `HED-MAP-SPEC-0001` | `HED_MAP_SPEC_0001` |
| `HED-MAP-SPEC-0002` | `HED_MAP_SPEC_0002` |
| `HED-MAP-SPEC-0003` | `HED_MAP_SPEC_0003` |
| `HED-MAP-SPEC-0004` | `HED_MAP_SPEC_0004` |
| `HED-MAP-SOURCE-0001` | `HED_MAP_SOURCE_0001` |
| `HED-MAP-SOURCE-0002` | `HED_MAP_SOURCE_0002` |
| `HED-MAP-SOURCE-0003` | `HED_MAP_SOURCE_0003` |
| `HED-MAP-POLICY-0001` | `HED_MAP_POLICY_0001` |
| `HED-MAP-POLICY-0002` | `HED_MAP_POLICY_0002` |
| `HED-MAP-STYLE-0001` | `HED_MAP_STYLE_0001` |
| `HED-MAP-STYLE-0002` | `HED_MAP_STYLE_0002` |
| `HED-MAP-OFFLINE-0001` | `HED_MAP_OFFLINE_0001` |
| `HED-MAP-OFFLINE-0002` | `HED_MAP_OFFLINE_0002` |
| `HED-MAP-OFFLINE-0003` | `HED_MAP_OFFLINE_0003` |
| `HED-MAP-RUNTIME-0001` | `HED_MAP_RUNTIME_0001` |
| `HED-MAP-RUNTIME-0002` | `HED_MAP_RUNTIME_0002` |
| `HED-MAP-RUNTIME-0003` | `HED_MAP_RUNTIME_0003` |
| `HED-MAP-EVENT-0001` | `HED_MAP_EVENT_0001` |
| `HED-MAP-EVENT-0002` | `HED_MAP_EVENT_0002` |
| `HED-MAP-EVENT-0003` | `HED_MAP_EVENT_0003` |

## HED-MODEL

| Code | Catalog symbol |
|---|---|
| `HED-MODEL-0001` | `HED_MODEL_0001` |
| `HED-MODEL-0002` | `HED_MODEL_0002` |
| `HED-MODEL-0003` | `HED_MODEL_0003` |
| `HED-MODEL-0004` | `HED_MODEL_0004` |
| `HED-MODEL-0005` | `HED_MODEL_0005` |
| `HED-MODEL-0006` | `HED_MODEL_0006` |

## HED-PATCH

| Code | Catalog symbol |
|---|---|
| `HED-PATCH-0001` | `HED_PATCH_0001` |
| `HED-PATCH-0002` | `HED_PATCH_0002` |
| `HED-PATCH-0003` | `HED_PATCH_0003` |
| `HED-PATCH-0004` | `HED_PATCH_0004` |

## HED-PLUGIN

| Code | Catalog symbol |
|---|---|
| `HED-PLUGIN-0001` | `HED_PLUGIN_MISSING` |
| `HED-PLUGIN-0002` | `HED_PLUGIN_INCOMPATIBLE` |
| `HED-PLUGIN-0003` | `HED_PLUGIN_CYCLE` |
| `HED-PLUGIN-0004` | `HED_PLUGIN_DUPLICATE` |
| `HED-PLUGIN-0005` | `HED_PLUGIN_FAILED` |

## HED-EXPLORER

| Code | Catalog symbol |
|---|---|
| `HED-EXPLORER-0001` | `HED_EXPLORER_0001` |
| `HED-EXPLORER-0002` | `HED_EXPLORER_0002` |
| `HED-EXPLORER-0003` | `HED_EXPLORER_0003` |

## HED-CAP

| Code | Catalog symbol |
|---|---|
| `HED-CAP-0001` | `HED_CAP_0001` |

## HED-REPLAY

| Code | Catalog symbol |
|---|---|
| `HED-REPLAY-0001` | `HED_REPLAY_0001` |
| `HED-REPLAY-0002` | `HED_REPLAY_0002` |
| `HED-REPLAY-0003` | `HED_REPLAY_0003` |
| `HED-REPLAY-0004` | `HED_REPLAY_0004` |

## HED-UPGRADE

| Code | Catalog symbol |
|---|---|
| `HED-UPGRADE-0001` | `HED_UPGRADE_0001` |
| `HED-UPGRADE-0002` | `HED_UPGRADE_0002` |
| `HED-UPGRADE-1001` | `HED_UPGRADE_1001` |
| `HED-UPGRADE-1002` | `HED_UPGRADE_1002` |

## HED-PREPARE

| Code | Catalog symbol |
|---|---|
| `HED-PREPARE-0001` | `HED_PREPARE_0001` |
| `HED-PREPARE-0002` | `HED_PREPARE_0002` |
| `HED-PREPARE-0003` | `HED_PREPARE_0003` |

## HED-RENDER

| Code | Catalog symbol |
|---|---|
| `HED-RENDER-0001` | `HED_RENDER_0001` |
| `HED-RENDER-0002` | `HED_RENDER_0002` |
| `HED-RENDER-0003` | `HED_RENDER_0003` |
| `HED-RENDER-0004` | `HED_RENDER_0004` |
| `HED-RENDER-0005` | `HED_RENDER_0005` |
| `HED-RENDER-0006` | `HED_RENDER_0006` |
| `HED-RENDER-0007` | `HED_RENDER_0007` |
| `HED-RENDER-0008` | `HED_RENDER_0008` |
| `HED-RENDER-0009` | `HED_RENDER_0009` |
| `HED-RENDER-0010` | `HED_RENDER_0010` |
| `HED-RENDER-0011` | `HED_RENDER_0011` |
| `HED-RENDER-0012` | `HED_RENDER_0012` |
| `HED-RENDER-0013` | `HED_RENDER_0013` |
| `HED-RENDER-0014` | `HED_RENDER_0014` |

## HED-ROUTE

| Code | Catalog symbol |
|---|---|
| `HED-ROUTE-0001` | `HED_ROUTE_0001` |

## HED-SEC

| Code | Catalog symbol |
|---|---|
| `HED-SEC-0001` | `HED_SEC_0001` |
| `HED-SEC-0002` | `HED_SEC_0002` |
| `HED-SEC-0003` | `HED_SEC_0003` |
| `HED-SEC-0004` | `HED_SEC_0004` |
| `HED-SEC-0005` | `HED_SEC_0005` |
| `HED-SEC-0006` | `HED_SEC_0006` |
| `HED-SEC-0007` | `HED_SEC_0007` |
| `HED-SEC-0008` | `HED_SEC_0008` |
| `HED-SEC-0009` | `HED_SEC_0009` |
| `HED-SEC-0010` | `HED_SEC_0010` |
| `HED-SEC-0011` | `HED_SEC_0011` |

| `HED-ELEMENT-0001` | blocker | Element tag/definition conflict | Align definitions or choose a new tag/logical id |
| `HED-ELEMENT-0002` | blocker | Incompatible element ABI pair | Align markup/module ABI majors |
| `HED-ELEMENT-0003` | blocker | First-party naming / prefix violation | Use `hedron-*` for first-party tags |
| `HED-ELEMENT-0005` | blocker | Structured input bound/encoding failure | Reduce payload size/depth |
| `HED-ELEMENT-ASSET-0001` | blocker | Packaged element asset path escape | Pass a single basename under `static/` |
| `HED-ELEMENT-ASSET-0002` | blocker | Packaged element asset missing | Use a filename that ships in the package |
| `HED-ELEMENT-AUTHOR-0001` | blocker | Incomplete third-party author metadata | Declare every required author metadata surface |
| `HED-ELEMENT-AUTHOR-0002` | blocker | Invalid author tag or a11y contract | Use a hyphenated tag and mapping `a11y_contract` |
| `HED-ELEMENT-STATE-0002` | blocker | Illegal element-owned capability | Keep capabilities server-controlled |
| `HED-ELEMENT-STATE-0006` | blocker | Draft transfer before 0.41 | Keep drafts instance-local |
| `HED-SIM-ASSET-0001` | blocker | Packaged sim asset path escape | Pass a single basename under `static/` |
| `HED-SIM-ASSET-0002` | blocker | Packaged sim asset missing | Use a filename that ships in `hedron_sim/static/` |
| `HED-SEC-0020` | `HED_SEC_0020` |

## HED-A11Y

| Code | Catalog symbol |
|---|---|
| `HED-A11Y-0001` | `HED_A11Y_0001` |
| `HED-A11Y-0010` | `HED_A11Y_0010` |
| `HED-A11Y-0011` | `HED_A11Y_0011` |
| `HED-A11Y-0012` | `HED_A11Y_0012` |

## HED-THEME

| Code | Catalog symbol |
|---|---|
| `HED-THEME-0001` | `HED_THEME_UNKNOWN` |
| `HED-THEME-0002` | `HED_THEME_MISSING_TOKEN` |
| `HED-THEME-0003` | `HED_THEME_INVALID` |
| `HED-THEME-0004` | `HED_THEME_DUPLICATE` |
| `HED-THEME-0005` | `HED_THEME_STYLE_CONTRACT` |
| `HED-THEME-0006` | `HED_THEME_ELEMENT_TOKEN` |
| `HED-THEME-0007` | `HED_THEME_CONTRAST` |

## HED-TRACE

| Code | Catalog symbol |
|---|---|
| `HED-TRACE-0001` | `HED_TRACE_0001` |

## HED-UPDATE

| Code | Catalog symbol |
|---|---|
| `HED-UPDATE-0001` | `HED_UPDATE_0001` |
| `HED-UPDATE-0002` | `HED_UPDATE_0002` |
| `HED-UPDATE-0003` | `HED_UPDATE_0003` |
| `HED-UPDATE-0004` | `HED_UPDATE_0004` |
| `HED-UPDATE-0005` | `HED_UPDATE_0005` |
| `HED-UPDATE-0006` | `HED_UPDATE_0006` |
| `HED-UPDATE-0007` | `HED_UPDATE_0007` |
| `HED-UPDATE-0008` | `HED_UPDATE_0008` |
| `HED-UPDATE-0009` | `HED_UPDATE_0009` |

## HED-VIEW

| Code | Catalog symbol |
|---|---|
| `HED-VIEW-0001` | `HED_VIEW_0001` |
| `HED-VIEW-0002` | `HED_VIEW_0002` |
| `HED-VIEW-0003` | `HED_VIEW_0003` |
| `HED-VIEW-0004` | `HED_VIEW_0004` |

## HED-WB

| Code | Catalog symbol |
|---|---|
| `HED-WB-0001` | `HED_WB_0001` |
| `HED-WB-0002` | `HED_WB_0002` |
| `HED-WB-0003` | `HED_WB_0003` |
| `HED-WB-0004` | `HED_WB_0004` |
| `HED-WB-0005` | `HED_WB_0005` |
| `HED-WB-0006` | `HED_WB_0006` |
| `HED-WB-0007` | `HED_WB_0007` |
| `HED-WB-0008` | `HED_WB_0008` |
| `HED-WB-0009` | `HED_WB_0009` |

## HED-POSIT

Unified Posit Workbench / Connect adapter (RFC-0066 / 0.33).

| Code | Catalog symbol |
|---|---|
| `HED-POSIT-0101` | `HED_POSIT_0101` |
| `HED-POSIT-0301` | `HED_POSIT_0301` |
| `HED-POSIT-0302` | `HED_POSIT_0302` |
| `HED-POSIT-0303` | `HED_POSIT_0303` |
| `HED-POSIT-0304` | `HED_POSIT_0304` |
| `HED-POSIT-0401` | `HED_POSIT_0401` |
| `HED-POSIT-0508` | `HED_POSIT_0508` |
| `HED-POSIT-0512` | `HED_POSIT_0512` |
| `HED-POSIT-0513` | `HED_POSIT_0513` |
| `HED-POSIT-0514` | `HED_POSIT_0514` |
| `HED-POSIT-0515` | `HED_POSIT_0515` |
| `HED-POSIT-0516` | `HED_POSIT_0516` |

## HED-ELEMENT

Web Component element ABI, author kit, and packaged assets (RFC-0060).

| Code | Catalog symbol |
|---|---|
| `HED-ELEMENT-0001` | `HED_ELEMENT_0001` |
| `HED-ELEMENT-0002` | `HED_ELEMENT_0002` |
| `HED-ELEMENT-0003` | `HED_ELEMENT_0003` |
| `HED-ELEMENT-0004` | `HED_ELEMENT_0004` |
| `HED-ELEMENT-0005` | `HED_ELEMENT_0005` |
| `HED-ELEMENT-0006` | `HED_ELEMENT_0006` |
| `HED-ELEMENT-0007` | `HED_ELEMENT_0007` |
| `HED-ELEMENT-ASSET-0001` | `HED_ELEMENT_ASSET_0001` |
| `HED-ELEMENT-ASSET-0002` | `HED_ELEMENT_ASSET_0002` |
| `HED-ELEMENT-AUTHOR-0001` | `HED_ELEMENT_AUTHOR_0001` |
| `HED-ELEMENT-AUTHOR-0002` | `HED_ELEMENT_AUTHOR_0002` |
| `HED-ELEMENT-STATE-0001` | `HED_ELEMENT_STATE_0001` |
| `HED-ELEMENT-STATE-0002` | `HED_ELEMENT_STATE_0002` |
| `HED-ELEMENT-STATE-0003` | `HED_ELEMENT_STATE_0003` |
| `HED-ELEMENT-STATE-0004` | `HED_ELEMENT_STATE_0004` |
| `HED-ELEMENT-STATE-0005` | `HED_ELEMENT_STATE_0005` |
| `HED-ELEMENT-STATE-0006` | `HED_ELEMENT_STATE_0006` |

## HED-SIM

Docs simulation packaged assets.

| Code | Catalog symbol |
|---|---|
| `HED-SIM-ASSET-0001` | `HED_SIM_ASSET_0001` |
| `HED-SIM-ASSET-0002` | `HED_SIM_ASSET_0002` |

## HED-MIG-ST

Streamlit AST migrator findings (RFC-0061 / `MIGRATE-031`).

| Code | Catalog symbol |
|---|---|
| `HED-MIG-ST-0001` | `HED_MIG_ST_0001` |
| `HED-MIG-ST-0002` | `HED_MIG_ST_0002` |
| `HED-MIG-ST-0003` | `HED_MIG_ST_0003` |
| `HED-MIG-ST-0004` | `HED_MIG_ST_0004` |
| `HED-MIG-ST-0005` | `HED_MIG_ST_0005` |
| `HED-MIG-ST-0006` | `HED_MIG_ST_0006` |
| `HED-MIG-ST-0007` | `HED_MIG_ST_0007` |
| `HED-MIG-ST-0008` | `HED_MIG_ST_0008` |
| `HED-MIG-ST-0009` | `HED_MIG_ST_0009` |
| `HED-MIG-ST-0010` | `HED_MIG_ST_0010` |
| `HED-MIG-ST-0011` | `HED_MIG_ST_0011` |
| `HED-MIG-ST-0012` | `HED_MIG_ST_0012` |
| `HED-MIG-ST-0013` | `HED_MIG_ST_0013` |
| `HED-MIG-ST-0014` | `HED_MIG_ST_0014` |

## HED-TYPE (0.44)

Type-driven authoring diagnostics (D-072 / D-076 / RFC-0071). Public contract:
[Type-driven authoring](../api/TYPE_DRIVEN_AUTHORING.md). `HED-TYPE-BIND-SOURCE` is the
mnemonic alias of `HED-TYPE-0001`.

| Code | Catalog symbol |
|---|---|
| `HED-TYPE-0001` | `HED_TYPE_0001` / `HED_TYPE_BIND_SOURCE` |
| `HED-TYPE-0002` | `HED_TYPE_0002` |
| `HED-TYPE-0003` | `HED_TYPE_0003` |
| `HED-TYPE-0004` | `HED_TYPE_0004` |
| `HED-TYPE-0005` | `HED_TYPE_0005` |
| `HED-TYPE-0006` | `HED_TYPE_0006` |
| `HED-TYPE-0007` | `HED_TYPE_0007` |
| `HED-TYPE-0008` | `HED_TYPE_0008` |
| `HED-TYPE-0009` | `HED_TYPE_0009` |
| `HED-TYPE-0010` | `HED_TYPE_0010` |

## HED-CATALOG (0.45)

Interaction catalog and sealed-manifest diagnostics (D-074 / D-077 / RFC-0072). Public
contract: [Interaction catalog](../api/INTERACTION_CATALOG.md).

| Code | Catalog symbol |
|---|---|
| `HED-CATALOG-0001` | `HED_CATALOG_0001` |
| `HED-CATALOG-0002` | `HED_CATALOG_0002` |
| `HED-CATALOG-0003` | `HED_CATALOG_0003` |
| `HED-CATALOG-0004` | `HED_CATALOG_0004` |
| `HED-CATALOG-0005` | `HED_CATALOG_0005` |
| `HED-CATALOG-0006` | `HED_CATALOG_0006` |
| `HED-CATALOG-0007` | `HED_CATALOG_0007` |
| `HED-CATALOG-0008` | `HED_CATALOG_0008` |

## HED-PROJECTION (0.45)

Namespaced package projection diagnostics. Registration and catalog presence never
grant remote exposure.

| Code | Catalog symbol |
|---|---|
| `HED-PROJECTION-0001` | `HED_PROJECTION_0001` |
| `HED-PROJECTION-0002` | `HED_PROJECTION_0002` |
| `HED-PROJECTION-0003` | `HED_PROJECTION_0003` |
| `HED-PROJECTION-0004` | `HED_PROJECTION_0004` |
| `HED-PROJECTION-0005` | `HED_PROJECTION_0005` |
| `HED-PROJECTION-0006` | `HED_PROJECTION_0006` |

## HED-BUNDLE (0.46)

Atomic FeatureBundle inclusion diagnostics (D-075 / D-079 / RFC-0073). Public
contract: [Package-native workflows](../api/PACKAGE_WORKFLOWS.md). Never reuse
`HED-WORKFLOW-*`, `HED-CATALOG-*`, or `HED-PROJECTION-*` for bundle failures.

| Code | Catalog symbol |
|---|---|
| `HED-BUNDLE-0001` | `HED_BUNDLE_0001` |
| `HED-BUNDLE-0002` | `HED_BUNDLE_0002` |
| `HED-BUNDLE-0003` | `HED_BUNDLE_0003` |
| `HED-BUNDLE-0004` | `HED_BUNDLE_0004` |
| `HED-BUNDLE-0005` | `HED_BUNDLE_0005` |
| `HED-BUNDLE-0006` | `HED_BUNDLE_0006` |
| `HED-BUNDLE-0007` | `HED_BUNDLE_0007` |
| `HED-BUNDLE-0008` | `HED_BUNDLE_0008` |
| `HED-BUNDLE-0009` | `HED_BUNDLE_0009` |
| `HED-BUNDLE-0010` | `HED_BUNDLE_0010` |

## HED-WORKFLOW

| Code | Catalog symbol |
|---|---|
| `HED-WORKFLOW-0001` | `HED_WORKFLOW_0001` |
| `HED-WORKFLOW-0002` | `HED_WORKFLOW_0002` |
| `HED-WORKFLOW-0003` | `HED_WORKFLOW_0003` |

## Related HTTP statuses (not `HED-*`)

| Status | Common cause |
|---|---|
| 403 | Undeclared HTMX target / region authz (`HED-HTMX-0001`) |
| 422 | Validation failure |
