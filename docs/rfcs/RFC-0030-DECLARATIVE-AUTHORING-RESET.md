# RFC-0030: Declarative authoring reset

**Status:** Superseded by [RFC-0031](RFC-0031-JINJA-INTEGRATION.md)

> **Outcome:** This reset established the design hold and evaluated the credible directions.
> RFC-0031 selects an optional Jinja integration, keeps Python components authoritative, and
> defines the phase 0.9 Jinja replacement and immediate HDN removal boundary. The audit below is a
> historical record of why the old implementation was not extended.

## Summary

Hedron should stop extending the current HDN language and reconsider declarative component
authoring from first principles. The immediate decision is a **design hold**, not a replacement
syntax: Python components remain the supported authoring model, current HDN APIs and artifacts are
classified experimental, and no new HDN grammar, bytecode, import, formatter, or editor contract is
accepted while this RFC remains Draft.

This review starts with a more basic question than “what should HDN syntax look like?”:

> Does Hedron need a separate template language at all, and what user job would justify owning one?

The superseding phase 0.9 authoring gate selects a smaller replacement through an accepted revision
of this RFC or remove the custom language after a documented migration window.

## Motivation and background

The product promise is already satisfied for onboarding and ordinary applications by typed Python
components, built-ins, native HTML nodes, HTMX, and scoped styles. A second language is justified
only if it materially improves one or more validated jobs:

1. precise HTML-oriented layout authoring;
2. collaboration with people who should not need to edit Python component logic;
3. build-time validation of component props, slots, styles, assets, and accessibility;
4. inspectable/ejectable customization of built-in presentation; or
5. portable component packages whose declarative surface is substantially easier to audit than
   Python.

The current implementation has not yet demonstrated those benefits. Repository usage is narrow:
the reference proof manually calls `compile_hdn()` and `run_program()`, while component discovery
records a source path but does not make an HDN file a complete typed component implementation.

### Audit of the current design

| Intended property | Current implementation evidence | Consequence |
|---|---|---|
| Typed component language | Component tags are resolved from a runtime `Mapping[str, Any]`; props and slots are not checked against component schemas during compilation. | Misspelled or invalid component calls fail late. |
| Safe, closed expressions | Expressions are parsed with Python `ast` and evaluated against arbitrary Python objects. Attribute access, indexing, membership, `len`, `str`, `int`, and `bool` can invoke user-defined Python protocols. | Rejecting explicit call nodes does not create a closed or side-effect-free evaluation model. |
| Bounded execution | Parser fuzzing has a time check, but loops, input collections, property access, helper work, node count, and output size are not governed by one HDN execution budget. | A valid template can still perform unbounded work. |
| HTML-first semantics | Hedron owns a custom lexer/parser rather than a specified HTML parsing model. HTML error recovery, void/raw-text elements, entities, namespaces, and browser-equivalent tree construction are not fully defined. | Familiar-looking markup can have unfamiliar semantics. |
| Compiled production artifact | The flat render program retains expression source strings and evaluates them at runtime. Child regions are encoded by opcode counts rather than a typed tree. | The artifact is a serialized interpreter program, not a fully resolved typed component plan. |
| Explicit dependencies | Component resolution is still host-supplied and only lightly integrated with registry schemas, packages, or build-manifest compatibility. | Dependency metadata does not guarantee executable resolution. |
| Source tooling | Source maps record operation start locations; the parser fails fast and the formatter reconstructs syntax from a lossy AST. | Full-span diagnostics, recovery, safe refactors, and editor tooling would require substantial redesign. |
| Product leverage | Roughly 1,700 lines of core parser/compiler/runtime code support a narrow parity example and several direct API tests. | Language ownership cost is high relative to demonstrated user value. |

The gap is architectural. Adding imports, operators, recovery, or language-server features to the
current stack would deepen the commitment before the product requirement and safety model are
settled.

## Design principles for any replacement

1. **Python remains authoritative.** Business rules, derived values, I/O, authorization, and
   component registration live in typed Python.
2. **No arbitrary object graph.** Declarative rendering consumes a closed value algebra or a
   compiled view-model schema, never unrestricted `Any` plus Python attribute semantics.
3. **No expression language by default.** Derived values belong in Python. If conditions or
   repetition are proven necessary, they operate only on compiled field references and bounded
   collections—not operators, calls, reflection, or helper registries.
4. **Schemas resolve at build time.** Component identity, props, slots, styles, and asset
   dependencies are validated against the registry before an artifact is accepted.
5. **HTML semantics are explicit.** Select and document either standards-compatible HTML parsing or
   a deliberately restricted markup grammar. Do not let browser familiarity imply unspecified
   behavior.
6. **The IR is typed and structural.** A replacement artifact contains resolved node/prop/slot
   operations and numeric field references, not source expressions for a runtime evaluator.
7. **One execution budget.** Depth, nodes, repetitions, collection sizes, string sizes, output, and
   evaluation steps share enforceable limits and observable diagnostics.
8. **Tooling follows the language.** Formatter, source maps, recovery, LSP, conversion, and visual
   tooling are not built until the core authoring model is accepted.
9. **No runtime/compiler identity requirement.** The production runtime should not need the source
   parser, formatter, or compiler package.
10. **The smallest useful surface wins.** If Python composition is clearer for representative
    applications, Hedron should remove the second language.

## Candidate directions

### A. Python-only authoring

Remove HDN after migration and invest in the Python HTML/component experience: more concise native
tag construction, typed props/slots, better `inspect` output, reusable layout helpers, and optional
code generation.

This is the baseline and lowest-cost choice. It preserves one language, one type system, one
debugger, and one component execution model. It does not directly serve non-Python template authors.

### B. Layout-only declarative components

Prototype a deliberately small, HTML-oriented layout format compiled against a Python-declared
component and view-model schema. The prototype may support:

- native elements selected by an explicit HTML schema;
- component aliases supplied by the owning Python component/package, not imports in template text;
- static attributes and exact field bindings such as a prop, local item, or slot;
- typed child and named-slot placement;
- optional condition/repetition constructs limited to boolean/list field references and the common
  execution budget; and
- an explicit trusted-content binding whose schema type is `TrustedHtml`.

It must not initially support arithmetic, comparisons, helper calls, method/property execution,
module imports, dynamic attribute/tag names, arbitrary mappings, or source expressions in the
production artifact. File extension and surface syntax remain open until parser prototypes and user
examples are compared.

This is the preferred prototype **if** evidence shows Python-only composition leaves a meaningful
authoring gap. It is not yet the accepted replacement.

### C. Optional established template-engine adapter

Offer an integration package for Jinja or another established engine while keeping it outside the
core component contract. This gains familiarity and ecosystem tooling, but sandboxing, contextual
escaping, typed component calls, build-time dependency analysis, and deterministic artifacts are
weaker. It may be a useful escape hatch; it should not silently become Hedron's security model.

### D. Full custom component language

Restart the current direction with a formally specified grammar, type system, resolver, interpreter,
and tooling stack. This offers the most control and the highest permanent cost. It should be selected
only after real applications demonstrate that A, B, and C cannot meet the product need.

## Proposed evaluation

Before selecting an implementation:

1. Build the same three representative components in Python-only form, a throwaway layout-only
   prototype, and (where relevant) a sandboxed established template engine:
   - a semantic card with typed props and optional regions;
   - a form/error layout with accessibility and HTMX state; and
   - a repeated data/status view with styles, assets, and a nested component dependency.
2. Test authoring time, readability, typing, error locality, diff quality, formatting, editor
   behavior, build time, render time, artifact size, security boundary, and migration complexity.
3. Interview at least one Python-first author and one HTML/design-oriented collaborator using the
   same tasks. Record where Python is genuinely insufficient rather than assuming a second syntax is
   inherently friendlier.
4. Publish the prototype and evidence without using it in built-ins or promising compatibility.
5. Accept a revised RFC only if one direction is materially better on validated product jobs and
   still meets the security and operations gates.

## Implementation hold and boundaries

While this RFC is Draft:

- do not add HDN syntax, expression helpers, imports, artifact fields, formatter behavior, LSP work,
  or new built-in/reference dependencies on HDN;
- maintain the current implementation only for critical security/correctness fixes and inventory/
  migration tooling;
- label `compile_hdn`, `format_hdn`, `run_program`, `load_hdn_program`, `.hdn` source, and
  `RenderProgram` experimental;
- keep production build support for already-shipped experimental templates until the migration
  decision is accepted; and
- do not use current `HDN_FORMAT_VERSION = 2` or the flat opcode model as a compatibility constraint
  on a replacement.

The in-progress explicit-import experiment is useful audit input, but it is not an accepted public
contract and should not drive the new architecture.

## Security implications

The existing evaluator's denial list is not a sufficient sandbox because ordinary Python data-model
operations can execute application code. The design hold reduces exposure by stopping feature
growth and new recommendations. Any replacement must consume closed, normalized values; resolve
component schemas at build time; prohibit dynamic code/object access; apply one execution budget;
and pass adversarial parsing, artifact, dependency, trusted-content, and resource-exhaustion suites.

An established template-engine adapter must be documented as application-executed code unless its
threat model proves otherwise. “Sandboxed” is not a substitute for an explicit trust boundary.

## Accessibility implications

A replacement must validate what can be known statically without claiming that static checks prove
accessibility. Component schemas should carry required semantic/label/slot constraints. Source
diagnostics need precise spans. Representative components must pass keyboard, screen-reader,
focus/status, non-JavaScript, and browser automation evidence through the same component contracts
as Python implementations.

## Performance implications

The evaluation records cold and incremental compile time, installed/runtime dependency cost,
artifact size, load time, render time, memory, maximum-depth/list behavior, and failure under budget.
Python-only is the zero-new-runtime baseline. A declarative format must demonstrate useful authoring
or validation benefits that justify its build/runtime cost.

## Testing strategy

- Golden component fixtures shared by all prototypes.
- Parser/tokenizer conformance against the explicitly chosen markup model.
- Compile-time schema failures for components, props, slots, styles, assets, and view-model fields.
- Closed-value and artifact deserialization adversarial corpora.
- Runtime budget tests for depth, repetition, collections, strings, nodes, and output.
- Python/declarative observable-output parity where parity is claimed.
- Formatter/recovery/source-map tests only after a concrete syntax is selected.
- Published-artifact build/install/upgrade/migration evidence before promotion.

## Compatibility and migration

The 0.8 HDN surface is reclassified experimental by D-039. Existing templates continue to build
during the design window, but new applications should use Python components.

If HDN is removed, Hedron will inventory usage, emit a diagnostic, provide Python-equivalent
inspection/ejection where feasible, and retain at least one intervening minor phase before removal.
If a replacement is selected, a converter handles only the representable subset; expressions,
helpers, raw access, or ambiguous HTML behavior fail with actionable diagnostics rather than being
silently translated.

The replacement may use a new name, extension, artifact format, and API namespace. Compatibility is
defined by the accepted migration path, not by preserving HDN implementation internals.

## Open questions

- Is there validated demand for non-Python component authorship, or is clearer Python sufficient?
- Must a declarative format support condition/repetition, or can Python prepare all structure?
- Which markup parsing model provides familiar HTML behavior and precise, recoverable source spans?
- Should template bindings consume a generated closed view-model, explicit named values, or both?
- Can component props/slots be represented completely enough for useful build-time validation?
- Is an established template-engine adapter worth supporting as an explicitly less-typed escape hatch?
- Does “HDN” still describe the product if the selected model is layout-only, or should the name be retired?

## Acceptance criteria

This RFC cannot become Accepted until:

- the three representative authoring studies and user-role evaluation are published;
- the selected direction is compared honestly with Python-only and an established-engine adapter;
- grammar/parsing, value algebra, schema resolution, IR, execution budgets, security, accessibility,
  performance, packaging, and diagnostics are specified without relying on current internals;
- a migration/disposition exists for every current public function, artifact, manifest field,
  component folder, CLI/Explorer surface, example, and `.hdn` file;
- the prototype passes the defined adversarial and conformance gates; and
- an explicit decision either removes the second language or accepts a narrowly justified replacement.
