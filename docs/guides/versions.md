# Versioned documentation

Hedron publishes release snapshots and development documentation on Read the Docs.

- **Stable** documents the newest published release, currently **1.1.0**.
- **Latest** follows `main` and may describe changes after the **1.1.0** release.
- A numbered version such as **1.1.0** is an immutable snapshot built from the
  [`release-20260918-02`](https://github.com/eddiethedean/hedron/releases/tag/release-20260918-02) Git tag.

Use the version menu in the documentation header to switch versions. Before copying a
command or API example, confirm that the documentation version matches the package version
in your lockfile. The development banner identifies `latest` and local builds.

## Which version should I read?

| Situation | Documentation version |
|---|---|
| Starting or operating a production project | Stable |
| Maintaining an app pinned to an older release | The matching version tag |
| Contributing to Hedron | Latest |
| Evaluating an unreleased fix | Latest plus the relevant pull request or commit |

Stable public APIs follow the 1.x compatibility policy. Beta and Experimental surfaces can
change under their documented rules even when they ship in a Stable package. Read the
[compatibility policy](../COMPATIBILITY.md), [stability reference](../api/STABILITY.md), and
[upgrade guide](upgrade.md) before changing versions.

## Maintainer release step

After pushing a release tag, activate its Read the Docs version, mark the newest release as
**stable**, and verify that the version menu links to the tag and **latest**. Never repoint an
existing tag. Correct released documentation through a patch release and record the change in
the release history.
