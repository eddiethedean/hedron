# Release evidence and checksums

Every Hedron release publishes its wheels, source distributions, and supply-chain
evidence as assets on the matching GitHub Release. Beginning with **0.26.1**, release CI
also attaches a checksum manifest and refuses to create the GitHub Release until the
exact PyPI artifact passes the documented scaffold smoke. PyPI remains authoritative
for installable package versions.

## 0.28.0 assets

- [GitHub Release v0.28.0](https://github.com/eddiethedean/hedron/releases/tag/v0.28.0)
- [Hedron 0.28.0 on PyPI](https://pypi.org/project/hedron/0.28.0/)
- [Build provenance attestations](https://github.com/eddiethedean/hedron/attestations)

Prefer the release-tag `release-manifest.json` (when attached) plus SBOM / license /
evidence-bundle assets for evaluator diligence. Reproduce from the immutable tag if an
expected asset is missing.

## 0.26.0 assets

- [GitHub Release v0.26.0](https://github.com/eddiethedean/hedron/releases/tag/v0.26.0)
- [Hedron 0.26.0 on PyPI](https://pypi.org/project/hedron/0.26.0/)
- [Build provenance attestations](https://github.com/eddiethedean/hedron/attestations)

Version 0.26.0 predates `release-manifest.json`; use its GitHub build attestations and
evidence assets, or reproduce the evidence from its immutable tag. For 0.26.1 and later,
`release-manifest.json` records the SHA-256 digest and byte size of every attached wheel,
source distribution, SBOM, license inventory, and evidence artifact. The evidence
bundle's own `bundle-manifest.json` identifies its release version, gate manifest,
lockfile digest, and generated contents.

## Verify downloaded assets

For 0.26.1 or later, download `release-manifest.json`, the assets you need, and the
verification script from the same tag. Replace `VERSION` below, then run:

```bash
VERSION=0.28.0
curl -fsSLO "https://github.com/eddiethedean/hedron/releases/download/v${VERSION}/release-manifest.json"
curl -fsSLO "https://raw.githubusercontent.com/eddiethedean/hedron/v${VERSION}/scripts/verify_release_manifest.py"
# Download the wheel, sdist, and/or evidence assets you intend to verify.
python verify_release_manifest.py release-manifest.json --artifact-dir .
```

The verifier fails if a listed file is missing, duplicated, has a different size, or
has a different SHA-256 digest. You may also compare a single file manually:

```bash
python -c "import hashlib, pathlib; p=pathlib.Path('FILE'); print(hashlib.sha256(p.read_bytes()).hexdigest())"
```

Match that value to the asset's `sha256` field in `release-manifest.json`.

## Reproduce evidence from a tag

Regeneration is useful for audit comparison, but it does not replace verification of
the artifacts actually published by the release workflow.

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
git checkout v0.28.0
uv sync --locked
uv run python scripts/build_evidence_bundle.py --version 0.28.0
uv run python scripts/verify_pkg_28.py
```

| Artifact | Generator |
|---|---|
| SBOM | `scripts/generate_sbom.py` |
| License inventory | `scripts/license_inventory.py` |
| Asset audit | `scripts/asset_audit.py` |
| Evidence bundle | `scripts/build_evidence_bundle.py` |
| Release checksums | `scripts/write_release_manifest.py` |

If an expected release asset or attestation is absent, treat that as a release defect
and report it through [support](support.md). Security-sensitive discrepancies should use
the private [security-reporting process](../SECURITY.md).
