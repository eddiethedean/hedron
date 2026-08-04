---
status: shipped
---

# Content extras


!!! note "Stability (0.8 compatibility baseline)"

    Classifications for this surface are recorded in [STABILITY.md](STABILITY.md). Package maturity (Beta/Alpha) is separate from API level (`beta` / `experimental` / `internal` / `deferred`).

**Status:** Shipped in `0.6.0`

Optional content helpers live in `hedron.content` (lazy imports; missing extras raise
diagnostics with exact install commands).

## `Markdown`

```bash
pip install "hedron[markdown]"
```

```python
from hedron import Markdown

Markdown("# Hello\n\nSupports **fenced code** and tables.")
```

Rendered Markdown is sanitized through `TrustedHtml.nh3` before `html.raw`. Install
`hedron[sanitize]` (or rely on the markdown extra's dependency chain) so nh3 is available.

## `highlight_code`

```bash
pip install "hedron[code]"
```

```python
from hedron import highlight_code
from hedron_core.html import html

trusted = highlight_code("print('hi')", lexer="python")
node = html.div(html.raw(trusted), class_="hedron-code")
```

## `process_image`

```bash
pip install "hedron[images]"
```

```python
from hedron import process_image

# Returns processed bytes / metadata under Pillow; see remediation if Pillow is missing.
process_image(path_or_bytes, max_width=1200)
```

## `validate_email_address`

```bash
pip install "hedron[email]"
```

```python
from hedron import validate_email_address

validate_email_address("user@example.com")  # normalized address or raises
```

## Install remediations

| API | Extra |
|---|---|
| `Markdown` | `pip install "hedron[markdown]"` |
| `highlight_code` | `pip install "hedron[code]"` |
| `process_image` | `pip install "hedron[images]"` |
| `validate_email_address` | `pip install "hedron[email]"` |
| `TrustedHtml.nh3` | `pip install "hedron[sanitize]"` |

See also [Security types](SECURITY_TYPES.md) and [Charts and HTMX](../guides/charts-and-htmx.md).
