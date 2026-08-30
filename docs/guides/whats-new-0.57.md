# What's new in 0.57

!!! note "Historical release note"

    This page records the 0.x release named in its title. For current installation,
    support, and published 1.0 status, use [Current release and support](current-release.md).
    Keep the historical pins below only when maintaining that release line.

Phase **0.57** (`v0.57.0` in-tree; tag/PyPI deferred) lands unified presentation and
zero-application-CSS evidence under
[RFC-0084](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0084-UNIFIED-PRESENTATION.md).

## Highlights

- Shared appearance vocabulary extended with `plain` / `raised`, width, overflow, track,
  and CSP-safe gap tokens (`data-hedron-*` markers).
- Layout gaps no longer require inline `--hedron-gap` styles under strict CSP.
- `Grid` / `GridItem` responsive tracks and spans; Text overflow/line-clamp without
  implicit `title` disclosure.
- `Surface`, AppShell chrome (`Brand`, `AccountSummary`, `EnvironmentBanner`,
  `NavStatus`, `AppFooter`), `ResourceList` / `ResourceRow`, core `Avatar` / `Identity`.
- FileUpload composition, Status compact/activity variants, richer ProcessFlow steps.
- Authenticated Data Mover chrome fixture with zero application CSS.

See [PRESENTATION](../api/PRESENTATION.md) and
[RELEASE_0_57](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_57.md).

The 0.57.0 PyPI upload remained deferred. Current applications should use
`hedron>=1.0.0,<1.1` from PyPI; the historical repository tip is `0.57.0`.

## Hardening on the tip

The in-tree tip also closes fail-closed regressions across maps policy, CSS/`@import`,
Unicode scheme smuggling, MCP authz, workspace search allowlists, idempotency cancel,
and related auth/cache edge cases. See [Release notes](release-notes.md).
