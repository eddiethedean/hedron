# Cutting a Hedron release

This runbook records the authorized publication of **1.0.0** and governs later coordinated
releases. The 1.0 artifacts, tags, and registry uploads are complete; future Git tags and registry
uploads remain separate, explicit release actions.
Historical cut records live under `docs/archive/`; future releases repeat the same build,
upload, smoke-test, and documentation sequence without moving an existing tag.

Hedron is a Python monorepo with independently publishable distributions. The Stable 1.0 package
boundary is `hedron-core`, `hedron`, `edron`, `hedron-data`, `hedron-charts`, and `hedron-maps`.
Every other distribution is a Beta satellite even when it shares the `1.0.0` version number;
`fastapi-workbench` is currently `1.0.11`. The removed `hedron-workbench` package is not part of
the release inventory.

Release tags use the `release-` namespace and carry no package-version semantics; the
checked-out repository metadata is the version source. Never move or replace a published tag
except for an explicitly authorized corrective retag after a failed publication.

## Preconditions

1. The release commit is on the `v1.0` branch with a clean working tree and green CI. Fast-forward
   `main` to that exact commit and verify the Read the Docs `latest` build before publishing, so
   immutable package links never land on an older documentation train.
2. `docs/release.toml`, package metadata, `__version__`, dependency pins, lockfile,
   changelog headings, security support window, and release notes agree.
3. Run `uv run python scripts/check_100.py --check-plan`; all 1.0-owned rows must be
   planned or verified with no unexpected deferred work.
4. Verify the release gate with `uv run python scripts/check_100.py --gate ENTRY-100
   --verify` and retain the generated evidence under `docs/acceptance/`.
5. Confirm the package inventory contains `hedron`, its maintained satellites,
   `hedron-posit`, and `fastapi-workbench`; it must not contain `hedron-workbench`.
6. Confirm the release tag does not already exist locally or on the remote. A failed
   publication requires an authorized corrective action after metadata and workflow
   fixes.
7. Confirm the protected `release` GitHub environment requires maintainer approval. The main and
   native workflows use the environment-scoped PyPI token; Edron uses PyPI trusted publishing.
8. For a future release, before publishing release notes, verify uploaded wheels, attestations,
   both Hedron and Edron install/scaffold smoke tests, and then set
   `registry_status = "uploaded"` in `docs/release.toml`. Until that point, the previous
   public release pins remain authoritative.

## Build and validate artifacts

```bash
uv sync --locked --all-groups --python 3.12
uv run pytest -q
uv run ruff check packages tests examples --output-format concise
uv run python scripts/check_100.py --check-plan
uv run python scripts/check_100.py --gate ENTRY-100 --verify
uv lock --check
git diff --check
```

Build wheels and test them in a clean environment before tagging:

```bash
uv build --all-packages
uv run python scripts/check_published_quickstart.py 1.0.8 --dist-dir dist --attempts 1
uv run python scripts/check_workbench_release_artifacts.py --dist-dir dist
```

Run the quick-start check first against local artifacts. After upload, rerun it against the
registry and record the result before changing public documentation.

## Tag and publish

Use this exact sequence; create one unique release tag per publication:

1. Fast-forward `main` to the green `v1.0` release commit and verify Read the Docs.
2. Create and push a unique release tag (for example, `release-20260902-01`). The coordinated workflow
   publishes every workspace distribution, including Edron and `edron-sim`, except the separately
   owned native artifacts.
3. Wait for the coordinated workflow, native-wheel workflow, attestations, PyPI visibility, and
   the published Hedron quick-start verification to succeed.
4. The separate Edron workflow remains available for historical `edron-v*` tags and recovery, but
   new coordinated releases publish Edron and the Beta `edron-sim` companion in step 2.
5. Verify both published Edron artifacts and the generated application before changing public
   status facts.

The completed 1.0.0 cut used the historical `v1.0.0` tag followed by `edron-v1.0.0`; those tags
remain immutable. The coordinated workflow now includes Edron and `edron-sim`, so future cuts do
not require a second publication tag.

Every upload requires explicit maintainer authorization through the protected release workflow.
After publication, update `docs/release.toml` first; rendered release callouts and validation
derive from it. Then update release notes, rerun the documentation/release checks, and verify all
PyPI project pages. Never move a release tag after publication.
