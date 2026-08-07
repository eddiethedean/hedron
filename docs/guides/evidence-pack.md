# Evidence pack

Public supply-chain and release evidence for evaluators. Maintainer scripts produce
these artifacts at cut time.

## Where to get artifacts

| Artifact | Preferred source | Regenerator (tagged checkout) |
|---|---|---|
| SBOM | GitHub Release assets for the train tag (when attached), or regenerate | [`scripts/generate_sbom.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/generate_sbom.py) |
| License inventory | GitHub Release assets (when attached), or regenerate | [`scripts/license_inventory.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/license_inventory.py) |
| Evidence bundle | GitHub Release / `dist/evidence-bundle` after `build_evidence_bundle.py` | [`scripts/build_evidence_bundle.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/build_evidence_bundle.py) |
| Package verify (0.19) | CI / release checklist | [`scripts/verify_pkg_19.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/verify_pkg_19.py) |

**PyPI is authoritative for published package versions.** Last published train is
`hedron==0.18.0` (`v0.18.0`). Coordinated **`0.19.0`** is Ready to cut / Implemented on
`main` — confirm on [PyPI](https://pypi.org/project/hedron/) after `v0.19.0` is tagged.
Until then, regenerate evidence from `main` (or the future `v0.19.0` tag).

Releases: [eddiethedean/hedron/releases](https://github.com/eddiethedean/hedron/releases).
Tags: [eddiethedean/hedron/tags](https://github.com/eddiethedean/hedron/tags).
Script index: [`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md).

## How to verify (evaluator)

1. Confirm package versions on PyPI match your pin (for example `hedron==0.19.0` after
   cut; until then last published is `0.18.0`).
2. Prefer GitHub Release assets for **`v0.19.0`** when present (SBOM / license /
   evidence-bundle); until cut, use **`v0.18.0`** assets or regenerate from `main`.
3. If Release assets are absent, clone and regenerate:

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
# After cut: git checkout v0.19.0
# Pre-cut: stay on main (0.19.0 Ready to cut)
uv sync
uv run python scripts/build_evidence_bundle.py
uv run python scripts/verify_pkg_19.py
```

Formats are maintainer-oriented evidence — **not** a marketed SLSA attestation product
or commercial compliance certification.

## Related

- Maturity claims: [What's ready](whats-ready.md)
- Diligence sheet: [Enterprise diligence](enterprise-diligence.md)
- Maintainer cut procedure (GitHub): [`docs/RELEASE.md`](https://github.com/eddiethedean/hedron/blob/main/docs/RELEASE.md)

## FAQ snippets

See also [FAQ — SBOM / evidence](faq.md#where-is-the-sbom--evidence-bundle).
