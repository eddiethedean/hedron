# Diagnostic contract

**Status:** Accepted for the phase 0.0 baseline

Every compiler, build, route, security, accessibility, integration, and runtime diagnostic has a stable code:

```text
HED-<AREA>-<NNNN>
```

Initial areas are `MODEL`, `RENDER`, `HTML`, `ROUTE`, `API`, `HTMX`, `HDN` (legacy experimental),
`CSS`, `ASSET`, `PLUGIN`, `DATA`, `CHART`, `ASYNC`, `SEC`, `A11Y`, `PERF`, `BUILD`, and `CONFIG`.
RFC-0031 reserves `JINJA` for the planned optional template integration.

Examples: `HED-SEC-0001`, `HED-HDN-0042`, `HED-ROUTE-0010`.

## Diagnostic record

A record contains:

- stable code and severity (`error`, `warning`, `information`);
- concise title and complete explanation;
- source owner, file and span when available;
- component, route, plugin, or artifact identifier;
- remediation and relevant documentation link;
- safe structured context after shared redaction;
- optional related locations and causal diagnostics.

The same record renders as human-readable text, Rich terminal output, JSON, SARIF, and Explorer data. Formatters never receive raw secrets.

## Stability and suppression

Codes are never silently reassigned. Message wording may improve without changing the code. Suppressions name a code, smallest source scope, and justification; security errors and selected strict-profile diagnostics cannot be suppressed. CI may set severity thresholds without changing the underlying diagnostic.

Unexpected internal exceptions remain distinct from user diagnostics, receive a trace identifier, and preserve the original exception for developers without exposing it to production clients.
