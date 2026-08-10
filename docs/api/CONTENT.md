---
status: shipped
---

# Content extras


!!! note "Stability"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md).
    Package maturity (Beta/Alpha) is separate from API level
    (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Shipped in `0.6.0`

Optional content helpers live in `hedron.content` (lazy imports; missing extras raise
diagnostics with exact install commands).

## `Markdown`

```bash
pip install "hedron[markdown]>=0.27.0,<0.28"
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| body (positional / children) | `str` | required | Markdown source |
| (props) | — | — | See component page / Autodoc |

```python
from hedron import Markdown

Markdown("# Hello\n\nSupports **fenced code** and tables.")
```

Rendered Markdown is sanitized through `TrustedHtml.nh3` before `html.raw`. Install
`hedron[sanitize]` (or rely on the markdown extra's dependency chain) so nh3 is available.

## `highlight_code`

```bash
pip install "hedron[code]>=0.27.0,<0.28"
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `code` | `str` | required | Source text |
| `lexer` | `str` | `"python"` | Pygments lexer name |

**Returns:** `TrustedHtml` (sanitized highlighted markup).

```python
from hedron import highlight_code
from hedron_core.html import html

trusted = highlight_code("print('hi')", lexer="python")
node = html.div(html.raw(trusted), class_="hedron-code")
```

## `process_image`

```bash
pip install "hedron[images]>=0.27.0,<0.28"
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `path_or_bytes` | `str \| bytes` | required | Filesystem path or raw image bytes |
| `max_width` | `int` | `1600` | Downscale when wider |
| `format` | `str` | `"PNG"` | Pillow output format (`PNG` → RGBA, else RGB) |

**Returns:** `bytes` — encoded image bytes.

```python
from hedron import process_image

png_bytes = process_image("photo.jpg", max_width=1200, format="PNG")
```

## `validate_email_address`

```bash
pip install "hedron[email]>=0.27.0,<0.28"
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `value` | `str` | required | Address to validate |

**Returns:** normalized email `str`.

```python
from hedron import validate_email_address

validate_email_address("user@example.com")
```

## Errors

| Situation | Code / behavior |
|---|---|
| Markdown / highlight without extra | Diagnostic with install remediation |
| `process_image` without Pillow | `HED-CONTENT-0003` — install `hedron[images]` |
| `validate_email_address` without email-validator | `HED-CONTENT-0004` — install `hedron[email]` |
| Invalid email | `HED-CONTENT-0005` |
| `TrustedHtml.nh3` without nh3 | `HED-SEC-0020` — install `hedron[sanitize]` |

## Install remediations

| API | Extra |
|---|---|
| `Markdown` | `pip install "hedron[markdown]>=0.27.0,<0.28"` |
| `highlight_code` | `pip install "hedron[code]>=0.27.0,<0.28"` |
| `process_image` | `pip install "hedron[images]>=0.27.0,<0.28"` |
| `validate_email_address` | `pip install "hedron[email]>=0.27.0,<0.28"` |
| `TrustedHtml.nh3` | `pip install "hedron[sanitize]>=0.27.0,<0.28"` |

See also [Security types](SECURITY_TYPES.md) and [Charts and HTMX](../guides/charts-and-htmx.md).
