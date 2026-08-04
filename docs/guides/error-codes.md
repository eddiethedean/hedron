# Error codes

Stable `HED-*` diagnostics from `hedron_core.codes`. Prefer these codes in CI and
support reports. Full format: [Diagnostics](https://github.com/eddiethedean/hedron/blob/main/docs/DIAGNOSTICS.md).

## Config

| Code | Meaning |
|---|---|
| `HED-CONFIG-0001` | Unknown configuration key |
| `HED-CONFIG-0002` | Unsupported configuration version |
| `HED-CONFIG-0003` | Invalid configuration value |

## Build / production gate

| Code | Meaning | Typical fix |
|---|---|---|
| `HED-BUILD-0001` | Unsupported build artifact version | Rebuild with matching Hedron |
| `HED-BUILD-0002` | Build failed | Inspect CLI output; fix assets/CSS |
| `HED-BUILD-0003` | Missing `manifest.json` in production | Run `hedron build` before `HEDRON_ENV=production` |
| `HED-BUILD-0004` | Runtime CSS compile blocked in production | Use build-time CSS; do not compile at runtime |

## Assets

| Code | Meaning |
|---|---|
| `HED-ASSET-0001` | Unsupported asset manifest version |
| `HED-ASSET-0002` | Path traversal rejected |
| `HED-ASSET-0003` | Remote asset URL rejected by policy |
| `HED-ASSET-0004` | Asset missing |
| `HED-ASSET-0005` | Asset id collision |
| `HED-ASSET-0006` | Symlink rejected |
| `HED-ASSET-0007` | Disallowed MIME type |
| `HED-ASSET-0010` | Duplicate browser / Web Component registration |
| `HED-ASSET-0011` | Invalid browser asset registration |

## CSS

| Code | Meaning |
|---|---|
| `HED-CSS-0001` | Unsupported CSS pipeline version |
| `HED-CSS-0002` | CSS parse failure |
| `HED-CSS-0003` | Unknown style symbol |
| `HED-CSS-0004` | Unsafe global CSS rejected |
| `HED-CSS-0005` | Remote CSS rejected |
| `HED-CSS-0006` | Inline CSS rejected by policy |
| `HED-CSS-0007` | Duplicate CSS registration |
| `HED-CSS-0008` | Unused CSS warning / gate |

## Themes

| Code | Meaning |
|---|---|
| `HED-THEME-0001` | Unknown theme |
| `HED-THEME-0002` | Missing required theme token |
| `HED-THEME-0003` | Invalid theme definition |
| `HED-THEME-0004` | Duplicate theme registration |

## Plugins

| Code | Meaning |
|---|---|
| `HED-PLUGIN-0001` | Plugin missing / not found |
| `HED-PLUGIN-0002` | Incompatible `hedron_version` |
| `HED-PLUGIN-0003` | Plugin dependency cycle |
| `HED-PLUGIN-0004` | Duplicate plugin registration |
| `HED-PLUGIN-0005` | Plugin `register()` failed |

## Models / Field

| Code | Meaning |
|---|---|
| `HED-MODEL-0001` | Contradictory field metadata |
| `HED-MODEL-0002` | Unsupported `Field` option |
| `HED-MODEL-0003`+ | Additional model diagnostics (see source / diagnostics payload) |

## Related HTTP statuses (not `HED-*`)

| Status | Common cause |
|---|---|
| `403` | CSRF failure or HTMX target outside `fragment_regions` |
| `401` | Application auth dependency rejected the request |
| `422` | Validation failure on typed action/form input |

See [Troubleshooting](troubleshooting.md) · [Deployment](deployment.md).
