# hedron-conformance

[![PyPI](https://img.shields.io/pypi/v/hedron-conformance.svg)](https://pypi.org/project/hedron-conformance/)
[![Python](https://img.shields.io/pypi/pyversions/hedron-conformance.svg)](https://pypi.org/project/hedron-conformance/)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/hedron/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/hedron/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/eddiethedean/hedron/blob/main/LICENSE)

Language-neutral Hedron conformance-test kit and capability runner.

Ships versioned machine-readable fixtures, golden render/diagnostic artifacts,
normalization rules, and a capability-level runner CLI so experimental Java/Node
runtimes and optional native accelerators can prove parity with the Python
reference — without matching incidental CPython formatting.

Also available as the flagship extra `hedron[conformance]`.

**Package maturity:** Beta · **Train:** `0.38.x` (last published `0.39.0`) · pin `>=0.39.0,<0.40`

## Install

```bash
pip install "hedron-conformance>=0.39.0,<0.40"
# or
uv add "hedron-conformance>=0.39.0,<0.40"
# via flagship:
pip install "hedron[conformance]>=0.39.0,<0.40"
```

Requires Python 3.11–3.14.

## Runner

```bash
hedron-conformance run
hedron-conformance run --json
hedron-conformance list
hedron-conformance schema
hedron-conformance --version
# or
python -m hedron_conformance run
```

Failures report fixture id, contract version, and violated capability.

### Python API

```python
from hedron_conformance import load_bundled_fixtures, run_kit

fixtures = load_bundled_fixtures()
result = run_kit(fixtures)
assert result.ok
```

## Related runtimes

Experimental evaluators in the monorepo (not published as PyPI apps):

- [`hedron-runtime-node`](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-runtime-node) — Node ≥ 18
- [`hedron-runtime-java`](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-runtime-java) — JDK 11+

## Links

- [Package docs](https://hedron.readthedocs.io/en/latest/packages/hedron-conformance/)
- [Conformance docs](https://hedron.readthedocs.io/en/latest/conformance/INDEX/)
- [Changelog](https://github.com/eddiethedean/hedron/blob/main/packages/hedron-conformance/CHANGELOG.md)
- [Source](https://github.com/eddiethedean/hedron/tree/main/packages/hedron-conformance)
- [Issues](https://github.com/eddiethedean/hedron/issues)
- [`hedron-core`](https://pypi.org/project/hedron-core/)

## License

MIT. See the [repository license](https://github.com/eddiethedean/hedron/blob/main/LICENSE).
