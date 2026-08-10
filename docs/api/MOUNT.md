# Mount / path prefix

!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).
    Mount helpers are part of the production security floor (0.20+) and remain on the
    living **0.26** train. Package maturity remains **Beta** — pin versions.

**Status:** Shipped · public exports from `hedron`

When a reverse proxy serves your app under a subpath (for example `/apps/hedron`),
session/CSRF cookie `Path`, local redirects, and HTMX URLs must share one trusted mount.
These helpers resolve that mount and keep cookie paths consistent.

## Quick start (operator)

1. Configure the proxy to strip or forward the prefix consistently.
2. Set ASGI `root_path` (uvicorn `--root-path /apps/hedron`) **or** set
   `HEDRON_ROOT_PATH=/apps/hedron`.
3. Confirm CSRF cookies use `Path=/apps/hedron` (not `/` alone) and that Refresh /
   form posts still hit the app.

See [Deployment](../guides/deployment.md) · [Ship a Hedron app](../guides/ship.md) ·
[Troubleshooting](../guides/troubleshooting.md).

## Trust order

`resolve_mount_path` / `mount_from_request` use this order:

1. **`HEDRON_ROOT_PATH`** (operator override) when `prefer_env` is true
2. **ASGI `root_path`** when present
3. **Allowlisted peer + prefix header** (`X-Forwarded-Prefix` by default) — ignored unless
   the peer is in `trusted_peers`
4. Otherwise **site root** (`""`)

Untrusted forwarded headers are ignored by default (fail closed for spoofed prefixes).

`normalize_mount_path` also rejects path segments of `.` / `..` (including percent-encoded `%2e` forms) so cookie `Path` and redirect prefixes cannot escape the intended mount. Prefixed local URLs are re-checked with `is_local_path`.

## Parameters / Returns

| Helper | Parameters (summary) | Returns |
|---|---|---|
| `normalize_mount_path(value)` | raw mount string | `str` (`""` or `/prefix`) |
| `cookie_path_for_mount(mount)` | normalized mount | cookie `Path` string |
| `prefix_local_path(url, mount)` | local URL + mount | prefixed local path |
| `resolve_mount_path(...)` | `root_path`, `headers`, `peer`, `trusted_peers`, … | `MountPath` |
| `mount_from_request(request, …)` | Starlette/FastAPI request | `MountPath` |

## API

### `MountPath`

| Field / property | Type | Description |
|---|---|---|
| `path` | `str` | Normalized mount (`""` at site root, or `/prefix` with no trailing slash) |
| `source` | `str` | Where the value came from (`env:HEDRON_ROOT_PATH`, `asgi:root_path`, …) |
| `cookie_path` | `str` | Cookie `Path` (`/` at root, `/prefix` under a mount; no forced trailing slash so `/prefix` matches both `/prefix` and `/prefix/...`) |

### `normalize_mount_path(value) -> str`

Normalize to `""` or `/prefix` (no trailing slash).

### `cookie_path_for_mount(mount) -> str`

Return cookie `Path` for a mount.

### `prefix_local_path(url, mount) -> str`

Prefix a local absolute path with `mount` once (no double-prefix). Leaves non-local /
protocol-relative URLs unchanged.

### `resolve_mount_path(*, root_path=None, headers=None, peer=None, trusted_peers=None, prefix_headers=("x-forwarded-prefix",), environ=None, prefer_env=True) -> MountPath`

Resolve the external mount using the trust order above.

| Parameter | Description |
|---|---|
| `root_path` | ASGI `root_path` |
| `headers` | Request headers (for prefix header lookup) |
| `peer` | Client peer address string |
| `trusted_peers` | Peers allowed to supply prefix headers |
| `prefix_headers` | Header names to read when peer is trusted |
| `environ` | Optional environ mapping (defaults to `os.environ`) |
| `prefer_env` | When true, honor `HEDRON_ROOT_PATH` first |

### `resolve_mount_path_from_environ(*, environ=None) -> MountPath | None`

Read `HEDRON_ROOT_PATH` when set; otherwise `None`.

### `mount_from_request(request, *, trusted_peers=None) -> MountPath`

Resolve from a Starlette/FastAPI request (`scope["root_path"]`, headers, client peer).

## Example

```python
import os

from hedron import Hedron, mount_from_request, prefix_local_path

# Operator override for a reverse-proxy subpath:
os.environ.setdefault("HEDRON_ROOT_PATH", "/apps/hedron")

app = Hedron(
    title="Mounted",
    security="standard",
    explorer="off",
    session_secret=os.environ["HEDRON_SESSION_SECRET"],
)


@app.page("/")
def home(request):
    mount = mount_from_request(request)
    # Local redirect / HTMX href under the same mount:
    href = prefix_local_path("/status", mount.path)
    ...
```

## Errors

| Situation | Behavior |
|---|---|
| Missing mount config under a subpath | Cookies/redirects use site root — Refresh/CSRF appear broken behind the proxy |
| Spoofed `X-Forwarded-Prefix` from untrusted peer | Ignored; mount falls back to env / ASGI / root |
| Double-prefixed local paths | `prefix_local_path` avoids re-prefixing when already under the mount |
| Protocol-relative / absolute URL / backslash mount values | Rejected at normalize / resolve (fail closed) |

## See also

- Autodoc: [AUTODOC.md](AUTODOC.md) (when listed)
- [Configuration](../CONFIGURATION.md) (`HEDRON_ROOT_PATH`)
- [Security](../guides/security.md)
