# BLE001 noqa policy (phase 0.26 prep)

Ruff rule `BLE001` (blind `except Exception`) is enabled for the workspace.

## When `# noqa: BLE001` is allowed

Document the reason on the same line or the line above:

- Optional import / settings discovery where absence must not break the host path
- Framework boundary parsing (form bodies, type hints) where the library raises
  broad exceptions and the fail-closed path is intentional
- Best-effort cleanup / cancel paths that must not mask the primary error

## When it is not allowed

- Swallowing errors without logging or re-raise in Supported security boundaries
- Empty `except Exception: pass` on trust-boundary code (prefer specific types)

Prep for 0.26 does not require eliminating every historical catch; new code should
prefer narrow exception types.
