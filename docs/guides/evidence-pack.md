# Evidence pack

Public supply-chain and release evidence for evaluators. Maintainer scripts produce
these artifacts at cut time.

## Where to get artifacts

| Artifact | Preferred source | Regenerator (tagged checkout) |
|---|---|---|
| SBOM | GitHub Release assets for the train tag (when attached), or regenerate | [`scripts/generate_sbom.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/generate_sbom.py) |
| License inventory | GitHub Release assets (when attached), or regenerate | [`scripts/license_inventory.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/license_inventory.py) |
| Evidence bundle | GitHub Release / `dist/evidence-bundle` after `build_evidence_bundle.py` | [`scripts/build_evidence_bundle.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/build_evidence_bundle.py) |
| Package verify (0.18) | CI / release checklist | [`scripts/verify_pkg_18.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/verify_pkg_18.py) |

**PyPI is authoritative for package versions.** Confirm `hedron==0.18.0` (and sibling
packages on the Beta train) on [PyPI](https://pypi.org/project/hedron/). Git tags such as `v0.18.0`
mark the cut; Release asset attachment may lag — if assets are missing, regenerate from
the tagged checkout as below.

Releases: [eddiethedean/hedron/releases](https://github.com/eddiethedean/hedron/releases).
Tags: [eddiethedean/hedron/tags](https://github.com/eddiethedean/hedron/tags).
Script index: [`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md).

## How to verify (evaluator)

1. Confirm package versions on PyPI match your pin (for example `hedron==0.18.0`).
2. Prefer GitHub Release assets for **`v0.18.0`** when present (SBOM / license /
   evidence-bundle).
3. If Release assets are absent, clone the tag and regenerate:

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
git checkout v0.18.0
uv sync
uv run python scripts/build_evidence_bundle.py
uv run python scripts/verify_pkg_18.py
```

Formats are maintainer-oriented evidence — **not** a marketed SLSA attestation product
or commercial compliance certification.

## Related

- Maturity claims: [What's ready](whats-ready.md)
- Diligence sheet: [Enterprise diligence](enterprise-diligence.md)
- Maintainer cut procedure (GitHub): [`docs/RELEASE.md`](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md)

## FAQ snippets

**Where is the SBOM?** In `dist/evidence-bundle/` after `build_evidence_bundle.py`, or on
the GitHub Release when assets are attached.

**Why might GitHub “Latest release” lag the PyPI train?** Tags can land before Release
objects/assets are published. Trust PyPI + the git tag for version truth; regenerate
evidence from the tag if needed.

**What does Supported mean if some ops rows are Deferred?** Feature Supported ≠ full
load/proxy proof. Prefer polling when `PERF-10-001` / live-browser Deferred rows matter
for your risk profile — see [What's ready](whats-ready.md).
