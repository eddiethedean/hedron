# Phase 0.61 upgrade fixtures

The phase is additive. Existing `InteractionState`, `InteractionResult`, HTMX markup, built-in
constructors, and theme hooks remain valid when no new phase 0.61 arguments are supplied.

Required before release:

- render the pre-0.61 `Tabs`, `Container`, `AppShell`, and `Identity` calls and compare their
  semantic markers and target IDs;
- render the new surface arguments with the package import path and the facade import path;
- disable JavaScript and confirm `AsyncRegion` still returns ordinary HTML;
- import a clean wheel and confirm the action-state schema and element module copies match; and
- remove new optional arguments to verify the pre-0.61 render path remains available.

Rollback is declaration-level: remove optional phase 0.61 arguments and stop projecting the new
action metadata. Existing server routes, HTMX headers, and browser enhancement continue to own
their prior behavior.
