# What's new in 0.58

!!! note "Historical release note"

    This page records the 0.x release named in its title. For current installation,
    support, and 1.0 candidate status, use [Current release and support](current-release.md).
    Keep the historical pins below only when maintaining that release line.

Phase **0.58** (`v0.58.0` on PyPI) lands progressive feature and styling
authoring under
[RFC-0085](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0085-PROGRESSIVE-FEATURE-AUTHORING.md)
(D-101 / D-102 / D-105).

## Highlights

- Beginner facades: `Hedron.screen`, `Hedron.form_command`, `DataWorkspace.with_screen`,
  `TaskFlow`, `DashboardWorkspace`, `SessionAuthFlow`, and `UploadFlow` — each lowers to
  existing page/command/bundle/job/auth/upload authorities.
- `DesignSystem.brand` compiles a coordinated light/dark `Theme` from one hex accent;
  `StyleRecipe` families (`control` / `surface` / `data` / `status` / `content`) and
  built-in feature roles; explicit `StyleScope` for theme/color-mode/density.
- Shared explain / preview / diff / check / eject CLI (`hedron explain`, `hedron style …`)
  with redacted provenance and safe ejection.
- FastAPI scaffolds: `hedron new NAME --template minimal|crud|dashboard|task`.

See [RELEASE_0_58](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_58.md)
and
[PROGRESSIVE_AUTHORING_058](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/PROGRESSIVE_AUTHORING_058.md).

Install from PyPI with `hedron>=0.58.0,<0.60`; the repository tip is `0.58.0`.
