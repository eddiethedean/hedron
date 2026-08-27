# hedron-posit

[![PyPI](https://img.shields.io/pypi/v/hedron-posit.svg)](https://pypi.org/project/hedron-posit/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-posit.svg)](https://pypi.org/project/hedron-posit/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Unified Posit Workbench / Connect deployment facade for Hedron.

**Package maturity:** Stable · **Repository release candidate:** `v1.0.0` (Git tag/PyPI upload deferred) · **Latest PyPI release:** `v0.66.2` · public pin `>=0.66.2,<0.67` until publication; checkouts use `uv sync`

```python
from hedron_posit import HedronPosit

app = HedronPosit(title="My app", session_secret="replace-me")
```

Install with `pip install "hedron[posit]>=0.66.2,<0.67"` or
`pip install "hedron-posit>=0.66.2,<0.67"`.

Native Connect GUID is Supported on Posit Connect **2025.06.0** through **2026.07.0**.
Posit Workbench **2025.05.1** through **2026.07.0** is Supported.
Install this package into the content environment (do not vendor only source trees
on Connect 2025.06).

Docs: [Posit deployments](https://hedron.readthedocs.io/en/latest/guides/posit/).
