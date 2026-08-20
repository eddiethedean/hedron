# RFC-0081: Authoring loop and application chrome

**Status:** Accepted<br>
**Target phase:** 0.54 (`v0.54.0`)<br>
**Decision:** D-093<br>
**Stage 0 contract refine:** D-094<br>
**Planning baseline:** Published in-tree `v0.53.0`<br>
**Required predecessor/cut baseline:** Verified in-tree `v0.53.0`<br>
**Tracking:** [#538](https://github.com/eddiethedean/hedron/issues/538)–[#543](https://github.com/eddiethedean/hedron/issues/543);
companions [#523](https://github.com/eddiethedean/hedron/issues/523)–[#537](https://github.com/eddiethedean/hedron/issues/537)
(epic [#528](https://github.com/eddiethedean/hedron/issues/528))<br>

**Revision:** 2026-08-20 — D-093 ownership + D-094 Stage 0 refine against
Published in-tree `v0.53.0`. No Stage 0 runtime, version bump, or registry claim.

## Summary

Phase 0.54 turns the notebook preview, offline simulator, and sample plugin into
one coherent external-author loop, and delivers Python-native application chrome /
design-system companions so a Data Mover-class front end is reproducible with
Hedron components and Python configuration while Hedron owns CSS.

Acceptance requires: **copy a minimal sample → inspect its manifest → run it in
the simulator → preview it in a notebook → hand it to a real development server →
run the package doctor**. The same fixture and diagnostics must survive each
boundary.

## Goals

- Refresh `hedron-sample-kit` with modular modern variants removable independently.
- Give `hedron-sim` a machine-readable supported-subset/divergence manifest;
  unsupported behavior fails visibly.
- Extend `hedron-notebook` with display handles, multi-view sessions, static
  fallbacks, and opt-in real-server handoff without public hosting.
- Add `hedron package doctor` for external package-author validation (distinct
  from 0.53 `hedron fleet`).
- Share fixtures/diagnostics across sample-kit, sim, notebook, doctor, and
  overlapping `AppScenario` semantics via public
  `hedron_conformance.authoring_loop` contracts.
- Deliver companion presentation primitives (#523–#537) and prove them through
  the authoring loop plus a zero-application-CSS reference fixture (#528).

## Non-goals and exclusions

- Public notebook hosting or turning localhost preview into a Supported server.
- A general-purpose browser automation engine or silent simulator parity.
- Private-import compatibility for third-party packages.
- A new CSS escape hatch for application authors on the #528 path.
- Replacing Explorer, the 0.53 fleet doctor, or the stable facade.
- Reopening `polling_only`, `MORPH-048`, `SR-021`, adapter dispositions, or
  scheduling Hedron `1.0`.
- Runtime symbols, numeric performance limits, version bumps, or living-tip
  movement during Stage 0.

## Consume shipped, do not fork (D-094)

| Area | Published 0.53 seams retained |
|---|---|
| Sample kit | `hedron-sample-kit` `0.1.10` Callout plugin, `hedron.plugins` entry, Explorer panel |
| Simulator | `SimApp`, `embed_demo`, `subset.require_supported_*`, `UnsupportedSimFeatureError` |
| Notebook | `start_preview`, `NotebookPreview`, token gate, localhost-only defaults |
| Fleet vs doctor | `hedron fleet` / Explorer package health with `package_doctor: False` |
| Theme / chrome | `Theme`, `REQUIRED_A11Y_TOKENS`, `AppShell`, layout builtins, `default_styles` |
| Application DX | RFC-0080 assets/diagnostics/routes/workflow/testgen/theme/discover/fleet |

Public shared schema import path (locked): **`hedron_conformance.authoring_loop`**.

## Locked gate plan

| Gate | Verified means |
|---|---|
| `SAMPLE-054` | Modular modern sample-kit examples pass from public contracts. |
| `DOCTOR-054` | `hedron package doctor` checks pass from a clean external-style consumer. |
| `SIM-054` | Declared subset, divergence, recording/time control, and deterministic scenarios pass. |
| `PARITY-054` | Real-server/browser differential parity fixtures pass. |
| `NOTEBOOK-054` | Display handles, saved fallbacks, and bounded sessions pass. |
| `LIFECYCLE-054` | Repeated execution, interrupt/restart/stale/close, and cleanup pass. |
| `SECURITY-054` | Token/origin/host/proxy/port/iframe/output/temp/browser-open boundaries pass. |
| `TOPOLOGY-054` | Non-loopback rejection and printed security/topology disposition pass. |
| `ECOSYSTEM-054` | Explorer/HDJ/Elements/conformance/adapters/examples interoperate without private imports. |
| `COMPAT-054` | Missing-extra, min/max, and current-previous matrices pass. |
| `PLATFORM-054` | Python/OS/kernel/frontend/saved-output matrices pass. |
| `A11Y-054` | Static/rich output and companion fixture accessibility evidence pass. |
| `DOCS-054` | Author, simulator, notebook, security, migration, troubleshooting, and publishing docs pass. |
| `PKG-054` | Clean artifacts, metadata, reproducibility, and 0.53 upgrade/rollback pass. |
| `REGRESS-054` | Whole-fleet regression passes with no hidden Deferred 0.54 claims. |

Companion issues #523–#537 fold evidence into `ECOSYSTEM-054`, `A11Y-054`, and
`DOCS-054` plus the #528 reference fixture. They do not add gate IDs.

## Security implications

Notebook remains localhost/token-gated by default; non-loopback serving is rejected.
Simulator input, URL, HTML, event, history, and recording imports are bounded with
deterministic failure codes. Package doctor is read-only validation of package
metadata and artifacts; it does not install or enable plugins. Tokens and local
paths are redacted from saved notebook outputs and logs.

## Testing strategy

The evidence index names `scripts/check_*_054.py` commands. Stage 0 rows are
`Planned`; Stage 1 supplies implementations and Verified evidence. PKG-054
upgrade source is 0.53 (`v0.53.0`).

## Resolved questions (D-093 / D-094)

1. **Who owns 0.54?** RFC-0081 under D-093, with foundation issues #538–#543 and
   companions #523–#537 bound.
2. **What is the baseline?** Published/Verified in-tree `v0.53.0`; target
   `v0.54.0`.
3. **Shared schema path?** `hedron_conformance.authoring_loop`.
4. **Which doctor is this?** External package-author `DOCTOR-054`, not fleet.
5. **Does Stage 0 change runtime or versions?** No.

Locks:
[authoring-loop-inventory-054.toml](../acceptance/authoring-loop-inventory-054.toml) ·
[authoring-shared-054.toml](../acceptance/authoring-shared-054.toml) ·
[authoring-sim-notebook-054.toml](../acceptance/authoring-sim-notebook-054.toml) ·
[authoring-chrome-054.toml](../acceptance/authoring-chrome-054.toml).

## Acceptance criteria

- RFC-0081 and D-093/D-094 are Accepted; #538–#543 and #523–#537 are bound.
- Every owned gate is Planned with an evidence command.
- All four contract locks parse and agree on baseline, target, and boundaries.
- Stage 0 changes contracts only; living tip remains `v0.53.0`.
