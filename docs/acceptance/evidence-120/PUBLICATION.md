# v1.2.0 publication verification

**Checked:** 2026-10-28<br>
**Release:** Hedron `v1.2.0`<br>
**PyPI:** <https://pypi.org/project/hedron/1.2.0/><br>
**PyPI JSON:** <https://pypi.org/pypi/hedron/1.2.0/json>

The Hedron 1.2.0 release is published on PyPI. The first Hedron artifact was uploaded at
`2026-10-27T20:06:05.000138Z`. The published Hedron wheel and source archive match the
SHA-256 values in [python-artifacts.json](python-artifacts.json):

| Artifact | SHA-256 |
|---|---|
| `hedron-1.2.0-py3-none-any.whl` | `c0e714d39dc5b08391be06ca59080125965e2a95f5965973e80016b1ac2b3618` |
| `hedron-1.2.0.tar.gz` | `2b198656a40091d569416e12ebde3aebc184afc37ba4f4cda2b3ee6557250cef` |

The 22 coordinated Python distributions in the 1.2.0 artifact ledger were checked against
their PyPI release files: **44 of 44 wheel and source archive filenames and SHA-256 digests
match**. This includes Edron. The reproducibility ledger identifies package source commit
`92e369a26aaa771ee5b5d4a8264dfd758a71a533`; the local release tag
`release-20261027-01` points to `fced98f466478dd9e1c31a8e13f3b1bae7ce4fc3`, an evidence-only
follow-up commit whose parent is the package source commit.

The separately published native distribution is not included in that 22-package PyPI set.
The `hedron-native==0.1.4` PyPI project lookup returned not found at verification time, although
the separate native artifact ledger lists 16 platform wheels. This record therefore confirms
the coordinated Python release, not publication of those native wheels.
