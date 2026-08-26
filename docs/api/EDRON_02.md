---
status: implemented
---

# Edron 0.2 authoring and tooling contract

Edron 0.2 refines the 0.1 class facade without adding a second renderer, router, state store,
browser runtime, or dependency authority. It adds source-aware author feedback, safe teaching
scaffolds, and two explicit authoring conveniences.

## Source-aware diagnostics

`edron.diagnostics` provides immutable `SourceLocation`, `EdronDiagnostic`, and
`DiagnosticReport` values. Locations are one-based and reports can be projected to text, JSON, or
SARIF. Diagnostic context is bounded and redacts values whose names suggest passwords, secrets,
tokens, cookies, or CSRF data. Runtime Edron errors expose `.diagnostic` while retaining their
exception classes and `.code` compatibility.

## Non-executing checks and explanations

`edron.tooling.check_source(path)` parses Python with `ast`; it never imports the file, invokes a
callback, reads application data, or starts a server. `App.explain()` and `App.source_map()` inspect
registered definitions and native projections only. They include page/surface names, methods,
routes, native logical IDs, and source locations, with `callbacks_executed=False` in explanations.

The CLI mirrors these boundaries:

```text
edron check app.py [--register] [--format text|json|sarif]
edron explain app.py [--format text|json]
edron doctor [app.py] [--format text|json]
```

`--register` is an explicit trusted-import opt-in. `doctor` reports required and optional package
status as `available`, `missing`, `incompatible`, or `broken`; it never installs anything.

## Teaching scaffolds

`edron new NAME --path PATH --template minimal|dashboard|form` creates a small `app.py`, a
bounded package definition, and a README. It refuses to overwrite a non-empty destination unless
`--overwrite` is passed. Generated source uses explicit Edron ownership and is intended for review,
not as a promise of application behavior.

## Explicit conveniences

`@app.function_page(...)` (also spelled `@app.page_function(...)`) registers one function through
the same native route and a fresh request-local `Page` instance. It is deliberately limited to a
single render surface; classes remain the composition path for fragments, actions, dependencies,
and inheritance.

Decorated fragments and actions are never inherited implicitly. `ed.inherit(Base.surface)` (also
`ed.expose(...)`) clones one descriptor for assignment on a subclass. The clone receives its own
app-scoped native projection and may override its public name or path:

```python
class Shared(ed.Page):
    @ed.fragment
    def status(self) -> None:
        self.text("ready")

class Home(Shared):
    status = ed.inherit(Shared.status, name="status")
```

The clone does not expose other base-class descriptors and does not make the base class globally
registered.
