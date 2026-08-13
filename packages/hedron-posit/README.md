# hedron-posit

[![PyPI](https://img.shields.io/pypi/v/hedron-posit.svg)](https://pypi.org/project/hedron-posit/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-posit.svg)](https://pypi.org/project/hedron-posit/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Unified Posit Workbench / Connect deployment facade for Hedron.

```python
from hedron_posit import HedronPosit

app = HedronPosit(title="My app", session_secret="replace-me")
```

Install with `pip install "hedron[posit]>=0.33.0,<0.34"` or `hedron-posit`.

Docs: [Posit deployments](https://hedron.readthedocs.io/en/latest/guides/posit/).
Compatibility package: `hedron-workbench` (re-exports / `HedronWorkbench` subclass).
