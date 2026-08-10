# Evidence pack

Public supply-chain and release evidence for evaluators. Maintainer scripts produce
these artifacts at cut time.

## Where to get artifacts

| Artifact | Preferred source | Regenerator (tagged checkout) |
|---|---|---|
| SBOM | GitHub Release assets for the train tag (when attached), or regenerate | [`scripts/generate_sbom.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/generate_sbom.py) |
| License inventory | GitHub Release assets (when attached), or regenerate | [`scripts/license_inventory.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/license_inventory.py) |
| Evidence bundle | GitHub Release / `dist/evidence-bundle` after `build_evidence_bundle.py` | [`scripts/build_evidence_bundle.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/build_evidence_bundle.py) |
| Package verify (0.26) | CI / release checklist | [`scripts/verify_pkg_26.py`](https://github.com/eddiethedean/hedron/blob/main/scripts/verify_pkg_26.py) |

**PyPI is authoritative for published package versions.** Last published train is
`hedron==0.26.0` (`v0.26.0`). Confirm on [PyPI](https://pypi.org/project/hedron/).

Releases: [eddiethedean/hedron/releases](https://github.com/eddiethedean/hedron/releases).
Tags: [eddiethedean/hedron/tags](https://github.com/eddiethedean/hedron/tags).
Script index: [`scripts/README.md`](https://github.com/eddiethedean/hedron/blob/main/scripts/README.md).

## How to verify (evaluator)

1. Confirm package versions on PyPI match your pin (for example `hedron==0.26.0`).
2. Prefer GitHub Release assets for **`v0.26.0`** when present (SBOM / license /
   evidence-bundle). Maintainers should attach these on release day; if absent,
   regenerate from the tagged checkout.
3. If Release assets are absent, clone and regenerate:

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
git checkout v0.26.0
uv sync
uv run python scripts/generate_sbom.py
uv run python scripts/license_inventory.py
uv run python scripts/build_evidence_bundle.py
uv run python scripts/verify_pkg_26.py
```

Do not treat regenerated local artifacts as a substitute for confirming the published
PyPI version and GitHub Release assets when they exist.
