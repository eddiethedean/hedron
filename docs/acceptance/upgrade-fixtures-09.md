# Edron 0.8 to 0.9 upgrade fixtures

These fixtures define the planned train transition. They do not authorize changing the published
Edron 0.8.0 artifacts or its Hedron 0.66.2 dependency boundary.

## Version matrix

| Fixture | Edron | Hedron | Purpose |
|---|---:|---:|---|
| `source-08` | `0.8.x` | `0.66.2` | Existing deployment and rollback source |
| `target-09` | `0.9.0` | `0.67.0` | Candidate target, locked and tested in a clean environment |
| `future-10` | `0.9.0` | `1.0.0` | Forward-compatibility target, exercised when Hedron 1.0 is released |
| `mixed-refusal` | `0.9.0` | `0.66.x` | Must fail with a dependency/train diagnostic rather than run partially |
| `moving-refusal` | `0.9.0` | `>=0.67,<0.68` without a 0.67.0 lock record | Must be labeled installable-but-untested until exact evidence is retained |

## Required scenarios

1. Rebuild the application manifest and native 0.67 browser feature plan before serving the target
   application. A missing, stale, or invalid plan fails closed at the check boundary.
2. Exercise a common local widget through native HTML plus Alpine and a specialist chart, map, or
   data editor through its owning Web Component/package. The fixture records exact native identity,
   assets, CSP/SRI, keyboard/focus behavior, and no-JavaScript fallback.
3. Exercise one `local`, one `request`, and one `combined` Hedron 0.67 interaction. There is at
   most one request, server truth remains authoritative, and an ordinary HTTP fallback remains
   usable when enhancement is unavailable.
4. Exercise native 0.67 action outcomes, lifecycle cleanup, HTMX replacement, stale-result handling,
   focus, announcements, and bounded redacted traces. Each concern has one writer.
5. Scan runtime imports, generated source, examples, documentation beginner paths, package metadata,
   and browser asset manifests for every forbidden Hedron 0.67 compatibility path. The scan must be
   empty; only migration input and warning fixtures may mention a deprecated path.
6. Run the 0.8 deployment preflight before migration, preserve application-owned data and secrets,
   and record any Edron/Hedron warning with its replacement, first release, and removal window.
7. Roll back the application artifact and package lock to the 0.8/Hedron 0.66.2 fixture. Edron never
   reverses application-owned data migrations, queued work, external effects, or secret rotation.
8. When Hedron 1.0.0 is released, run the same accepted Edron 0.9 source and public-contract corpus
   against it. Record every incompatibility as a release-blocking finding; do not solve it by
   importing deprecated 0.67 paths or by weakening the 0.67 evidence.

## Acceptance boundary

The target fixture is not complete until the exact Hedron `0.67.0` lock is visible in the package
metadata, lockfile, runtime report, and retained artifact evidence. A green test against the moving
workspace tip alone is insufficient. Hedron 1.0 forward compatibility is a required follow-up
matrix, not evidence that can be inferred from the 0.67 run.
