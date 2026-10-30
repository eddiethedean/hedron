# v1.3.0 publication verification

**Published:** 2026-10-30<br>
**Release:** Hedron `v1.3.0`<br>
**Tag:** [`release-1.3.0`](https://github.com/eddiethedean/hedron/releases/tag/release-1.3.0)<br>
**Tag commit:** `b265426da6c787db63ad1ec93d1bba622e09855f`<br>
**Main CI:** [run 40998469596](https://github.com/eddiethedean/hedron/actions/runs/40998469596)<br>
**Release workflow:** [run 40999409118](https://github.com/eddiethedean/hedron/actions/runs/40999409118)<br>
**PyPI:** <https://pypi.org/project/hedron/1.3.0/><br>
**npm:** <https://www.npmjs.com/package/hedron-runtime-node>

The exact tag commit passed main CI, the strict 1.3.0 release gate, and the approved artifact
verification. Release workflow run 40999409118 completed successfully, published the coordinated
Python packages to PyPI, published `hedron-runtime-node` to npm, completed the optional Java
runtime publish step, verified the published quick start, and created the GitHub release.

The approved [Python artifact manifest](python-artifacts.json) records 44 wheel and source archive
hashes across 22 distributions. The release workflow checked the release build against that exact
set and verified published PyPI payloads before upload. `hedron-core==1.3.0` and
`fastapi-workbench==1.0.13` had been published by the initial interrupted attempt; the successful
workflow retained those immutable versions after verifying parity and published the remaining
missing versions. All release files and supply-chain manifests are attached to the GitHub release.

The first publication attempt and its recovery are documented in
[the release approval record](RELEASE_APPROVAL_2026-10-30.md). That history is retained for
auditability; this file records the successful final publication.
