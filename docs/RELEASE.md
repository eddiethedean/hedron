# Cutting a Hedron release

This is the living maintainer runbook for the `0.26.x` train. Historical cut records
live under `docs/archive/`. The last published release is `v0.26.0`; the next planned
patch is `v0.26.1`.

Hedron uses coordinated package versions for the core train. A Git tag includes `v`;
Python metadata does not. Never move or replace a published tag.

## Preconditions

1. The release commit is on green `main`, with no unexplained waived checks.
2. `docs/release.toml`, package metadata, `__version__`, dependency pins, lockfile,
   changelog headings, CI gate version, security support window, and release notes agree.
3. `docs/acceptance/release-gate-0.26.toml` remains Verified and the 0.26 package verifier
   passes.
4. The repository and PyPI trusted-publishing configuration are controlled by active
   maintainers; the release uses the GitHub Actions workflow.
5. The tag does not already exist locally or on the remote.

## Local release candidate

Run the same suites used by release CI:

```bash
uv sync --locked --all-groups --python 3.12
bash scripts/ci_checks.sh test --python 3.12
bash scripts/ci_checks.sh quality --python 3.12
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.26.1
bash scripts/ci_checks.sh browser --python 3.12
uv run python scripts/check_release_gate.py 0.26.1
uv run python scripts/verify_pkg_26.py
```

Build and inspect local evidence if the release changes packaging or the release path:

```bash
uv run python scripts/build_evidence_bundle.py --version 0.26.1
uv run python scripts/rehearse_release.py
```

Do not publish artifacts built on a maintainer laptop. These commands are rehearsal and
diagnosis; the tag workflow builds and attests the released files.

## Tag and publish

After reviewing the complete version/changelog diff:

```bash
git fetch --tags origin
git rev-parse v0.26.1 >/dev/null 2>&1 && { echo "tag exists; stop"; exit 1; }
git tag -a v0.26.1 -m "Hedron 0.26.1"
git push origin v0.26.1
```

The release workflow must, in order:

1. run Python 3.11–3.14 tests, quality/docs, browser, and evidence suites;
2. build the evidence bundle for the tag version;
3. build all workspace distributions;
4. write `release-manifest.json` with SHA-256 checksums and attest the artifacts;
5. publish packages to PyPI;
6. install the exact published `hedron==0.26.1`, run `hedron new`, and import the
   generated application;
7. create the GitHub Release only after the published quick-start verification passes,
   attaching distributions, evidence, and the checksum manifest.

If publication is partial, use the workflow's explicit `publish_only` recovery input for
the same immutable tag. Do not create a replacement tag or upload locally built files.

## Post-release verification

- Confirm `hedron==0.26.1` and every coordinated package version on PyPI.
- Confirm the GitHub Release includes `release-manifest.json`, SBOM, license inventory,
  evidence manifests, wheels, and source distributions.
- Confirm build attestations exist and the checksum verifier succeeds on downloaded
  assets.
- Activate `v0.26.1` on Read the Docs, mark it stable, and verify the version menu.
- Update `docs/release.toml` so `published_version` is `0.26.1`, run
  `scripts/check_docs_train_ssot.py`, and publish any post-release documentation commit.
- Verify the stable quick start from a clean environment once more.

## Patch-release scope

A patch release may fix bugs, tests, documentation, packaging, or security issues
without removing a Supported API. Any unavoidable behavior change must be called out in
the release notes with impact, migration, and rollback instructions. Public API removal,
security-default redesign, or a new compatibility train requires the RFC/decision path
described in [governance](guides/governance.md).
