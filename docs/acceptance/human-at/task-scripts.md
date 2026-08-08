# Reference-app task scripts (human AT / 0.21)

**App:** [`examples/reference-app`](../../../examples/reference-app/)
**Default credentials:** `admin` / `secret` (HTTP Basic) — local demo only; replace before any
shared deploy.
**Run:** `uv run uvicorn app:app --app-dir examples/reference-app`

Each task lists the goal, steps, and what to observe. Facilitators record results in redacted
ledger rows (`task_id` below). Do not coach expected announcements mid-task.

## Task `login`

**Goal:** Authenticate and reach the main admin surface.

1. Open the app root URL.
2. Complete HTTP Basic authentication with the demo credentials (or the session’s provided
   credentials).
3. Confirm the main page loads with a clear document title and primary landmark/heading.

**Observe:** Focus lands in a sensible place after auth; page title is announced; no silent
failure; credentials fields (if any beyond browser Basic UI) have accessible names.

## Task `crud-form-pe`

**Goal:** Create or update a user via the progressive-enhancement (full page) form path.

1. From the user admin UI, open create or edit.
2. Disable JavaScript **or** otherwise force a classic full-page POST (no `HX-Request`).
3. Fill required fields (name, email, role) using AT / keyboard.
4. Submit and confirm success via full page or redirect.

**Observe:** Labels associated with inputs; errors announced and associated; required state
exposed; submit control named; focus not lost after error.

## Task `crud-form-htmx`

**Goal:** Complete the same create/update flow with HTMX fragment enhancement enabled.

1. With JavaScript/HTMX available, open create or edit.
2. Submit a valid change that swaps a fragment (or returns `InteractionResult` region content).
3. Confirm the updated row/status appears without a confusing full navigation.

**Observe:** Focus preserved or moved intentionally after swap; status/alert announced if
present; region update does not strand browse mode in an empty container.

## Task `fragment-refresh`

**Goal:** Use Refresh / status fragment controls without keyboard or SR traps.

1. Locate the refresh or status control on the main surface.
2. Activate it with keyboard (and SR gesture where applicable).
3. Confirm the targeted region updates.

**Observe:** Control has an accessible name; busy/loading state is conveyed when present;
completion is perceivable; focus not trapped.

## Task `data-editor-smoke`

**Goal:** Perform a minimal DataEditor interaction (view + one edit or selection).

1. Open the DataEditor surface in the reference app.
2. Move to a cell/row using keyboard (and SR table navigation if offered).
3. Perform one edit **or** confirm read-only navigation and selection state are perceivable.
4. Exit editing mode without trapping focus.

**Observe:** Grid/table has a caption or accessible name; headers/associations make sense;
edit mode is discoverable; Escape or equivalent exits; validation messages are announced when
shown.

## Facilitator checklist (every session)

- [ ] Record OS, browser, AT name + versions
- [ ] Note reduced-motion / contrast settings if changed
- [ ] Capture Blocker / Major / Minor / Note per [PROTOCOL.md](PROTOCOL.md)
- [ ] Draft redacted ledger row before ending the session
- [ ] File or link remediation issues the same day when feasible
