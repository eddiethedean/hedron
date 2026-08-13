# Fleet SBOM notes (SUPPLY-035)

Owning gate: `SUPPLY-035`.

## Generation

```bash
python scripts/build_evidence_bundle.py
```

Produces CycloneDX / SPDX-oriented artifacts under `dist/evidence-bundle/` together with
asset and stability inventories. Dependency vulnerability triage:

```bash
python scripts/dep_audit.py
```

## Retention

- Cut-time evidence bundles are retained with the GitHub Release assets for `v0.35.0`
- Prior train bundles remain available on historical tags (`v0.34.0`, …)
- Rollback uses previous published train pins (see `ROLLBACK.md`)

## Pass criteria

- `build_evidence_bundle.py` and `dep_audit.py` exist and are CI-attested via the evidence job
- Critical/high findings dispositioned in `security-review-035/DISPOSITION.toml`
