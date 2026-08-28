# What's new in 0.54

!!! note "Historical release note"

    This page records the 0.x release named in its title. For current installation,
    support, and 1.0 candidate status, use [Current release and support](current-release.md).
    Keep the historical pins below only when maintaining that release line.

**Status:** Published in-tree as `v0.56.0` (tag/PyPI deferred). This historical
cut was superseded by later published trains; current applications should use
`hedron>=0.66.2,<0.67` from the public index.

Phase 0.54 ships one external-author loop and Python-native application chrome.

## Authoring loop

- Modular `hedron-sample-kit` variants (pure Python, Web Component + SSR fallback,
  workflow, HDJ binding, optional integration).
- `hedron package doctor` for external package-author validation (distinct from
  `hedron fleet`).
- `hedron-sim` machine-readable subset/divergence, recording/time control, and
  HTTP/browser parity helpers.
- `hedron-notebook` display handles, multi-view sessions, static fallbacks, and
  opt-in real-server handoff with topology honesty.
- Shared schema: `hedron_conformance.authoring_loop`.

## Application chrome (#523–#537)

- Layout: `PageHeader`, `SplitView`, `FormGrid`, `ActionGroup`.
- `AppShell` production chrome slots; `SkipLink` / `RequestIndicator`.
- `ProcessFlow` / `FlowStep`; `Icon`; typography roles; palette compiler;
  theme inheritance; shared appearance vocabulary; overlay elevation;
  `StateView`; production `Table` / `DescriptionList`.
- `hedron theme check` and `hedron style check --zero-app-css`.
- Reference fixture: `examples/chrome-zero-css/`.

## Honesty

Notebook and simulator stay tooling-grade. Live transport remains `polling_only`.
No Hedron `1.0`. See [package author handbook](package-author-handbook.md).
