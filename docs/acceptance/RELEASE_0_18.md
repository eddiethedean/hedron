# Hedron `v0.18` model demos and inference workflows acceptance

Phase 0.18 delivers fail-closed model-demo composition, governed feedback, inference
scheduling over `JobBackend`, an interaction recorder, typed inference workflows, and
optional Gradio interop — without auto-publishing callables or embedding Gradio's UI
runtime. Evidence is indexed by [`release-gate-0.18.toml`](release-gate-0.18.toml).
**Zero Deferred:** every 0.18-owned gate row must be Verified at cut.

Owning RFCs: [RFC-0045](../rfcs/RFC-0045-INFERENCE-INTERFACE.md),
[RFC-0046](../rfcs/RFC-0046-MODEL-DEMO-PRESENTATION.md),
[RFC-0047](../rfcs/RFC-0047-INFERENCE-POLICY.md),
[RFC-0048](../rfcs/RFC-0048-INTERACTION-RECORDER.md),
[RFC-0049](../rfcs/RFC-0049-GRADIO-ADAPTER.md),
[RFC-0050](../rfcs/RFC-0050-INFERENCE-WORKFLOW.md). Decision: D-049.

## Spec packet

- [x] ROADMAP §0.18 scope accepted; Gradio cross-check refreshed (6.22.0 / 2026-08-06).
- [x] RFCs 0045–0050 Accepted.
- [x] Entry gate: 0.17 evidence remains closed; 0.18 gate TOML owns Planned→Verified rows only.
- [x] Gate checker recognizes `0.18` (`python scripts/check_release_gate.py 0.18.0`).

## Scenarios and inference

- [x] `ModelDemoScenario` synthetic kit. *(`SCENARIO-018`)*
- [x] `InferencePolicy` admission/queue/batch/concurrency/stream/cancel. *(`INFER-018`)*

## Demo, examples, presentation, feedback

- [x] `InferenceInterface` / `ModelDemo` fail-closed generation. *(`DEMO-018`)*
- [x] `ExampleSet` cache provenance/invalidation. *(`EXAMPLE-018`)*
- [x] `PredictionLabel` / `ParameterViewer` / `Dialogue`. *(`PRESENT-018`)*
- [x] `PredictionFeedback` consent/retention/redaction. *(`FEEDBACK-018`)*

## Recorder, workflow, Gradio, migration

- [x] `InteractionRecorder` redacted public snippets. *(`RECORD-018`)*
- [x] `InferenceWorkflow` authz/publish/adversarial. *(`WORKFLOW-018`)*
- [x] Optional `hedron-gradio` (experimental; deny-by-default discover). *(`GRADIO-018`)*
- [x] Gradio migration inventory without auto-conversion claims. *(`MIGRATE-018`)*

## Packaging

- [x] Coordinated package verify (`scripts/verify_pkg_18.py`). *(`PKG-018`)*

## Exit

- [x] Full regression suite. *(`REGRESS-018`)*

**Exit met** — coordinated `0.18.0` (**Published** as `v0.18.0`); every 0.18 gate row Verified.
