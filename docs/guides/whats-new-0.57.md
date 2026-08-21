# What's new in 0.57

Phase **0.57** (`v0.57.0` in-tree; tag/PyPI deferred) lands unified presentation and
zero-application-CSS evidence under
[RFC-0084](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0084-UNIFIED-PRESENTATION.md).

## Highlights

- Shared appearance vocabulary extended with `plain` / `raised`, width, overflow, track,
  and CSP-safe gap tokens (`data-hedron-*` markers).
- Layout gaps no longer require inline `--hedron-gap` styles under strict CSP.
- `Grid` / `GridItem` responsive tracks and spans; Text overflow/line-clamp without
  implicit `title` disclosure.
- `Surface`, typed AppShell chrome (`Brand`, `AccountSummary`, `EnvironmentBanner`,
  `NavStatus`, `AppFooter`), `ResourceList` / `ResourceRow`, core `Avatar` / `Identity`.
- FileUpload composition, Status compact/activity variants, richer ProcessFlow steps.
- Authenticated Data Mover chrome fixture with zero application CSS.

See [PRESENTATION](../api/PRESENTATION.md) and
[RELEASE_0_57](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_57.md).

Pin from PyPI remains `hedron>=0.56.0,<0.58` until the 0.57.0 wheel lands; the repository
tip is `0.57.0`.

## Hardening on the tip

The in-tree tip also closes fail-closed regressions across maps policy, CSS/`@import`,
Unicode scheme smuggling, MCP authz, workspace search allowlists, idempotency cancel,
and related auth/cache edge cases. See [Release notes](release-notes.md).
