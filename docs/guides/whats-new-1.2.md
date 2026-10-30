---
description: Hedron 1.2.0 release notes and Python 3.11 migration guidance.
---

# What’s new in Hedron 1.2

Hedron `v1.2.0` was published on PyPI on 2026-10-27. This release moves the maintained Python
workspace to CPython 3.11–3.14 and tightens the typing and runtime baseline.

## Python 3.11+ baseline

- Maintained distributions and generated applications declare `requires-python = ">=3.11,<3.15"`.
- Ruff targets `py311`; BasedPyright targets Python 3.11 in `all` mode.
- `Self` and `NotRequired` use the standard library, and Python 3.10 enum/TOML compatibility
  branches are removed while public compatibility aliases are retained.
- Python 3.11–3.14, package metadata, native wheel selectors, and migration tooling share the
  declared support baseline.

## Upgrade

Move the project to Python 3.11 or newer, recreate its virtual environment, update coordinated
packages, and run the application’s test suite:

```bash
python -m pip install -U "hedron>=1.2.0,<1.3" "edron>=1.2.0,<2.0"
```

See the [upgrade guide](upgrade.md) and [compatibility policy](../COMPATIBILITY.md) before moving
an application that still runs on Python 3.10. The published 1.1 support window was not extended.

## Publication evidence

PyPI filenames and SHA-256 digests for all 44 wheel and source archive files across the 22
coordinated Python distributions match the retained [1.2.0 publication record](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/evidence-120/PUBLICATION.md).
The optional native package is published through a separate workflow and is not included in that
coordinated Python artifact verification.
