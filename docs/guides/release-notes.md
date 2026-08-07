# Release notes

Adopter-facing summary for the **0.18.x** train. For per-package commit detail, use the
[package changelog index](changelog.md) or
[GitHub Releases](https://github.com/eddiethedean/hedron/releases).

## Current train — 0.18.0 (2026-08-06)

**Published** (`v0.18.0`). Model demos and inference workflows: `InferenceInterface` /
`ModelDemo`, `ExampleSet` / presentation builtins / `PredictionFeedback`, `InferencePolicy`
over `JobBackend`, `InteractionRecorder`, `InferenceWorkflow` with structured editor, and
optional Alpha `hedron-gradio` (Experimental).

Narrative deep-dive: [What's new in 0.18](whats-new-0.18.md) · maturity:
[What's ready today](whats-ready.md) · Gradio: [Gradio migration](gradio-migration.md).

```bash
pip install -U "hedron>=0.19.0,<0.20"
# or
uv add "hedron>=0.19.0,<0.20"
```

Optional: `pip install "hedron[gradio]>=0.1.0,<0.2"` · `"hedron[notebook]>=0.1.0,<0.2"` · `"hedron[mcp]>=0.1.0,<0.2"`.

## Earlier trains

| Train | Summary | Narrative |
|---|---|---|
| **0.17** | Reactive dashboards / agent interfaces | [What's new in 0.17](whats-new-0.17.md) |
| **0.16** | Curated extras / workbenches | [What's new in 0.16](whats-new-0.16.md) |
| **0.15** | Data-app surface completeness | [What's new in 0.15](whats-new-0.15.md) |
| **0.14** | Portable runtimes / acceleration | [What's new in 0.14](whats-new-0.14.md) |
| **0.13–0.10** | Async/observability → live interaction | Archive links in nav / [changelog](changelog.md) |

Upgrade paths: [Upgrade guide](upgrade.md) (0.8 → 0.18).
