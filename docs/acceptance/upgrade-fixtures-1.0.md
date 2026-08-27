# Hedron 0.67 to 1.0 upgrade fixtures

**Status:** Stage 0 Refined; fixture implementations are pending

**Source:** immutable `v0.67.0` wheels/sdists and source snapshot
**Target:** `v1.0.0`
**Authority:** RFC-0096, D-114–D-117, `one-zero-cut-contract.toml`

The fixture corpus proves the unusual compatibility direction: source written only to the 1.0
canonical surface must run unchanged on both 0.67.0 and 1.0.0. Transitional 0.67 fixtures prove
that every removed path warned before the cut and has a deterministic migration result or explicit
manual/non-fit disposition.

## Corpus lanes

| Lane | Runs on 0.67.0 | Runs on 1.0.0 | Purpose |
|---|---|---|---|
| `canonical/` | Yes, unchanged | Yes, unchanged | Complete documented 1.0 source/config/HDJ/CLI corpus |
| `shared/` | Yes | Yes | Package-native and Advanced contracts intentionally retained in both releases |
| `transitional/` | Yes, with warning/finding | Only after migration; otherwise precise failure is allowed | Every public 0.67 path removed from 1.0 |
| `negative/` | Deterministic rejection | Same rejection | Illegal interactions, unsafe directives, late assets, dual writers, invalid outcomes |
| `rollback/` | Yes | N/A | Exported data/config/project source created without a 1.0-only format dependency |

## Required canonical journeys

1. A `Hedron` application with function-only `page`, `view`, and `action` handlers.
2. Page/view handlers returning one explicit `hedron.ui` tree and an action returning each admitted
   role-valid `Outcome` family.
3. Local, request, and combined `Interaction` values with ordinary HTTP/no-JavaScript fallback.
4. A document plan whose reachable fragment closure installs exact Alpine assets up front and
   rejects an undeclared late feature.
5. Python and HDJ rendering the same feature, provenance, interaction, and warning facts.
6. Native/Alpine common widgets plus retained chart, map, and data-editor specialist hosts.
7. FastAPI, Flask, Django, Workbench/Posit, package-native satellites, and clean optional-dependency
   failures at the exact supported versions in the compatibility BOM.
8. CLI check/build/inspect, generated project, configuration, manifest, and offline package paths.

## Transitional minimum

The initial runtime registry covers `app.component -> app.view`, `app.fragment -> app.view`, and
`app.include_feature -> app.include`. Those three fixtures are a floor, not proof that the public
0.67 inventory is complete. W0 must generate the full public-artifact inventory and add one row per
removed import, decorator, argument, config/CLI/HDJ/markup form, browser tag/controller, root shim,
and generated spelling.

Every transitional fixture records:

- warning code and old path/form;
- replacement or explicit non-fit reason;
- runtime/static applicability and complete/partial/unknown analysis confidence;
- first-warning and removal version;
- non-executing migration output plus idempotence result;
- before/after behavior, typing, security, accessibility, and browser parity where applicable; and
- owning package, source location, documentation anchor, and retained evidence path.

## Cut rules

- A removal with no 0.67 warning/finding and fixture blocks `REMOVE-100`.
- `partial` or `unknown` coverage may remain a diagnostic result, but cannot authorize removal.
- The migrator never imports or executes application/template/plugin code.
- Default migration output is a diff/report. In-place changes require explicit `--apply`; existing
  output is never overwritten without an explicit choice.
- Running the migrator twice produces no second semantic change.
- No canonical fixture may contain a 0.67 compatibility alias or receive a target-1.0 finding.
- Any necessary 1.0-only correction is backported to 0.67.x before cut or deferred to 1.1.

## Retained evidence

For each supported Python version, retain the exact package lock, artifact hashes, environment and
browser identities, Pyright result, runtime result, CLI/HDJ/build output, browser trace, migration
report, and rollback rehearsal. Generated evidence is stored outside source packages and linked
from the release packet; prose checkboxes alone cannot satisfy a gate.
