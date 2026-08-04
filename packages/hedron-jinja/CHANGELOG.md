# Changelog

## [0.9.0] - 2026-08-04

- Replace the removed HDN language with HDJ, an explicit standards-first `.hdj` format whose static
  prologue declares template kind, feature profile, and required capabilities before a Jinja body.
- Add typed template specifications, explicit component bindings, component/body/slot tags,
  one shared core render session, and HTML-body/purpose-specific URL trust filters.
- Add the mandatory prologue parser, `.hdj`-only guarded loader, static dependency/kind checks,
  capability-versus-policy diagnostics, registered assets, and bounded chunk consumption.
- Reject direct rendering, dynamic/foreign format-v1 dependencies, and conditional page assets;
  later-phase ownership is recorded in RFC-0031 and the roadmap.
