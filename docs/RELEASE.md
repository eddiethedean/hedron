# Cutting a Hedron release

This runbook covers the authorized publication of the verified, currently untagged **1.0.0**
candidate and later coordinated releases. The in-tree artifacts and technical evidence are
verified; the Git tag and registry upload remain separate, explicit release actions.
Historical cut records live under `docs/archive/`; future releases repeat the same build,
upload, smoke-test, and documentation sequence without moving an existing tag.

Hedron is a Python monorepo with independently publishable distributions. The Stable 1.0 package
boundary is `hedron-core`, `hedron`, `edron`, `hedron-data`, `hedron-charts`, and `hedron-maps`.
Every other distribution is a Beta satellite even when it shares the `1.0.0` version number;
`fastapi-workbench` is currently `1.0.1`. The removed `hedron-workbench` package is not part of
the release inventory.

A Git tag includes the `v` prefix; Python metadata does not. Never move or replace a
published tag except for an explicitly authorized corrective retag after a failed
publication.

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
6. Confirm the tag does not already exist locally or on the remote. A failed
   publication requires an authorized corrective action after metadata and workflow
   fixes.
7. Confirm the protected `release` GitHub environment requires maintainer approval. The main and
   native workflows use the environment-scoped PyPI token; Edron uses PyPI trusted publishing.
8. Before publishing release notes, verify uploaded wheels, attestations, both Hedron and Edron
   install/scaffold smoke tests, and then set `registry_status = "uploaded"` in
   `docs/release.toml`. Until that point, the public fallback pins remain authoritative.

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
uv run python scripts/check_published_quickstart.py 1.0.0 --dist-dir dist --attempts 1
```

Run the quick-start check first against local artifacts. After upload, rerun it against the
registry and record the result before changing public documentation.

## Tag and publish

Use this exact sequence; do not push both tags together:

1. Fast-forward `main` to the green `v1.0` release commit and verify Read the Docs.
2. Create and push `v1.0.0`. The coordinated workflow publishes every main-train distribution
   except Edron, `edron-sim`, and the separately owned native artifacts.
3. Wait for the coordinated workflow, native-wheel workflow, attestations, PyPI visibility, and
   the published Hedron quick-start verification to succeed.
4. Create and push `edron-v1.0.0`. The Edron workflow must preflight the already-published Stable
   dependencies, then publish Edron and the Beta `edron-sim` companion.
5. Verify both published Edron artifacts and the generated application before changing public
   status facts.

Every upload requires explicit maintainer authorization through the protected release workflow.
After publication, update `docs/release.toml` first; rendered release callouts and validation
derive from it. Then update release notes, rerun the documentation/release checks, and verify all
PyPI project pages. Never move either tag after publication.
