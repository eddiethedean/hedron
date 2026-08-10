# Versioned documentation

Hedron publishes documentation for released versions on Read the Docs.

- **Stable** is the documentation for the newest published release.
- **Latest** follows the development branch and can describe unreleased behavior.
- A version such as **0.26.0** is an immutable snapshot built from that Git tag.

Use the version menu in the documentation header to switch versions. When copying an
install command, use the docs for the version you intend to install. The banner and
version menu make development documentation distinguishable from a released snapshot.

## Which version should I read?

| Situation | Documentation version |
|---|---|
| Starting a production project | Stable |
| Maintaining an app pinned to an older release | The matching version tag |
| Contributing to Hedron | Latest |
| Evaluating an unreleased fix | Latest, followed by the relevant pull request |

The public API may evolve between minor releases while Hedron is pre-1.0. Patch releases
within a train are intended to remain compatible. See the [compatibility policy](../COMPATIBILITY.md)
and [upgrade guide](upgrade.md) before moving between trains.

## Maintainer release step

After pushing a release tag, activate its Read the Docs version, mark the newest release
as **stable**, and verify that the header's version menu links to both the tag and
**latest**. Do not repoint an existing tag. If a released page is wrong, correct it in a
patch release and add a short note to the release history.

