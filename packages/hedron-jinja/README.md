# hedron-jinja

[![PyPI](https://img.shields.io/pypi/v/hedron-jinja.svg)](https://pypi.org/project/hedron-jinja/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-jinja.svg)](https://pypi.org/project/hedron-jinja/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Explicit standards-first `.hdj` templates over Jinja, HTML, and HTMX for Hedron.

HDJ lets advanced applications write ordinary HTML, CSS, JavaScript, Web
Components, Jinja, and HTMX directly while preserving typed Hedron components and
render metadata. Install as `hedron-jinja` or via the flagship extra `hedron[jinja]`.

**Package maturity:** Beta · **Train:** `0.40.x` (published `v0.40.0`) · pin `>=0.40.0,<0.41`

## Install

```bash
pip install "hedron-jinja>=0.40.0,<0.41"
# or
uv add "hedron-jinja>=0.40.0,<0.41"
# via flagship:
pip install "hedron[jinja]>=0.40.0,<0.41"
```

Requires Python 3.11–3.14, `hedron-core`, and Jinja2.

## Quick start

```python
from jinja2 import Environment, FileSystemLoader
from hedron_jinja import HedronJinja, TemplateSpec

templates = HedronJinja(Environment(loader=FileSystemLoader("templates")))
result = templates.render(
    TemplateSpec("dashboard.hdj"),
    {"heading": "Operations"},
)
print(result.html)
```

Example `templates/dashboard.hdj`:

```hdj
---hdj
version = 1
kind = "fragment"
profile = "standard"
regions = ["main"]
---
<main id="main" hx-history-elt>{{ view.heading }}</main>
```

## Trust model

Templates are **trusted application code**, not a sandbox for hostile authors.
Strict mode checks a finite dynamic sink matrix with purpose-specific URL
filters. Deployment capability declarations and application policy remain
separate and authoritative. Format v1 accepts static `.hdj` dependencies only;
every source must render through `HedronJinja`.

## Links

- [Package docs](https://hedron.readthedocs.io/en/latest/packages/hedron-jinja/)
- [HDJ authoring guide](https://hedron.readthedocs.io/en/latest/guides/hdj-authoring/)
- [Jinja / HDJ API](https://hedron.readthedocs.io/en/latest/api/JINJA/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-jinja/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-jinja)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [HDJ progressive examples](https://github.com/eddiethedean/hedron/tree/main/examples/hdj-progressive)
- [`hedron-core`](https://pypi.org/project/hedron-core/) ·
  [`hedron`](https://pypi.org/project/hedron/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
