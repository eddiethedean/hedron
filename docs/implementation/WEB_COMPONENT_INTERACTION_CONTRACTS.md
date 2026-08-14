# Web Component interaction contracts

**Planning status:** Normative under Accepted
[RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) (D-064); public type names and
serialized shapes freeze with `ABI-036` / `STATE-036` fixtures.

These five contracts close the browser-interaction gaps that appear when a React application moves
to server-rendered Hedron + HTMX. They extend the
[Web Component platform implementation](WEB_COMPONENT_PLATFORM.md); they do not add a virtual DOM,
hydration, client router, global store, or client-side authority.

The state machines, ownership rules, and failure boundaries are normative for planning and
acceptance.

## 1. `ElementStateOwnership`

Every mutable element field declares exactly one ownership mode. A field cannot silently switch
between server and browser authority because a module upgraded or an HTMX swap occurred.

| Mode | Source of truth | Browser behavior | Incoming server value |
|---|---|---|---|
| `controlled` | Current server markup/property | Emit intent; do not claim canonical mutation until server response | Apply unless it conflicts with an active declared draft |
| `local` | Current element instance | Disposable presentation state; may initialize from server once | Ignore after initialization unless the contract exposes an explicit reset |
| `draft` | User-owned bounded draft over a server base | Track base version, dirty fields, submit/discard, and conflict state | Rebase only when proven safe; otherwise preserve both and surface conflict |
| `preference` | Namespaced non-secret browser preference | Persist only through `BrowserStorage` policy | Explicit server policy may override; never authorization or business state |

Capabilities, authentication, authorization, CSRF material, signed URLs, server job state, trusted
HTML, files, and durable records are never element-owned modes.

### Controlled fields

- Attribute/property changes are programmatic updates and do not emit user-intent events unless the
  field contract explicitly says otherwise.
- User interaction emits a typed intent event. The visible value may show a pending presentation,
  but the server response supplies the next canonical controlled value.
- Reflection between property and attribute is one-directional or guarded; it cannot create an
  event/update loop.
- A late response is applied only when its operation/revision relationship is valid. Ignoring a
  stale presentation response does not cancel or reverse server work.

### Local fields

- Local state is limited to presentation such as open/closed state, measured size, hover, temporary
  focus key, or adapter viewport.
- It is discarded on outer replacement and reconstructed on connect unless a separate preference or
  draft contract applies.
- Local state cannot select records, tenants, permissions, action URLs, or server query scope in a
  way the server trusts.

### Draft fields

A draft records a schema version, base server revision, bounded dirty field set, creation/expiry,
and submit/discard/conflict policy. When new server state arrives while dirty, the element uses one
declared policy:

- `replace`: allowed only for explicitly disposable drafts and announced before loss;
- `preserve`: retain the draft and mark the new canonical base as pending review;
- `rebase`: apply a typed, deterministic merge proven safe for the field schema; or
- `conflict`: retain base, incoming value, and draft long enough for an explicit resolution UI.

`conflict` is the default when a safe rebase is not proven. No last-write-wins behavior is inferred.
**Phase boundary (D-064):** Phase **0.36** (`STATE-036`) owns ownership modes, reflection,
incoming-update, persistence, submit/discard, and conflict/rebase rules for a single connected
instance. **Cross-instance draft transfer** across swaps/history remains a non-goal until phase
**0.41**; all other local state remains disposable.

### Metadata and diagnostics

Registry metadata declares each mutable field's mode, reflection, incoming-update policy, persistence,
limits, and event. Explorer shows authority and dirty/conflict state without displaying field values.
Unknown ownership, illegal persistence, or an ambiguous controlled/draft transition emits a redacted
`HED-ELEMENT-STATE-*` diagnostic and falls back to server rendering.

#### Diagnostic catalog (0.36)

| Code | When |
|---|---|
| `HED-ELEMENT-0001` | Tag or ABI definition conflict at registration |
| `HED-ELEMENT-0002` | Incompatible server/module ABI pair |
| `HED-ELEMENT-0003` | First-party `hedron-` prefix misuse / third-party naming violation |
| `HED-ELEMENT-0004` | Missing or undeclared module/CSS asset |
| `HED-ELEMENT-0005` | Structured-input schema, bound, or encoding failure |
| `HED-ELEMENT-0006` | Module timeout, init exception, or upgrade failure (fallback retained) |
| `HED-ELEMENT-STATE-0001` | Unknown or missing ownership mode on a mutable field |
| `HED-ELEMENT-STATE-0002` | Illegal persistence / capability marked element-owned |
| `HED-ELEMENT-STATE-0003` | Controlled update loop / illegal intent emission |
| `HED-ELEMENT-STATE-0004` | Dirty-draft incoming update without declared policy |
| `HED-ELEMENT-STATE-0005` | Conflict entered; last-write-wins refused |
| `HED-ELEMENT-STATE-0006` | Transfer attempted before phase 0.41 eligibility |

Diagnostics redact payloads and never print secrets, credentials, or full structured inputs by
default.

## 2. `InteractionState`

Every element-owned asynchronous interaction exposes one common state machine rather than inventing
component-specific loading flags.

```text
idle -> pending -> success -> idle
          |  |       |
          |  +-----> error -> pending (retry)
          +--------> canceled -> idle
```

Progress is metadata on `pending`, not a separate terminal state. Required fields are:

- stable interaction name and element instance identity;
- opaque operation ID suitable for correlation but not authorization;
- state: `idle`, `pending`, `success`, `error`, or `canceled`;
- optional bounded progress current/total/unit and safe status code/message key;
- start/settle timestamps or durations for diagnostics; and
- declared concurrency and retry policy.

### Concurrency

Each interaction selects one policy:

- `drop`: ignore a new equivalent intent while pending;
- `replace`: cancel/obsolete the prior browser operation before starting the new one;
- `queue`: enqueue to a documented bounded depth; or
- `parallel`: permit a documented bounded count with distinct operation IDs.

There is no unbounded default queue. Controls declare whether pending state disables only the
initiating control, a form, or nothing. The element exposes `aria-busy` and a non-noisy status/error
announcement where applicable while preserving focus and native form semantics.

### HTMX and jobs

The bridge derives transitions from the owned HTMX request lifecycle or a registered job/polling
contract. HTTP acceptance (`202`) is not success of the durable job. Canceling a browser request is
not reported as server/job cancellation until the server acknowledges that state.

Response status, structured Hedron error code, retry policy, and canonical fragment determine the
terminal transition. Late responses are correlated by operation ID/revision. Errors retain a safe
human message and diagnostic code; raw response bodies, stack traces, secrets, and user data do not
enter reflected attributes or telemetry.

### Progressive enhancement

Before upgrade and when JavaScript fails, native navigation/form submission exposes ordinary browser
loading and server error pages/fragments. `InteractionState` improves local feedback; it is never the
only way to complete, observe, retry, or cancel a Supported server workflow.

## 3. `OptimisticMutation`

Optimism is explicit, mutation-specific, and reversible. The default Hedron mutation remains
server-confirmed rendering.

An optimistic mutation declares:

- registered server action and authorization/CSRF boundary;
- base record/collection revision;
- typed forward patch and deterministic inverse or canonical refetch path;
- idempotency/replay key policy;
- affected element/region and focus/announcement behavior;
- timeout, retry, cancel, rejection, and conflict behavior; and
- whether optimism is permitted for the mutation's risk class.

### State machine

```text
canonical -> proposed -> submitted -> confirmed
                  |          |          |
                  |          +-------> rejected -> rolled_back/refetched
                  +------------------> conflicted -> resolve/refetch
```

The browser may present `proposed` state immediately, but it does not call it saved. Confirmation
comes from a matching server operation/revision and applies the server's canonical fragment or typed
patch. A rejection runs the inverse patch or refetches canonical state. A conflict preserves enough
context for an explicit resolution; it never silently overwrites the server or another user's work.

### Safety limits

- Optimism is deny-by-default for authentication/authorization, destructive irreversible actions,
  payments, secrets, file publication, cross-tenant moves, and operations without idempotency or a
  deterministic rollback/refetch path.
- Optimistic patches use the existing typed property/collection patch allowlists. They cannot contain
  HTML, CSS selectors, executable values, arbitrary URLs, object paths, or undeclared DOM targets.
- The server revalidates every value and may return a different canonical result.
- Disconnect/history does not imply rollback of already accepted server work. Reconnect resolves by
  operation/revision or canonical refetch.
- Pending/rollback/conflict states are perceivable without color or motion and do not steal focus.

Optimistic support is first proven on bounded DataEditor/collection mutations in phase 0.39. Other
components remain server-confirmed until they pass the same evidence.

## 4. `GestureOverlayCatalog`

Phase 0.37 locks a catalog of reusable interaction behaviors so components do not independently
implement drag/drop, resizing, focus traps, dismissal, or top-layer behavior.

### Gesture contracts

The initial catalog covers:

- reorder and drag/drop within an allowlisted collection/target set;
- resize/splitter behavior with declared min/max/step and persisted-state policy;
- pointer press/move/release/cancel and pointer-capture cleanup;
- keyboard move/reorder/resize equivalents with instructions and announcements; and
- touch target size, scrolling, zoom, reduced-motion, RTL, and cancellation behavior.

Gestures emit typed intent events; they do not mutate authoritative records directly. Pointer and
keyboard paths produce the same semantic result. Native HTML drag events may be used as one input
path but cannot be the only accessible path. Escape/cancel restores the pre-gesture presentation.
Outer swaps/disconnect release pointer capture, global listeners, auto-scroll, animation frames, and
temporary DOM.

Drop zones and reorder targets are registry/markup allowlisted. Payloads contain stable typed item
identities, positions, and operation metadata—not DOM nodes, selectors, arbitrary MIME data, file
paths, HTML, or authority.

### Overlay contracts

The initial overlay catalog covers dialog, popover/menu, combobox/listbox popup, tooltip/help,
command palette, and toast/status surfaces. Implementations prefer native `<dialog>`, Popover API,
and CSS anchoring when the declared browser floor provides the required semantics, with local
feature-detected fallbacks otherwise.

Each overlay declares:

- trigger, accessible name/description, role/state, and keyboard model;
- top-layer/stacking and nested-overlay policy;
- initial focus, focus containment where required, and return target;
- Escape, explicit close, outside interaction, navigation, submit, swap, and disconnect behavior;
- modal/inert/background behavior and scroll restoration;
- anchor loss, viewport collision, zoom/reflow, reduced-motion, and RTL behavior; and
- whether its contents are server-owned regions or element-owned presentation.

Tooltips are never the only source of essential information. Toasts do not contain the sole error or
completion record. A command palette invokes registered actions/routes only and performs the same
authorization and validation as their ordinary UI.

### Catalog governance

Explorer exposes the catalog entry, keyboard map, ownership, events, assets, and limitations. New
gesture/overlay behaviors require a catalog entry and conformance scenarios; copying a private
controller into a first-party component is rejected by build/review policy.

## 5. `ReactMigrationMatrix`

The migration matrix is both guidance and a coverage ledger. It distinguishes what Hedron replaces,
what becomes a bounded element, what may remain a temporary React island, and what is not a fit.

### Concept mapping

| React concept | Hedron target |
|---|---|
| Component render | Typed Python component + server-rendered HTML |
| Props | Validated Python props; element scalar attributes/structured properties where interactive |
| Callback prop | Versioned typed `CustomEvent` mapped to a registered action/graph trigger |
| Local `useState` | Declared `local` or `draft` element field |
| Controlled input | `controlled` state ownership + intent event + canonical server response |
| `useEffect` cleanup | Idempotent connect + abort/dispose on disconnect |
| Context | Explicit Python dependency/context, server session, theme token, or typed DOM event—not a hidden global store |
| Reducer | Server action/domain model; bounded local state machine only for browser presentation |
| Data fetching/mutation | Route/action + HTMX; `InteractionState`; optional evidenced `OptimisticMutation` |
| Router | HTTP routes, native navigation, HTMX boost/history |
| Portal | Native top layer / `GestureOverlayCatalog`; no arbitrary detached ownership |
| Suspense/loading boundary | SSR fallback + lazy fragment/job polling + `InteractionState` |
| Error boundary | Server error contract plus per-element upgrade/failure isolation and fallback |
| Memoization | Server/cache contracts and route-level asset deduplication; no correctness dependency |
| List keys | Hedron component/collection stable identities |

The published matrix expands this list with forms, refs, transitions, virtualization, drag/drop,
charts/maps/editors, testing, accessibility, CSS, data libraries, authentication, and deployment.

### Dependency disposition

For each React component/library in a migration, the tool and guide select one explicit disposition:

1. `native`: replace with HTML/CSS/HTMX;
2. `hedron`: replace with an existing Hedron component/element;
3. `element`: implement a native custom element against the author kit;
4. `react-island`: retain temporarily behind the migration bridge; or
5. `not-a-fit`: retain a client application or choose another architecture.

An optional React-island bridge is migration-only and Experimental. It declares a single owned mount
root, pinned React/runtime assets, typed props/events, SSR placeholder/fallback, CSP/supply inventory,
and deterministic unmount on disconnect. It is not transitive from `hedron`/`hedron-elements`, cannot
own an HTMX server region, and has a removal/destination ledger. Hedron does not promise transparent
wrapping of arbitrary npm components.

### Deliverables

- A React-to-Hedron fit questionnaire and inventory command/schema.
- Worked migrations for a CRUD form, dashboard with coordinated widgets, DataEditor optimistic edit,
  overlay/command interaction, and one temporary React island.
- Tests comparing ordinary navigation, HTMX, upgraded interaction, JS failure, accessibility,
  performance, and cleanup.
- An honest non-equivalence section for offline-first applications, client-authoritative editors,
  games/canvas runtimes, arbitrary npm ecosystems, and high-frequency collaborative clients without
  an accepted server synchronization design.

The matrix ships in phase 0.40 and becomes part of the 0.42 Supported-inventory honesty review.

## Cross-contract ordering

```text
ElementStateOwnership
    -> InteractionState
        -> OptimisticMutation
    -> GestureOverlayCatalog
        -> ReactMigrationMatrix
```

State ownership is foundational in 0.36. Interaction and gesture/overlay contracts ship with forms
and primitives in 0.37. Phase 0.38 proves the chart-scoped interaction profile on `hedron-chart`;
optimistic mutation is proven on rich data surfaces in 0.39. The migration matrix and optional
bridge ship with authoring/interoperability in 0.40. Composition/state transfer in 0.41 and
production graduation in 0.42 test all five together.
