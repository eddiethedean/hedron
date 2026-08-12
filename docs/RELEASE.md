# Cutting a Hedron release

This is the living maintainer runbook for the `0.29.x` train. Historical cut records
live under `docs/archive/`. The last published release is `v0.29.0`; the next planned
patch is `v0.29.1`.

Hedron uses coordinated package versions for the core train. A Git tag includes `v`;
Python metadata does not. Never move or replace a published tag.

## Preconditions

1. The release commit is on green `main`, with no unexplained waived checks.
2. `docs/release.toml`, package metadata, `__version__`, dependency pins, lockfile,
   changelog headings, CI gate version, security support window, and release notes agree.
3. `docs/acceptance/release-gate-0.29.toml` remains Verified and the 0.29 package verifier
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
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.29.0
bash scripts/ci_checks.sh browser --python 3.12
uv run python scripts/check_release_gate.py 0.29.0
uv run python scripts/verify_pkg_29.py
```

Build and inspect local evidence if the release changes packaging or the release path:

```bash
uv run python scripts/build_evidence_bundle.py --version 0.29.0
uv run python scripts/rehearse_release.py
```

Do not publish artifacts built on a maintainer laptop. These commands are rehearsal and
diagnosis; the tag workflow builds and attests the released files.

## Tag and publish

After reviewing the complete version/changelog diff:

```bash
git fetch --tags origin
git rev-parse v0.28.2 >/dev/null 2>&1 && { echo "tag exists; stop"; exit 1; }
git tag -a v0.28.2 -m "Hedron 0.28.2"
git push origin v0.28.2
```

The release workflow must, in order:

1. run Python 3.11–3.14 tests, quality/docs, browser, and evidence suites;
2. build the evidence bundle for the tag version;
3. build all workspace distributions;
4. write `release-manifest.json` with SHA-256 checksums and attest the artifacts;
5. publish packages to PyPI;
6. publish `hedron-native` to crates.io (`CARGO_REGISTRY_TOKEN`);
7. install the exact published `hedron==0.28.2`, run `hedron new`, and import the
   generated application (scaffold pin must match `docs/release.toml` `pin_floor`);
8. create the GitHub Release **only after** the published quick-start verification
   succeeds, attaching distributions, evidence, and the checksum manifest (omit plain
   `linux_*` native wheels that PyPI rejects).

If publication is partial, use the workflow's explicit `publish_only` recovery input for
the same immutable tag. Do not create a replacement tag or upload locally built files.

## Post-release verification

- Confirm `hedron==0.28.2` and every coordinated package version on PyPI.
- Confirm the GitHub Release includes `release-manifest.json`, SBOM, license inventory,
  evidence manifests, wheels, and source distributions.
- Confirm build attestations exist and the checksum verifier succeeds on downloaded
  assets.
- Activate `v0.28.2` on Read the Docs, mark it stable, and verify the version menu.
- Keep `docs/release.toml` `published_version` at `0.28.2`, run
  `scripts/check_docs_train_ssot.py`, and publish any post-release documentation commit.

## Template: next patch (`0.28.3`)

Bump the coordinated train to `0.28.3`, set `docs/release.toml` accordingly, then:

```bash
bash scripts/ci_checks.sh evidence --python 3.12 --gate-version 0.28.3
uv run python scripts/check_release_gate.py 0.28.3
git tag -a v0.28.3 -m "Hedron 0.28.3"
git push origin v0.28.3
```
