---
status: verified
---

# Edron state and interaction contract

**Status:** Published `1.0.1` Stable release<br>
**Target:** Edron `1.0.x`; Hedron `>=1.0.0`<br>
**Historical 0.1 target metadata:** Edron `0.1.0`; compatible Hedron train and release phase unassigned<br>
**Roadmap:** [Edron `0.x` release roadmap](../EDRON_ROADMAP.md)<br>
**Public API:** [Edron 0.1 public API](EDRON.md)<br>
**Packaging:** [Edron 0.1 packaging](EDRON_PACKAGING.md)<br>
**Capability inventories:** [Edron 0.1 capability inventories](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_CAPABILITY_INVENTORIES.md)<br>
**Implementation:** [Edron 0.1 implementation specification](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_001.md)<br>
**Acceptance:** [Edron 0.1 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_001.md)<br>
**Architecture:** [RFC-0094](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md)<br>
**Fixtures:** [Edron golden applications](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_GOLDEN_APPS.md)

This document began as the 0.1 design contract and now defines how state is owned and how
interactions progress through Edron 1.0. It complements the Python signatures in the public API
contract. Hedron remains the authority for request
binding, sessions, caches, handles, operation identity, action lifecycle, HTMX targets, responses,
CSRF, jobs, assets, and browser enhancement. Edron selects simpler defaults and maps their native
consequences back to Edron source.

## Short example

```python
import edron as ed

app = ed.App(title="Customers")


@app.page("/customers", title="Customers")
class Customers(ed.Page):
    repository: CustomerRepository = ed.dependency(get_repository)

    def render(self) -> None:
        query = self.text_input(
            "Search",
            name="query",
            updates=self.results,
        )
        self.results(query=query)

    @ed.fragment
    def results(self, query: str = "") -> None:
        for customer in self.repository.search(query):
            with self.card():
                self.text(customer.name)
                self.button(
                    "Delete",
                    action=self.delete.bind(
                        customer_id=customer.id,
                        query=query,
                    ),
                    variant="danger",
                    confirm=f"Delete {customer.name}?",
                )

    @ed.action(idempotency="required")
    def delete(self, customer_id: int, query: str = "") -> ed.Outcome:
        self.repository.delete(customer_id)
        return ed.refresh(self.results.bind(query=query)).toast("Customer deleted")
```

This source contains four distinct kinds of state:

- `query` is validated URL/query state owned by the current request;
- `repository` is a request-scoped dependency, not page state;
- customer records are durable application state owned by the repository/database; and
- pending/success/error/stale presentation is a bounded native interaction projection, not a
  durable browser store.

## Normative principles

1. **One value, one authoritative owner.** A value may be projected into several places, but only
   one layer is authoritative for writes at a time.
2. **`self` is not persistence.** Every page, fragment, and action HTTP request receives a fresh
   page instance. Instance attributes live only for that invocation.
3. **The URL owns shareable safe state.** Filters intended to survive refresh, links, or browser
   navigation use path/query values and safe `GET` requests.
4. **Typed forms own one submission.** Unsafe request data crosses one Pydantic/native binding
   boundary before application mutation code runs.
5. **The server owns domain truth.** Browser state, HTMX attributes, generated IDs, pending state,
   confirmation, and optimistic presentation cannot authorize or commit domain changes.
6. **Interactions lower to native handles.** Edron introduces no endpoint graph, target registry,
   response protocol, HTMX dialect, action state machine, or browser store.
7. **Progressive enhancement is required.** HTMX improves the ordinary page/form/fragment path; it
   is not the only correct path.
8. **Late responses cannot win.** A response may update presentation only when its app, target,
   operation, generation, and revision facts remain compatible.
9. **Mutation and presentation are separate.** Preventing a stale swap does not undo server work;
   transactions, revisions, and idempotency remain server/application concerns.
10. **State and metadata are bounded and redacted.** No owner may use an unbounded implicit map or
    embed secrets in URLs, identities, browser history, cache keys, traces, or explanations.

## State ownership matrix

| State class | Authority / writer | Lifetime | Edron access | Persistence and sensitivity |
|---|---|---|---|---|
| Application configuration | App construction/native Hedron config | Process/application | `ed.App(...)`, `app.hedron` | Immutable after registry seal; secrets stay in environment/config providers |
| Route/path state | Native router + validated request | Navigation/request | page/native path parameters | Public URL; never secret |
| Safe filter state | Canonical URL query + typed binding | Navigation/request/history | named inputs, `FilterScope`, fragment params | Bookmarkable; only safe serializable values |
| Form state | Pydantic/native form binder | One unsafe submission | `self.form(...)`, action model | Request body; sensitive fields redacted and not retained automatically |
| Bound action arguments | Native action binding plan | One control/submission | `.bind(...)` | Untrusted client input; never authorization |
| Page-local computation | Fresh page instance | One method/request | ordinary local/instance attributes | Never shared or durable |
| Request dependency | Native FastAPI/Hedron DI | One request or declared native scope | `ed.dependency(...)` | Cleanup/override owned by native host; cannot be client-bound |
| Typed session | Host/native session adapter | Configured session | dependency wrapping native `SessionState` | Small bounded user state; signing/storage/expiry are host policy |
| Derived cache | Native bounded cache | TTL/scope | `ed.cache_data(...)` | Recomputable only; explicit private/tenant/public scope |
| Durable domain state | Application service/database | Domain-defined | request dependency/service call | Multi-worker durable when claimed; app owns transactions/authz/revisions |
| Job state | Native `JobBackend` | Durable operation/retention | `ed.JobFlow` | Scope-bound; job ID is not authorization |
| Browser presentation state | Native HTML/HTMX/Web Component | Element/tab or explicit preference | native component/preference APIs | Non-authoritative; no secrets or permissions |
| Interaction lifecycle | Native `ActionState`/operation policy | One operation generation | implicit projection, native inspection | Bounded presentation/trace facts, not domain state |
| Theme preference | Native theme preference owner | Browser/session as configured | native preference through `app.hedron` | Presentation only; server validates supported theme/mode |

Moving a value between owners is a design change and must be explicit. For example, copying a query
filter into a session changes shareability, retention, cache variation, and privacy. Edron never
performs that transfer merely because a control name repeats.

## Placement rules

Use these rules in order:

1. If another user/process must observe the value after a restart, use durable application state.
2. If a worker owns the operation lifecycle, use `JobBackend` state and an authoritative `JobScope`.
3. If the value belongs in a shareable/reloadable URL and is safe to expose, use query/path state.
4. If the value exists for one command, use a typed form/action model.
5. If it is a small user-specific continuity value, use a typed native session through a
   dependency and configure signing/storage/expiry explicitly.
6. If it can be recomputed and losing it changes only performance, use an explicitly scoped cache.
7. If it affects only local presentation, use a native browser preference/element state.
8. Otherwise keep it as a local Python value for the current invocation.

The following substitutions are invalid:

- page instance field for database/session state;
- public cache for authenticated/private data;
- cache invalidation as a transaction;
- browser storage as authorization or durable truth;
- a query parameter for a secret;
- an action binding or hidden field for trusted identity;
- an interaction success marker as proof that a commit occurred; or
- an in-memory job backend in a multi-worker/production durability claim.

## Identity model

Every addressable or stateful projection uses explicit layered identity:

| Identity | Source | Compatibility status |
|---|---|---|
| App identity | Native application registry | Stable within registered app; not guessed across apps |
| Page logical identity | Registered page name/path | Name is public; generated internals are inspectable only |
| Control identity | Author `name=` + owning page/filter scope | Public binding identity |
| Fragment identity | Native `FragmentHandle.logical_id` | Public native handle identity |
| Bound fragment identity | Fragment + canonical serialized parameters + optional instance key | Stable for same non-secret binding |
| Action identity | Native `ActionHandle.logical_id` | Public native handle identity |
| Operation identity | Native operation ID + generation + target + correlation + optional revision | One interaction lifecycle |
| Durable record identity | Application model/service | Never inferred from DOM identity |
| Job identity | Backend-issued opaque ID + `JobScope` | ID alone grants nothing |
| Cache identity | Callable/version + canonical args + explicit scope | Redacted and bounded |

Identity values must not contain passwords, tokens, CSRF values, private form bodies, full query
strings, tenant secrets, dependency objects, component reprs, or raw job results. A deterministic
binding digest may be derived from safe canonical parameters; diagnostics disclose names and types,
not sensitive values.

Duplicate control names in one page binding namespace, duplicate fragment mounts with the same
binding, cross-app handles, or conflicting native logical IDs fail before ambiguous output is
emitted. Two visually identical controls are not the same control unless their registered identity
says so.

## Request and instance lifecycle

### Registration

Application import/registration may inspect class definitions, signatures, type annotations,
decorator metadata, native descriptors, and styling/capability metadata. It must not:

- instantiate page classes;
- invoke `render`, fragments, actions, dependencies, cache functions, jobs, or domain services;
- read a request/session/browser value;
- contact the network or optional service; or
- create mutable per-user state.

Registration produces one native screen/page descriptor per Edron page, one native
`FragmentHandle` per Edron fragment, and one native `ActionHandle` per Edron action.

### Full page request

For an ordinary page `GET`:

1. native routing and dependencies validate/authorize the request;
2. Edron constructs one fresh page instance and request-local root buffer;
3. generated title/chrome and canonical query inputs are bound;
4. `render()` runs once;
5. each called fragment creates a nested buffer and materializes initial content once on the same
   page instance;
6. all buffers validate and lower to native Hedron nodes/handles;
7. native page rendering, assets, security headers, cache policy, and response conversion run; and
8. the request context and page instance become unreachable after response cleanup.

If `render()` or initial fragment materialization fails, incomplete buffered output is discarded.
This does not roll back application I/O that the author incorrectly performed in a safe phase.

### Fragment request

For a fragment `GET`:

1. native route, HTMX facts, target allowlist, query/path binding, and dependencies validate;
2. Edron creates a new page instance and fragment buffer;
3. only the addressed fragment method runs once;
4. the result lowers to the exact registered native fragment host/response contract; and
5. native generation/target/cache/history policy decides whether the browser may apply it.

`render()` does not run. A fragment cannot depend on page-local values created during a previous
page request. Every required application value must be a parameter, dependency, session read,
cache result, or durable service read with an explicit owner.

### Action request

For an unsafe action request:

1. native route identity, method, content type, body limits, CSRF, dependencies, and authorization
   validate before application mutation code;
2. bound values and the optional Pydantic model validate without shadowing dependencies;
3. native idempotency/revision policy validates when declared;
4. Edron creates a fresh page instance in the `action` phase;
5. the addressed action runs once for the accepted operation;
6. its native outcome/effects validate against registered targets and safe redirects;
7. the native response compiler produces HTMX or ordinary HTTP behavior; and
8. dependency cleanup and interaction trace finalization run.

`render()` and fragment methods do not run as ordinary Python during the mutation. A returned
`RefreshIntent` may cause separate safe fragment requests after the mutation response.

## Query and filter state

### Canonical binding

Every safe input has an explicit `name`. The current request query is parsed through the control's
declared type and the addressed fragment signature. Defaults are source declarations, not hidden
session values. Empty/unknown option values, duplicate fields, invalid numbers/dates, missing
required parameters, or incompatible control/fragment types produce a validation error before the
fragment body runs.

Inputs connected to the same fragment form one coherent `GET` filter group. Each submission carries
all named values required by that fragment, not only the changed control. Independent or overlapping
graphs use explicit `self.filters(name=..., updates=...)`; Edron never emits nested forms.

Only registered safe page/filter parameters are preserved when Edron builds a canonical URL.
Unrelated unregistered parameters are not copied automatically. Default-valued parameters may be
omitted from the canonical URL only when omission and explicit value validate identically.

### History behavior

| Interaction | Enhanced history | Ordinary fallback |
|---|---|---|
| Initial page navigation | Normal browser entry | Normal browser entry |
| Change-triggered filter | Replace current URL after successful validated response | Visible `GET` submit creates normal navigation |
| Explicit filter submit | Push canonical URL after successful response | Normal `GET` navigation |
| Invalid filter | Do not update history | Validation response at submitted URL under browser rules |
| Back/forward | Native history restore or full page GET | Full page GET |

The URL shown after a successful enhanced filter is sufficient to reproduce the validated filter
state through an ordinary full-page request. Sensitive/private values are ineligible for query
ownership and cannot be made safe by disabling history.

### Filter concurrency

The Edron default for one filter group/target is native `latest` generation semantics:

- a newer filter request supersedes older pending presentation for that target;
- transport cancellation is attempted where supported but is not correctness authority;
- a late response with an older generation is recorded as stale and not swapped;
- different targets do not supersede each other unless they share an explicit native sync group;
- no filter request is queued without an explicit advanced native policy; and
- `GET` remains safe/repeatable even when a cancelled request continues on the server.

## Fragment interaction contract

A fragment method is a safe renderer. Edron compiles it to native `FragmentHandle`,
`ComponentRef`, host, target allowlist, fallback, cache facts, and source provenance.

Calling a fragment in an output phase means “bind, mount, and materialize this registered view,” not
“call an arbitrary helper.” A parameterized fragment must have a complete canonical binding before
mount. The same bound identity drives initial content, refresh controls, effects, tests, and
explanation.

Fragment requests must:

- use `GET` and remain free of application mutation by contract;
- target exactly their registered host/allowlist entry;
- reject missing/conflicting/undeclared `HX-Target` facts under native fail-closed policy;
- vary page/fragment representations on the native HTMX/history/target fields;
- retain the host's semantic tag, accessible name, busy state, and focus behavior; and
- remain directly usable as an ordinary HTTP fallback.

An advanced native component may use explicit swap, OOB, preload, extension, or cache options. Edron
does not shadow them with partial equivalents.

## Actions and forms

### Mutation boundary

Edron action controls never return a Boolean and render never branches on a button result. Passing
`action=self.save` constructs a native control; calling `self.save()` during render raises a phase
error.

Actions use `POST` by default. `PUT`, `PATCH`, and `DELETE` are allowed only through the explicit
decorator option and retain native CSRF and fallback form-method behavior. `GET` is not accepted by
`@ed.action`.

`.bind(...)` provides application arguments structurally. Bound values remain editable/untrusted
request values and must be authorized against the current subject/tenant/domain record inside the
server boundary. A hidden `customer_id` does not prove that the current user can delete it.

### Pydantic form state

`self.form(Model, action=...)` creates one native unsafe form. Pydantic/native binding is the
authoritative parse/validation boundary. Application code receives a model instance only after:

- body and field-count limits;
- CSRF and content-type checks;
- field alias/duplicate handling;
- type/constraint/discriminator validation;
- sensitive-field policy; and
- bound/dependency namespace separation.

On validation failure, the action does not run. Safe submitted values may be retained in semantic
controls; secrets, passwords, tokens, file bodies, and fields marked sensitive are not echoed.
Errors are associated with fields and summarized accessibly.

### Ordinary HTTP and HTMX parity

| Outcome | HTMX path | Ordinary HTTP/no-JavaScript path |
|---|---|---|
| Validation failure | Native `422` form/error fragment targeted to registered form/errors | Native `422` semantic page/form response |
| CSRF failure | Native fail-closed error, normally `403`; no success swap | Same status; action not invoked |
| Authorization denial | Dependency/application `401`/`403` policy | Same authoritative denial |
| Conflict/revision failure | Native `409` conflict state/region | `409` page/form response |
| Accepted async work | `202` pending/status target | `202`/local status navigation under native flow |
| Successful refresh intent | Validated refresh events/requests for registered targets | Local `303` to owning/explicit fallback, then safe `GET` |
| Successful direct result | Registered primary/OOB response | Semantic result or local PRG fallback |
| Safe local redirect | Validated `HX-Redirect`/location behavior | Local `303`/document redirect |
| Unhandled exception | Native error policy; no success lifecycle | Same server error policy |

Success meaning is the same on both paths even when presentation differs. Edron must not make an
action correct only when HTMX is present.

### Confirmation

`confirm=` is a presentation/control flow around an unsafe native submission. It must support
keyboard, focus, cancel, assistive technology, and an ordinary unsafe form fallback. It does not:

- change the action method;
- authorize a record;
- provide CSRF or idempotency;
- prove user intent to an external service; or
- make an irreversible action optimistically safe.

## Operation lifecycle

Edron consumes the native closed action lifecycle:

```text
idle -> pending -> success | error | cancelled | stale | conflict
```

Native transition helpers and schemas remain authoritative. Edron does not publish a second enum or
transition function. One operation identity has monotonic transitions: after a terminal state it
cannot return to pending or success again.

| Phase | Meaning in Edron presentation |
|---|---|
| `idle` | No accepted operation is pending for this control/target |
| `pending` | A request was submitted; server acceptance/commit is not yet proven |
| `success` | An authoritative response accepted the operation generation |
| `error` | Validation, transport, authorization, server, or declared failure presentation |
| `cancelled` | Presentation/operation cancellation was acknowledged under native policy |
| `stale` | Response belongs to a superseded generation and cannot update current presentation |
| `conflict` | Authoritative revision/idempotency/domain conflict requires reconciliation |

Browser-provided phase/status is never accepted as server proof. Aborting a request or marking it
cancelled does not undo server mutation. A timeout produces uncertain presentation until policy
reconciles through a status/refetch; it must not be reported as success or assumed rollback.

### Default concurrency policies

| Interaction | Edron default | Rationale |
|---|---|---|
| Filter/fragment change | native `latest` per filter group + target | Newest safe presentation wins |
| Manual safe refresh | native `replace/latest` per bound target | Avoid unbounded duplicate reads |
| Unsafe action/button | native `drop` while that control operation is pending | Reduce accidental browser duplicates; server policy remains authoritative |
| Unsafe form submit | native `drop` while pending | Preserve one visible submission lifecycle |
| Job poll | one in-flight request per job target; drop overlapping tick | Polling never queues |
| Full navigation | native navigation generation policy | Late partial navigation cannot replace current document target |

These browser/transport policies are not idempotency guarantees. An ordinary double submission,
retrying proxy, disconnected client, or server retry can still repeat a mutation unless the
application/native action uses authoritative idempotency.

### Idempotency

With `idempotency="application"`, Edron makes no replay-safety claim. With
`idempotency="required"`:

- a bounded idempotency key is required before mutation;
- an Edron-rendered control/form obtains a server-issued native submission key automatically;
- the same rendered logical submission keeps that key across double-submit and transport retry,
  while a newly rendered logical command receives a new key;
- the ordinary no-JavaScript form carries the same native key semantics as the HTMX request;
- the server scopes it to app, action, authenticated subject/tenant, and policy lifetime;
- the canonical validated application payload is associated with the key;
- the same key and same payload returns/replays the authoritative recorded disposition;
- the same key with a different payload fails as conflict;
- store unavailability fails closed before mutation; and
- CSRF tokens, DOM IDs, query strings, and operation generation are not substituted for the key.

Transaction/commit and idempotency-record atomicity are application/native backend concerns.
Edron diagnostics must not claim replay safety if that atomic boundary is unavailable.

## Updates and multi-target effects

`updates=` declares default success refresh targets. `ed.refresh(...)` returns the native refresh
intent. A refresh intent asks each mounted fragment to perform its ordinary safe GET; it does not
call fragment functions inside the action or invalidate a cache automatically.

Properties:

- targets are exact registered native handles/bound fragments from the active app;
- target count/fan-out is bounded;
- duplicates coalesce in deterministic declaration order;
- absent/unmounted targets do nothing safely;
- target requests run their normal dependencies, validation, cache, and authorization;
- the ordinary action fallback redirects/reloads the owning page rather than depending on events;
  and
- multiple refresh requests are not an atomic read transaction.

Native `Patch`/`PatchSet` may deliver one primary and bounded OOB updates in one response when the
application already has authoritative content. A target must use one OOB mechanism. Reserved sinks
such as toast/errors retain native rules. Arbitrary CSS selectors and client-provided retargeting
are not accepted.

If several views must represent one exact committed revision, the application must expose that
revision and make each read consistent or return a revisioned native patch. Edron does not promise
atomic UI merely because several targets refresh after one action.

## Stale responses, revisions, and conflicts

A response may update presentation only if all relevant facts match:

- active application and registered surface;
- target/host identity and allowed swap mode;
- operation or navigation generation;
- canonical bound instance identity;
- compatible server/domain revision when declared; and
- current scope/authorization.

When a generation mismatch is detected, the response becomes `stale`: it is traced in bounded
redacted form and is not swapped. Stale rejection never rewinds a committed mutation.

Durable edits that can conflict should use an application revision/ETag/version. An authoritative
revision mismatch returns native `409 conflict`, preserves server truth, presents recovery, and
requires refetch/retry under application policy. Edron does not silently last-write-win or merge
domain models.

## Optimistic interaction disposition

Generic optimistic mutation is excluded from Edron 0.1. Edron controls are server-confirmed by
default. The following cannot be optimistic through the Edron facade:

- authorization/identity/tenant changes;
- secrets, credentials, payments, external side effects, or irreversible destruction;
- job completion/cancellation truth;
- uploads/download authorization; and
- any mutation without a native inventoried reversible adapter, base revision, idempotency key,
  confirmation, rollback, conflict presentation, and server revalidation.

An advanced application may compose a native Hedron `OptimisticMutation` that is Supported for its
specific risk class. That native object retains its own authority and maturity; Edron does not infer
optimism from a button, dataframe edit, `variant`, or expected return type.

## Sessions

Edron 0.1 deliberately exposes no `session_state` dictionary or page-field persistence. Typed
session state is consumed through the native host adapter as a dependency:

```python
from hedron import SessionState, session_state
from pydantic import BaseModel


class Preferences(BaseModel):
    density: str = "comfortable"


class Settings(ed.Page):
    preferences: SessionState[Preferences] = ed.dependency(
        session_state("preferences", Preferences)
    )

    def render(self) -> None:
        self.text(f"Density: {self.preferences.value.density}")
```

`session_state(...)` remains the native session dependency declaration; `ed.dependency(...)` only
places that declaration on the request-scoped page instance.

Session rules:

- signing/storage/secret/expiry/cookie policy belongs to the host/native app;
- data is typed, bounded, versioned/migrated where required, and user-scoped;
- page/fragment safe phases read session state but do not perform hidden writes;
- writes occur in explicit unsafe actions or approved native auth/preference flows;
- sessions do not hold page/container/component/dependency instances, open connections, job
  results, or unbounded data; and
- session values do not enter public cache keys, URLs, browser history, or diagnostics unredacted.

Multi-worker claims require a session mechanism whose chosen semantics work across workers. A
process-local dictionary is not a session backend.

## Dependencies and resource lifetime

`ed.dependency(...)` is request state owned by native DI. It resolves lazily for the addressed page,
fragment, or action request and may be cached once per request under `use_cache=True`. Async
generator/resource cleanup occurs after response completion under native ordering.

Dependencies may provide repositories, authorization context, session adapters, clients, and
transaction factories. They are not:

- automatically serializable state;
- accessible during registration/static explanation;
- bindable through query/form/action data;
- persisted on the page class; or
- safe to retain in detached tasks after request cleanup.

An action owns its transaction boundary explicitly. Edron does not open or commit a transaction
because an action decorator is present.

## Cache state

`ed.cache_data(...)` stores derived/recomputable results through native bounded cache policy.

| Scope | Required key partition | Intended use |
|---|---|---|
| `request` | current request | Avoid duplicate computation within one request |
| `private` | authenticated/session subject plus args | User-specific derived data |
| `tenant` | authoritative tenant plus args | Tenant-shared derived data |
| `public` | callable/version plus non-secret args | Truly public cross-user data |

`public` is never inferred. Authentication-sensitive responses default to private/no-store HTTP
behavior independently of function caching. Cache values do not become durable truth, and cache
loss/restart may affect performance only.

Invalidation is explicit (`invalidate(...)`/`invalidate_all()`) and should occur after an
authoritative mutation/commit. Invalidation does not commit or roll back domain state and cannot
replace a revision check. Cache stampede limits, TTL, maximum entries/bytes, serialization, and
backend ownership are native acceptance concerns.

## Durable application state

Databases and application services own customers, reports, permissions, audit records, and other
domain values. Edron neither supplies nor infers an ORM/repository/unit-of-work.

Every unsafe domain action is responsible for:

- current authorization and tenant scope;
- validation beyond presentation/Pydantic structure;
- transaction and external side-effect boundaries;
- revision/conflict behavior;
- audit requirements;
- idempotency/replay policy; and
- deciding which caches/views become stale after commit.

Page visibility and previously rendered object IDs do not substitute for these checks.

## Job state and polling

`JobFlow` projects native `TaskFlow`/`JobBackend` state. The backend is authoritative for queued,
running, succeeded, failed, cancellation-requested/cancelled, expired, and result metadata. Edron's
page/fragment state is only presentation.

Rules:

- submission validates and authorizes before enqueue;
- the worker validates its payload again at its trust boundary;
- submit/status/cancel/result share one authoritative `JobScope`;
- unknown or mismatched scope returns `404` without existence disclosure;
- cancellation is a request until the backend records an authoritative terminal state;
- one poll is in flight per job target; overlapping timer ticks drop rather than queue;
- polling interval and retry/timeout/retention are bounded;
- polling stops on success, failure, cancellation, expiry, or unrecoverable error;
- a stale poll response cannot replace a newer terminal generation; and
- an opaque download ID/result is resolved through an authorized provider, never a filesystem path.

The no-JavaScript path can submit, navigate to status, and manually refresh. Polling is the
Supported enhancement. Live transports remain native experimental composition.

## Browser-local state

Browser-local state may own only presentation whose loss does not corrupt server truth, including:

- disclosure/tab open state;
- focus/scroll restoration;
- pending/busy indicators;
- non-secret draft presentation explicitly allowed by a native component;
- theme/color-mode preference under the native preference contract; and
- bounded reversible state of an approved native Web Component.

It cannot own authorization, current tenant, accepted form validity, durable revision, action
success, job completion, upload acceptance, or secret data. `localStorage`, history state, DOM
attributes, cookies visible to scripts, and HTMX state are all attacker-controlled from the
server's perspective.

Browser state transfer across a fragment replacement is opt-in, schema-compatible, target-bound,
and bounded. A component state field has one writer; HTMX and a Web Component cannot both own it
without an explicit native handoff contract.

## HTMX contract

HTMX is a progressive transport over native HTTP contracts. Edron generates/uses native handle
metadata rather than author-facing endpoint strings for ordinary interactions.

### Requests

- fragment/filter requests are `GET` with canonical query values;
- actions/forms are explicit unsafe methods with native CSRF;
- `HX-Target` must match the route's registered allowlist;
- `HX-Request`, history-restore, target, current URL, sync, and operation facts are parsed/validated
  by native Hedron helpers; and
- client headers are hints/input, not proof of authorization or lifecycle.

### Responses

- native response conversion selects page versus fragment representation;
- target/retarget/reselect/OOB values use registered `ComponentRef`/region identity and safe selector
  policy;
- local redirects/history updates use native URL validation;
- cache/Vary includes the required HTMX/history/target dimensions;
- assets are registry planned and deduplicated across full and fragment responses;
- response-provided scripts/CSS do not become an Edron interaction mechanism; and
- errors retain native HTTP status and accessible target/fallback presentation.

The optional native `hedron` HTMX extension may improve lifecycle markers, generation-aware stale
handling, focus, announcements, and traces. An application without the extension still works with
ordinary HTMX and full HTTP fallback. Edron does not require user-authored JavaScript for the golden
applications.

### History restore

History restoration rebuilds authoritative URL/page state. It does not revive a page instance,
dependency object, action result, CSRF token, job authorization, or durable snapshot from browser
memory. Sensitive/authenticated pages use private/no-store policy and native history safeguards.

## Accessibility interaction behavior

- Every input/action has an accessible label independent of `name`/identity.
- Busy state is associated with the initiating control and affected region without moving focus
  prematurely.
- Filter updates normally retain focus on the changed control and announce a concise result change
  only when useful.
- Validation failure focuses or links to a semantic error summary and associates field errors.
- Success/error/conflict/cancelled/stale states do not produce duplicate or high-frequency live
  announcements.
- A deleted control moves focus to a deterministic surviving neighbor/section or page heading under
  the native focus policy.
- Confirmation is keyboard/assistive-technology operable and has an unsafe no-JavaScript path.
- Job polling announcements are rate-limited and announce meaningful state transitions rather than
  every tick.
- Reduced motion, forced colors, zoom/reflow, RTL, print, and no-JavaScript paths preserve meaning.

Focus and announcement behavior belongs to native host/component/interaction contracts. An Edron
variant/theme cannot change semantic state or suppress the only authoritative message.

## Cache, privacy, and history policy

| Content | Default HTTP policy |
|---|---|
| Authenticated page/fragment | `private, no-store` under native authenticated policy |
| Page/fragment sharing one URL | Vary on HTMX/history and target when required |
| Validation/action error | Private/no-store unless stricter native policy |
| Public anonymous safe fragment | Private/no-store by default; explicit reviewed native public cache policy required |
| Job status/result | Private/no-store and scope-authorized |
| Static fingerprinted assets | Native immutable asset policy |

Edron does not infer public response caching from `cache_data(scope="public")`; function-result
caching and HTTP response caching are separate authorities. Query strings, browser history,
referers, logs, traces, and cache keys must not receive secrets or sensitive form/session values.

## Static explanation and observability

Plain `edron check` projects conservative static source facts only; it neither imports the
application nor claims native registration success. `edron check --register` and `edron explain`
cross the disclosed trusted-import boundary, seal/project the native interaction catalog, handle
descriptors, route/effect graph, dependency metadata, policies, assets, and Edron source map. None
of these modes executes page renderers, fragments, actions, dependency providers, jobs, or data
loaders merely to fill an explanation gap.

For each surface, explanation includes where applicable:

- Edron page/method/control source;
- native handle/logical ID, method, path disposition, fallback, and target;
- bindable parameters versus server dependencies;
- state owner/lifetime/sensitivity/cache/history disposition;
- action method, CSRF, authorization dependencies, idempotency, concurrency, and effects;
- operation identity/generation/revision policy;
- no-JavaScript behavior and known limitations; and
- native diagnostic/trace schema versions.

Runtime traces are bounded, versioned, and redacted. They may record names, phases, durations,
status, generations, target IDs, categorical errors, truncation, and correlation IDs. They must not
record secrets, full private payloads, session contents, bound record values, dependency reprs,
download identifiers, or unrestricted URLs.

Explanation is a projection, not another route/state/effect registry.

## Errors and status mapping

Edron-owned state/binding failures use the stable codes in the
[public API contract](EDRON.md#stable-edron-diagnostic-codes). Native validation, CSRF,
authorization, target, transition, cache, session, job, and response failures retain their
documented `HED-*` code and causal chain.

| Situation | Required result |
|---|---|
| Output or dependency access outside request | `EDR-PHASE-0001` |
| Action called during render | `EDR-PHASE-0002` |
| Duplicate/ambiguous filter binding | `EDR-BIND-0001` / `EDR-BIND-0004` |
| Invalid typed query/form value | Native `422`; application fragment/action not invoked |
| Dependency client shadow attempt | `EDR-DEP-0002` before application code |
| Cross-app/stale target reference | `EDR-BIND-0005` or native fail-closed target error |
| Missing/invalid CSRF | Native fail-closed CSRF status, normally `403` |
| Authorization denial | Application/native `401`/`403` policy |
| Stale operation generation | Native `stale`; response not applied |
| Revision/idempotency conflict | Native `409 conflict` |
| Required idempotency store unavailable | Fail closed before mutation, normally `503` |
| Unknown/mismatched job scope | `404` without disclosure |
| Rate/resource limit | Native/Edron bounded error, normally `413`, `422`, or `429` by boundary |

An interaction failure must not be rewritten as HTTP 200 success merely to make a fragment swap
convenient. Native error retarget/reswap behavior may render a useful region while preserving the
authoritative status and trace.

## Resource bounds and performance

Stage 0 freezes numeric limits for:

- controls/filter groups/parameters per page and target fan-out;
- query/body/file bytes and collection cardinality;
- output nodes/nesting/fragment hosts/OOB updates;
- concurrent requests per filter/action/job target and queued operations (zero by default);
- idempotency key/payload/result bytes and retention;
- session/cache entries and bytes;
- job payload/status/result/poll interval/attempts/retention;
- operation/trace events and serialized bytes; and
- history/prefetch/browser state retention.

Limit exhaustion fails predictably and does not silently drop authoritative fields, authorize a
partial mutation, or emit half of a target plan. Registration-time analysis is preferred over
repeated request introspection. Interaction metadata and traces are lazy/bounded and must not add a
persistent browser loop.

## Testing strategy

The state/interaction acceptance suite includes:

1. **Owner tests:** every golden value has one documented owner, writer, lifetime, sensitivity,
   cache/history, and restart disposition.
2. **Lifecycle tests:** page/fragment/action fresh instances, initial fragment materialization,
   phase refusal, context cleanup, async/cancellation, and no detached output.
3. **Binding tests:** canonical query values, defaults, typed conversion, coherent multi-control
   groups, explicit group partition, duplicate/ambiguous names, and cross-app binding.
4. **Parity tests:** every filter/form/action/job flow works through HTMX and no-JavaScript ordinary
   HTTP with equivalent authoritative meaning.
5. **Concurrency tests:** rapid filters, double action/form submit, overlapping polls, late
   responses, navigation, generation/revision mismatch, timeout, and disconnect.
6. **Idempotency tests:** same/different payload replay, subject/tenant/action scope, expiry, store
   outage, transaction uncertainty, and ordinary double submission.
7. **State backend tests:** typed session validation/migration/expiry, multi-worker session behavior,
   cache scopes/invalidation/restart, durable repository revisions, and job backend scope/terminal
   behavior.
8. **HTMX tests:** target allowlists, OOB conflicts, safe redirects/history, Vary/cache, assets,
   extension-present/absent behavior, and full fallback.
9. **Security tests:** CSRF, authz/tenant recheck, hidden-field tampering, dependency shadowing,
   secret leakage, cache poisoning/cross-scope access, job enumeration, open redirect, and trace
   redaction.
10. **Accessibility tests:** focus, busy, validation, conflict, confirmation, delete recovery, live
    announcements, polling rate, reduced motion, forced colors, zoom/reflow, and keyboard-only/no-JS.
11. **Differential tests:** Edron fixtures and explicit native Hedron lowerings produce equivalent
    methods, bindings, handles, policies, transitions, effects, cache/history, statuses, and traces.
12. **Static explanation tests:** deterministic output without callback/dependency execution and
    without secret/private-value disclosure.

Browser concurrency tests run against the supported engines, but server/multi-worker tests remain
the authority for persistence and replay correctness.

## Compatibility and migration

This contract is additive over native Hedron state and interaction APIs. Existing native
`SessionState`, `FragmentHandle`, `ActionHandle`, `InteractionPolicy`, `ActionState`,
`OperationIdentity`, `RefreshIntent`, `Patch`, `PatchSet`, `TaskFlow`, `OptimisticMutation`, HTMX extension,
and full route/response APIs remain usable through `app.hedron` and native imports.

Moving a native application surface into Edron must preserve:

- HTTP method/path compatibility when the path was explicitly public;
- typed request and dependency boundaries;
- state owner/lifetime and cache/history privacy;
- CSRF/authz/tenant/idempotency/revision behavior;
- target/effect allowlists and no-JavaScript fallback;
- operation generation/stale/conflict behavior; and
- job/result scope and durability claims.

Generated Edron paths/DOM IDs are not migration compatibility promises. Authors who need a public
path or persistent handle key declare it before migration.

Edron never migrates a Streamlit `session_state` dictionary wholesale. Each field receives an
explicit URL/form/session/durable/cache/browser/deferred disposition under RFC-0061 analysis.

## Acceptance criteria

- **EDR-SI-OWNER-001:** Every public/golden state value has one authoritative owner, writer,
  lifetime, sensitivity, cache/history, and restart disposition.
- **EDR-SI-LIFECYCLE-001:** Registration/page/fragment/action phases, fresh instances, nested initial
  fragments, async propagation, cancellation, cleanup, and phase errors pass.
- **EDR-SI-FILTER-001:** Typed coherent GET filters, canonical URLs, history, latest-generation
  concurrency, stale rejection, and full fallback pass.
- **EDR-SI-ACTION-001:** Unsafe method, binding, Pydantic validation, CSRF, authorization,
  confirmation, outcome, effects, PRG, and HTMX parity pass.
- **EDR-SI-IDENTITY-001:** App/surface/binding/operation/revision/job/cache identity and collision/
  redaction rules pass without secrets in public identity.
- **EDR-SI-CONCURRENCY-001:** Rapid filters, duplicate mutations, polling, navigation, late response,
  disconnect, timeout, stale, and conflict fixtures satisfy the frozen policies.
- **EDR-SI-IDEMPOTENCY-001:** Required idempotency is authoritative, scope/payload-bound, fail-closed,
  and honest about transaction atomicity.
- **EDR-SI-STATE-001:** Session, cache, durable, dependency, job, and browser owners pass restart and
  multi-worker tests appropriate to their claims.
- **EDR-SI-HTMX-001:** All enhanced requests/responses use native handles, targets, policies,
  statuses, history, cache, assets, extension, and ordinary HTTP fallback.
- **EDR-SI-OPTIMISM-001:** Generic Edron optimistic mutation is absent; native approved adapters keep
  their revision/rollback/reconciliation authority and maturity label.
- **EDR-SI-SECURITY-001:** Cross-scope, CSRF, authz, hidden-field, dependency, cache, job, redirect,
  history, and trace adversarial matrices pass.
- **EDR-SI-A11Y-001:** Keyboard/focus/busy/error/conflict/confirmation/polling/live-region and
  preference/no-JS evidence passes.
- **EDR-SI-EXPLAIN-001:** Static/runtime state and interaction projections are deterministic,
  native-derived, bounded, versioned, source-linked, and redacted without executing callbacks.
- **EDR-SI-PERF-001:** Numeric state/interaction resource budgets are frozen and pass equivalent
  native-versus-Edron benchmarks.

## See also

- [Edron 0.1 public API](EDRON.md)
- [Edron packaging](EDRON_PACKAGING.md)
- [Edron capability inventories](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_CAPABILITY_INVENTORIES.md)
- [Edron implementation specification](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_001.md)
- [Edron acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_001.md)
- [RFC-0094](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md)
- [Edron golden applications](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_GOLDEN_APPS.md)
- [Native state APIs](STATE.md)
- [Native interaction APIs](INTERACTION.md)
- [Refreshable views and commands](REFRESHABLE_VIEWS.md)
- [Action API](ACTION.md)
- [Phase 0.62 interaction contracts](INTERACTION_062.md)
- [Hedron HTMX extension](HTMX_HEDRON_EXTENSION.md)
- [Jobs](JOBS.md)
- [Cache](CACHE.md)
- [Security types](SECURITY_TYPES.md)
- [Accessibility](A11Y.md)
