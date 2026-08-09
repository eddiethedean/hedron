# Reference-app task scripts (human AT / 0.21)

**App:** [`examples/reference-app`](../../../examples/reference-app/)
**Default credentials:** `admin` / `secret` (HTTP Basic) — local demo only; replace before any
shared deploy.
**Train:** living Published **0.24** (human AT sessions still Planned — see [PROTOCOL.md](PROTOCOL.md)).

## Run

```bash
uv sync
uv run uvicorn app:app --app-dir examples/reference-app
```

Open `http://127.0.0.1:8000`. Codespaces / Dev Container also work; use the forwarded port URL
and the same Basic credentials.

Each task lists the goal, steps, and what to observe. Facilitators record results in redacted
ledger rows (`task_id` below). Do not coach expected announcements mid-task.

## Landmark map (facilitator)

| Surface | How to find it |
|---|---|
| Document title / `h1` | “Hedron Team Admin” |
| Main landmark | Users section on `/` |
| Users table fragment | `#user-table` (lazy-loaded) |
| Refresh users | Button “Refresh users” targeting `#user-table` |
| Create user | Card “Create user” (classic POST + `hx-post` to `/users`) |
| Edit users | Heading “Edit users” → links `Edit {name}` → `/users/{id}/edit` |
| DataEditor | Section “Data application toolkit” (employee editor) |
| Chart refresh | `#chart-region` / chart Refresh under “Visualization and interactions” |
| Status / OOB | Chart search / OOB status regions under charts |

## Environment notes

### Progressive enhancement (no JS)

- Disable JavaScript in the browser (or use an extension) so the create/edit forms POST without
  `HX-Request`. Success should **303 redirect** back to `/` with a status alert (`msg=` query).
- With JS enabled, the same forms use HTMX to swap `#user-table` only.

### HTTP Basic + TalkBack / Android

- The browser owns the Basic auth dialog; it is not Hedron markup. Confirm the page after auth
  has a usable title and landmarks.
- Prefer Chrome/Chromium for TalkBack sessions. If the auth dialog is awkward, pre-authorize via
  a bookmark with embedded credentials **only on a private test device**, never in public notes.

### Hosting

- Local `uvicorn` is the default facilitator path.
- Codespaces: start the same command; use the forwarded HTTPS URL. Expect slightly different
  focus timing after navigations.

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

1. From the user admin UI, open **Create user** or an **Edit {name}** link.
2. Disable JavaScript **or** otherwise force a classic full-page POST (no `HX-Request`).
3. Fill required fields (name, email, role) using AT / keyboard.
4. Submit and confirm success via **303 redirect** to a full page with a status alert (or
   visible updated roster).

**Observe:** Labels associated with inputs; errors announced and associated; required state
exposed; submit control named; focus not lost after error.

## Task `crud-form-htmx`

**Goal:** Complete the same create/update flow with HTMX fragment enhancement enabled.

1. With JavaScript/HTMX available, open create or edit.
2. Submit a valid change that swaps `#user-table` (declared `user-table` fragment region).
3. Confirm the updated row/status appears without a confusing full navigation.

**Observe:** Focus preserved or moved intentionally after swap; status/alert announced if
present; region update does not strand browse mode in an empty container.

## Task `fragment-refresh`

**Goal:** Use Refresh / status fragment controls without keyboard or SR traps.

1. Locate **Refresh users** (targets `#user-table`) and/or chart Refresh (`#chart-region`).
2. Activate it with keyboard (and SR gesture where applicable).
3. Confirm the targeted region updates.

**Observe:** Control has an accessible name; busy/loading state is conveyed when present;
completion is perceivable; focus not trapped.

## Task `data-editor-smoke`

**Goal:** Perform a minimal DataEditor interaction (view + one edit or selection).

1. Open the DataEditor surface under **Data application toolkit**.
2. Move to a cell/row using keyboard (and SR table navigation if offered).
3. Perform one edit **or** confirm read-only navigation and selection state are perceivable.
4. Exit editing mode with **Escape** (restores the prior cell text and blurs) or an equivalent
   explicit exit; Enter commits/blurs.

**Observe:** Grid/table has a caption or accessible name; headers/associations make sense;
edit mode is discoverable; Escape exits without trapping focus; validation messages are
announced when shown.

## Facilitator checklist (every session)

- [ ] Record OS, browser, AT name + versions
- [ ] Note reduced-motion / contrast settings if changed
- [ ] Capture Blocker / Major / Minor / Note per [PROTOCOL.md](PROTOCOL.md)
- [ ] Draft redacted ledger row before ending the session
- [ ] File or link remediation issues the same day when feasible
