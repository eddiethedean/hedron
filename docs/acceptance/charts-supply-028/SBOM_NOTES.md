# Charts / native SBOM notes (SUPPLY-028)

Owning gate: `SUPPLY-028`.

## Generator

Use the repository SBOM helper:

```bash
uv run python scripts/generate_sbom.py
```

Also invoked from `scripts/build_evidence_bundle.py` when assembling a release
evidence pack.

## Scope for 0.28

- `hedron-charts` and transitive chart runtimes (matplotlib Supported;
  Plotly/Vega/etc. Experimental pins)
- `hedron-native` wheels / sdist and Rust build inputs when present
- Flagship `hedron[charts]` / `hedron[native]` extras as declared in package
  metadata

## Notes

- Digests for vendored browser runtimes are asserted via
  `hedron_charts.pins.RUNTIME_PINS` and `tests/unit/test_chart_runtime_pins.py`.
- SBOM output is an evidence artifact; pin / license honesty still requires
  `LICENSE_INVENTORY.md` and offline install rehearsal.
