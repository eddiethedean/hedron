# Evidence pack

Public supply-chain and release evidence for evaluators. Maintainer scripts produce
these artifacts at cut time; **prefer consuming files attached to a GitHub Release**
over regenerating from an arbitrary checkout.

## Where to get artifacts

| Artifact | Preferred source | Regenerator (tagged checkout) |
|---|---|---|
| SBOM | GitHub Release assets for the train tag | [`scripts/generate_sbom.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/generate_sbom.py) |
| License inventory | GitHub Release assets | [`scripts/license_inventory.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/license_inventory.py) |
| Evidence bundle | GitHub Release assets / `dist/evidence-bundle` | [`scripts/build_evidence_bundle.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/build_evidence_bundle.py) |
| Package verify (0.13) | CI / release checklist | [`scripts/verify_pkg_13.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/verify_pkg_13.py) |

Releases: [eddiethedean/hedron/releases](https://github.com/eddiethedean/hedron/releases).
Script index: [`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md).

## How to verify (evaluator)

1. Open the GitHub Release matching your pinned train (for example **`v0.13.0`**).
2. Download SBOM / license / evidence-bundle assets when present.
3. Confirm package versions on PyPI match the release tag (`hedron==0.13.0`, …).
4. Optionally clone the tag and run `uv run python scripts/verify_pkg_13.py` (or the
   verify script named for that train) in a clean environment.

Formats are maintainer-oriented evidence — **not** a marketed SLSA attestation product
or commercial compliance certification.

## Related

- Maturity claims: [What's ready](whats-ready.md)
- Diligence sheet: [Enterprise diligence](enterprise-diligence.md)
- Maintainer cut procedure (GitHub): [`docs/RELEASE.md`](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md)
