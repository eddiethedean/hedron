# RFC-0061: Reviewable Streamlit AST migration assistant

**Status:** Proposed

**Target phase:** 0.30 (`v0.30.0`)

**Related:** RFC-0017, RFC-0019, RFC-0024, RFC-0026; phase 0.15 Streamlit migration
matrix; [Streamlit migration guide](../guides/streamlit-migration.md); [ROADMAP
§0.30](../ROADMAP.md); tracking
[#88](https://github.com/eddiethedean/hedron/issues/88) (close when `MIGRATE-030` is Verified)

## Summary

Add `hedron migrate streamlit` as a deterministic, reviewable migration assistant. It
statically parses a Streamlit application, inventories its UI, execution, state, cache,
resource, and side-effect boundaries, and emits two things:

1. a new Hedron project for the subset that can be translated safely; and
2. a machine-readable migration report for every translated, scaffolded, unsupported,
   or ambiguous source construct.

The assistant does not execute the source application, mutate it, or promise behavioral
equivalence. It generates explicit routes, forms, actions, fragment regions, and state
ownership from evidence available in the syntax tree. Where syntax is insufficient, it
generates a safe placeholder or no code and records a blocking finding with a source span
and recommended manual decision.

The first release supports ordinary Python Streamlit entrypoints and statically discoverable
multipage files. Python remains the only input language and Hedron/FastAPI remains the output
host.

## Motivation and background

Hedron already has a maintained Streamlit API matrix, execution/state guidance, a worked
dashboard migration, and a production cutover checklist. Those materials correctly explain
that Streamlit's widget/rerun model is not equivalent to Hedron's request/action model. They
do not reduce the repetitive work of inventorying a real codebase, locating every state or
side-effect boundary, scaffolding routes, and proving that no unsupported call was silently
dropped.

A call-for-call transpiler would encode the wrong architecture. A reviewable assistant can
instead automate the mechanical portion while making architectural decisions visible. Its
primary product is a migration plan with traceability; generated code is one artifact of that
plan.

## Proposed design

### 1. Public CLI

The initial interface is:

```bash
hedron migrate streamlit streamlit_app.py --out hedron_app
hedron migrate streamlit path/to/project --out hedron_app
hedron migrate streamlit streamlit_app.py --analyze-only --format json
```

Common options:

| Option | Behavior |
|---|---|
| `SOURCE` | A Python entrypoint or project directory |
| `--out PATH` | New output directory; required unless `--analyze-only` |
| `--project-root PATH` | Explicit boundary for local-module discovery |
| `--analyze-only` | Produce the report without generating a project |
| `--format text\|json\|sarif` | Human, automation, or code-scanning report |
| `--python-version 3.11\|3.12\|3.13\|3.14` | Parser grammar for the input source |
| `--fail-on information\|warning\|error` | CI threshold for findings |

Exit status `0` means analysis/generation completed below the configured finding threshold,
`1` means the tool could not safely parse, resolve, or write the migration, and `2` means a
report was produced but findings meet or exceed the configured threshold. A generated project
may therefore exist after exit `2`; its report remains the authority on readiness.

The command refuses an existing non-empty output directory. Version one has no in-place,
merge, or force-overwrite mode. Re-running uses a fresh output directory.

### 2. Static discovery without execution

The assistant uses Python's AST and a small static symbol resolver. It recognizes imports such
as `import streamlit as st`, `from streamlit import ...`, statically assigned aliases, calls
through `st.sidebar`, decorators, widget-result assignments, and direct `st.session_state`
access. It follows local imports only when they resolve beneath `--project-root` and remain
within configured file/node limits.

Analysis never:

- imports or executes the application;
- imports Streamlit or third-party application dependencies;
- evaluates decorators, callbacks, f-strings, default factories, or module globals;
- opens paths mentioned by application code;
- follows symlinks outside the project root; or
- contacts a network service.

Dynamic `getattr`, monkeypatching, runtime import construction, generated Python, and calls
whose Streamlit identity cannot be proven receive findings rather than speculative rewrites.

### 3. Versioned migration IR

AST nodes normalize into a versioned `StreamlitMigrationPlan`. The public CLI report is stable
JSON; the Python IR begins at `beta` and is not part of Hedron's minimal stable facade.

The plan contains:

- `SourceUnit` and `SourceSpan` records with content hashes;
- pages, navigation, layout scopes, and display operations;
- controls, forms, callbacks, and dependency edges from control values to outputs;
- writes and other side effects, including their control-flow guards;
- session-state reads/writes and inferred ownership candidates;
- cache/resource decorators and call sites;
- custom components, HTML/Markdown trust boundaries, files, secrets, and external services;
- dependency dispositions and required Hedron extras; and
- generated-artifact/source-map records.

Every operation has a stable ID, source span, mapping disposition, confidence, and zero or more
findings. Dispositions are:

| Disposition | Meaning |
|---|---|
| `translated` | Deterministic mapping with no unresolved semantic choice |
| `scaffolded` | Safe Hedron structure generated, but application logic requires review |
| `report_only` | No output code; the report explains the required redesign |
| `unsupported` | No supported Hedron equivalent or insufficient static evidence |

Confidence is not a probability. It is the closed vocabulary `exact`, `bounded`, or
`ambiguous`, defined by mapping rules and tested fixtures.

### 4. Mapping registry

Mappings live in a versioned, inspectable registry rather than a chain of ad hoc visitor
conditions. Each mapping declares recognized Streamlit symbols and versions, required argument
shapes, Hedron imports/extras, IR output, code-generation rule, findings, and parity notes. The
registry can power the existing Streamlit migration matrix so prose and tooling do not drift.

The first Supported mapping inventory is deliberately narrow:

| Streamlit pattern | Initial Hedron result |
|---|---|
| Titles, headings, text, Markdown without unsafe HTML | `Heading`, `Text`, or bounded Markdown/content mapping |
| Metrics and ordinary tables/dataframes | `Metric`, `Table`, or `DataTable` with an explicit dependency finding when data shape is unknown |
| Columns, containers, sidebar, tabs, and expanders | Typed layout components with semantic-order review |
| Simple select, multiselect, slider, checkbox, text, number, and date inputs | Typed GET form by default; POST only when mutation evidence requires it |
| `st.form` and submit button | Explicit Hedron `Form`; unsafe methods include `CsrfField` |
| Simple button-guarded mutations | Named POST action scaffold with the side effect left in an application-owned function or marked for extraction |
| Statically declared pages/navigation | Hedron page routes with a URL review ledger |
| Common charts | Conservative static/Matplotlib path when representable; interactive adapters remain explicitly Experimental |

The assistant must not infer authorization from control flow, mark arbitrary HTML trusted,
turn a cache into a database/session, or copy all `st.session_state` into one Hedron session.

### 5. Execution, state, and side-effect analysis

Streamlit control declarations, control values, callbacks, and later statements are connected
in a dependency graph. The assistant uses that graph to propose one of these owners:

- URL/query state for shareable filters;
- request/form state for one submission;
- server session for bounded user-specific continuity;
- database or application service for durable/domain state;
- cache/resource lifecycle for recomputable/shared values; or
- browser preference for non-secret, non-authoritative presentation state.

Only URL and request/form ownership may be selected automatically in the initial inventory, and
only when the mapping rule is exact. Other candidates are recommendations requiring review.

Side effects interleaved with display code, callback mutations, session-state mutation, rerun/
stop control flow, uploads, downloads, authentication, secrets, custom components, and raw HTML
are never silently copied. They receive a stable `HED-MIG-ST-*` finding. A generated action stub
must fail closed or remain unreachable until its TODO is resolved; it cannot pretend the mutation
was ported.

### 6. Generated project and provenance

For a successful generation, the output has this minimum shape:

```text
hedron_app/
├── app.py
├── pyproject.toml
├── migration/
│   ├── report.json
│   ├── source-map.json
│   └── REVIEW.md
└── tests/
    └── test_migration_smoke.py
```

The scaffold uses the current bounded Hedron pin, public imports, `security="standard"`, an
environment-owned session secret, and ordinary Uvicorn startup. Generated code contains stable
source-map markers but no copied secrets or machine-specific absolute paths. `REVIEW.md` groups
findings by user workflow and provides commands for running and testing the candidate.

`report.json` records input hashes, tool/schema/mapping versions, source spans, mappings,
findings, dependency dispositions, and emitted file hashes. That provenance lets reviewers prove
which source revision was analyzed. It is not a merge manifest and does not authorize overwriting
hand-edited output.

### 7. Diagnostics

Findings use the existing text, JSON, and SARIF conventions and a dedicated `HED-MIG-ST-*`
namespace. Each finding includes severity, stable code, source path/span, construct, disposition,
reason, remediation, and related generated span where present.

Required initial families include:

- unresolved/dynamic Streamlit symbol;
- unsupported or version-unknown API;
- ambiguous widget-state owner;
- callback or rerun control flow;
- interleaved or duplicate side effect;
- cache/resource lifecycle review;
- raw HTML, unsafe URL, file, secret, or external-component boundary;
- authentication/authorization/tenant boundary;
- accessibility label/order/fallback review; and
- dependency/hosting non-parity, including Community Cloud.

No success summary may hide warning/error counts. A generated application with blockers prints
`REVIEW REQUIRED` and exits according to `--fail-on`.

### 8. Extensibility boundary

The nested `hedron migrate streamlit` command leaves room for future analyzers, but phase 0.30
ships only Streamlit. Mappings are first-party code and data, not executable third-party plugins.
Supporting third-party migration rules would require a separate trust and compatibility design.

An optional AI explanation layer may be explored later, but it cannot alter the deterministic
plan or generated files in the Supported path. The AST, registry, report, and code generator are
the reproducible authority.

## Alternatives considered

### Import and instrument the Streamlit application

Rejected for the default tool. Importing can execute arbitrary module-level code, connect to
services, read secrets, mutate data, or hang. A future opt-in capture harness would require a
separate sandbox and consent contract.

### Provide a Streamlit compatibility shim

Rejected. It would recreate rerun/session semantics inside Hedron, obscure request and security
boundaries, and make generated applications dependent on a second runtime.

### Rewrite calls with regular expressions

Rejected. Regex cannot reliably resolve aliases, scopes, control flow, callbacks, or state
dependencies and would silently mis-handle valid Python.

### Use CST rewriting in place

A CST may be useful later for comments or targeted framework-free extraction, but in-place
rewriting is not the initial product. A new generated project plus source map is safer and makes
the architecture change visible.

### Make an LLM the converter

Rejected as the Supported authority. Model output is not deterministic enough for source
coverage, no-drop guarantees, stable diagnostics, or reproducible review. An assistant may
explain findings only as a clearly optional layer.

### Keep migration fully manual

Viable but unnecessarily repetitive. Static inventory, mapping, scaffolding, and source
traceability are deterministic work that the project can test and support.

## Security implications

- Input is untrusted source text. Parsing is bounded by file count, byte count, AST node count,
  recursion depth, and elapsed time.
- Local import resolution stays below the resolved project root and rejects escaping symlinks.
- The analyzer never executes source or opens application-referenced paths.
- Diagnostics redact likely secret values and do not embed full environment-specific paths in
  portable reports.
- Generated Markdown/HTML never becomes `TrustedHtml` solely because Streamlit accepted
  `unsafe_allow_html=True`; that call is a blocker.
- Generated mutations require explicit POST, CSRF, validation, and application-owned
  authorization. The tool never infers identity or tenant scope.
- Output uses atomic staging and an absent/empty destination. It never overwrites source or a
  hand-edited migration.
- SARIF/JSON fields are escaped and bounded so malicious source text cannot inject terminal,
  Markdown, HTML, or code-scanning payloads.

## Accessibility implications

The mapping registry records semantics, labels, keyboard behavior, source order, status/error
announcements, chart/table alternatives, and no-JavaScript fallback requirements. Missing or
dynamic labels, visual-only column ordering, inaccessible custom components, and charts without
an equivalent textual/table result generate findings.

Generated controls use native semantics and explicit labels. The tool does not claim WCAG
conformance, preserve an inaccessible behavior for parity, or treat automated analysis as human
assistive-technology evidence.

## Performance implications

Static analysis should be linear in total parsed source plus bounded local-import edges. The CLI
publishes default limits for files, bytes, AST nodes, import depth, and analysis time, with
actionable diagnostics when exceeded. It does not load datasets or import heavyweight application
dependencies.

Acceptance includes representative single-file, multipage, and adversarial projects; cold/warm
timings; peak memory; deterministic output; and a large-project refusal case. Performance claims
cover analysis and code generation, not the runtime performance of the migrated application.

## Testing strategy

- Unit tests cover alias/scope resolution, spans, dependency graphs, dispositions, confidence,
  diagnostics, redaction, path containment, and every mapping rule.
- Golden fixtures cover supported, scaffolded, report-only, and unsupported examples across the
  declared Python and Streamlit syntax matrix.
- Property/adversarial tests cover malformed/deep ASTs, encoding, giant literals, symlinks,
  dynamic imports, terminal/SARIF injection, secret-shaped values, and deterministic limits.
- Integration tests run the generated Hedron scaffold, assert routes/forms/CSRF/fragment policy,
  and verify no Streamlit runtime dependency remains.
- Outcome fixtures compare reviewed Streamlit `AppTest` results with Hedron TestClient/
  `AppScenario` results for the bounded Supported mappings. This comparison runs in tests; the
  migration CLI itself still does not execute the source.
- Snapshot tests prove deterministic reports, source maps, generated code, and idempotent analysis
  for identical source hashes.
- Packaging tests prove the CLI works without Streamlit installed and reports optional Hedron
  extras accurately.

## Compatibility and migration

The command and report schema begin at `beta`. Reports include a schema version and mapping-catalog
version; readers reject incompatible major schema versions. New mapping rules are additive unless
they would change an existing exact disposition, in which case release notes and golden upgrade
fixtures are required.

The analyzer declares the Streamlit API documentation/runtime ranges audited for each catalog
version. Unknown/newer calls are reported, not guessed. Generated projects pin the current Hedron
train through the same release metadata as `hedron new`.

The source application remains untouched and can continue running during acceptance. The generated
Hedron application uses a separate directory, process, hostname/path, and deployment until the
existing cutover checklist is complete.

## Open questions

1. Should `--project-root` default to the entrypoint parent or the nearest `pyproject.toml` when
   both are present?
2. Should phase 0.30 include bounded extraction of proven Streamlit-free functions into a generated
   `domain.py`, or only reference their original modules until the developer extracts them?
3. Which exact Streamlit versions form the first mapping-catalog compatibility window?
4. Should warnings make the default exit status `2`, or only errors, while keeping
   `--fail-on` configurable?
5. Is SARIF emitted directly by `hedron`, or through the existing diagnostics adapter shared with
   `hedron check`?

These questions must be closed before the RFC moves from Proposed to Accepted.

## Acceptance criteria

- `hedron migrate streamlit` analyzes without importing/executing the source or requiring
  Streamlit to be installed.
- The versioned mapping inventory covers the declared phase-0.30 subset and agrees with the public
  Streamlit migration matrix.
- Every recognized Streamlit call receives a disposition; no call is silently dropped.
- Generated projects use public Hedron APIs, bounded pins, secure defaults, explicit routes/state,
  and no Streamlit runtime dependency.
- Text, JSON, and SARIF reports are deterministic, redacted, source-mapped, and schema-versioned.
- Existing/non-empty destinations are refused and source files remain byte-identical.
- Security, accessibility, performance, adversarial, golden-upgrade, packaging, and outcome-parity
  suites pass for the Supported mapping inventory.
- The runnable sales-dashboard migration can be regenerated to the reviewed reference outcome,
  with any intentionally manual decisions represented by stable findings.
- The phase `MIGRATE-030` gate is Verified before the tool is called tooling-grade or Supported.
