# hedron-conformance

Language-neutral conformance-test kit for Hedron (phase 0.14).

Ships versioned machine-readable fixtures, golden render/diagnostic artifacts,
normalization rules, and a capability-level runner CLI so experimental Java/Node
runtimes and optional native accelerators can prove parity with the Python
reference without matching incidental CPython formatting.

## Install

```bash
pip install "hedron-conformance>=0.16.0"
# or
uv add "hedron-conformance>=0.16.0"
```

## Runner

```bash
hedron-conformance run
# or
python -m hedron_conformance
```

Failures report fixture id, contract version, and violated capability.

## License

MIT. See [LICENSE](LICENSE).
