# RFC-0050: Versioned permissioned inference workflows

**Status:** Accepted
**Phase:** 0.18 (`v0.18.0`)
**Stability:** `beta` (API); structured non-canvas editor is the Supported UI
**Evidence:** `WORKFLOW-018`
**Related:** [Gradio feature cross-check](../GRADIO_FEATURE_CROSSCHECK.md);
RFC-0012, RFC-0013, RFC-0026, RFC-0040, RFC-0045, RFC-0047, RFC-0049; D-049

## Summary

Define an optional typed visual inference workflow with versioned JSON, stable node/port
identities, explicit operator kinds, and separate read/run/edit/publish authority. Graph data
cannot execute arbitrary Python, install packages, access host paths, or automatically create
HTTP/MCP endpoints. A structured list/outline/table editor exposes the graph without requiring a
visual canvas or drag gesture.

## Motivation and background

Gradio Workflow demonstrates demand for composable AI pipelines. Hedron must adopt that outcome
with schema/version migration, authorization, tenant scope, secret references, immutable publish,
and adversarial resistance — reusing explicit actions and `InferencePolicy` rather than a second
code-execution runtime.

## Proposed design

### Workflow graph

- Versioned JSON with stable node/port identities.
- Node kinds: reference/input; action/model/remote/dataset operator; artifact/output.
- Validation, cycle detection, fan-out/fan-in, parallel scheduling via inference policy,
  cancellation, partial failure, provenance, and cost/resource diagnostics.
- Graphs reuse the same action and inference contracts as demos (RFC-0045 / RFC-0047).

### Permissions and revisions

- Separate read / run / edit / publish permissions.
- Tenant scope, secret references, optimistic conflict detection, audit, rollback, and immutable
  published revisions are mandatory.
- Editable and published graphs have distinct authorization; editable URLs without identity,
  authorization, revision, and audit policy are prohibited.

### Structured non-canvas editor

A Supported list/outline/table editor exposes nodes, ports, connections, order, parameters, and
results without requiring a visual canvas or drag gesture. A canvas may ship later as enhancement
but is not required for Verified (`WORKFLOW-018`).

### Hard prohibitions

Graph data cannot:

- execute arbitrary Python or install packages;
- access host paths;
- automatically create HTTP or MCP endpoints.

Optional Hugging Face vendor nodes remain adapters over this portable contract (RFC-0049).

## Alternatives considered

1. **JSON that executes host code or edits deployed files.** Rejected — D-049 deliberate
   non-parity with vibe/host-code modes.
2. **Canvas-only editor with no structured alternative.** Rejected — accessibility and
   no-drag Supported path require list/outline/table editing.
3. **Auto-publish workflow nodes as HTTP/MCP endpoints.** Rejected — exposure remains explicit.

## Security implications

Authorization is rechecked for run/edit/publish. Secret references never inline credentials into
graph JSON. Adversarial suites cover arbitrary code, host paths, and auto-exposure. Tenant
isolation and rollback are mandatory for published revisions.

## Accessibility implications

The structured editor is the Supported accessible path: keyboard operable, focus-preserving, with
non-spatial views of nodes/ports/connections. Any future canvas must provide equivalent
non-spatial alternatives.

## Performance implications

Parallel scheduling reuses inference admission/concurrency groups. Provenance and cost diagnostics
are inspectable without unbounded artifact retention. Replay/adversarial suites must not depend on
timing sleeps.

## Testing strategy

Schema/version migration, identity, type, cycle, authorization, tenant, secret, edit conflict,
immutable publish, rollback, parallel/failure, cancellation, remote-call, provenance,
API-exposure, and arbitrary-code/path adversarial suites (`WORKFLOW-018`).

## Compatibility and migration

Additive optional APIs. Existing actions and demos remain valid without workflows. Gradio Workflow
inventories map without automatic conversion (`MIGRATE-018`).

## Open questions

None blocking Acceptance. Visual canvas polish may remain experimental until a11y equivalence
evidence lands; structured editor Verified is sufficient for phase exit.

## Acceptance criteria

- Workflow graphs pass the schema, authz, publish/rollback, and adversarial suites above.
- Structured non-canvas editor is Supported; canvas is not required for Verified.
- Graph JSON cannot execute host code, touch host paths, or auto-publish endpoints.
- Gate evidence under `WORKFLOW-018`.
