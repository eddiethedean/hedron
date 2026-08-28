# Hedron 1.0 HTMX/Alpine boundary

**Status:** Verified normative contract for Hedron 1.0; implemented from the 0.67 preview
**Decisions:** D-114 / D-115 / D-116 / D-117
**Owning RFCs:**
[RFC-0095](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0095-ALPINE-BROWSER-ENHANCEMENT.md)
and
[RFC-0096](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md)  
**Evidence:** `FREEZE-067`, `INTERACTION-067`, `HTMX-067`, `STATE-067`, `FAILURE-067`,
and `INTERACTION-100`

This contract defines the authority boundary between HTMX and Alpine in Hedron 1.0. Its central
rule is:

> Hedron authors the contract and server truth, HTMX performs server communication and HTML
> replacement, Alpine performs disposable browser-local interaction, and the Hedron lifecycle
> coordinator hands control between them without becoming a third application runtime.

Neither library is a general substitute for the other. An interaction uses Alpine, HTMX, or one
explicitly coordinated combination according to the work it performs.

## Authority at a glance

| Concern | Authority | Other participants must not |
|---|---|---|
| Routes, authorization, tenancy, CSRF, mutation, validation, durable state | Hedron/application server | Trust Alpine or HTMX attributes as proof; move correctness into browser state |
| HTTP request dispatch and cancellation | HTMX | Let Alpine call `fetch()`, `XMLHttpRequest`, or `htmx.ajax()` as a parallel request path |
| Request method, URL, target, swap, synchronization, and fallback policy | Typed Hedron handle/`Interaction`; executed by HTMX | Let Alpine rewrite `hx-*`, action URLs, target identity, or concurrency policy at runtime |
| Authoritative response content | Hedron/application server | Return client templates or executable response scripts; let Alpine reconstruct server truth |
| Placement of returned HTML | HTMX within the declared target/OOB policy | Let Alpine perform server-response insertion or let HTMX write outside authorized regions |
| Ephemeral component state and local presentation | Alpine | Store domain truth, permissions, secrets, canonical validation, or job results |
| Local DOM projection inside a live Alpine root | Alpine | Give HTMX/lifecycle code an independent writer for the same property or state |
| Root initialization, cleanup, swap handoff, and reconciliation | Hedron lifecycle coordinator using documented upstream surfaces | Double-initialize, double-clean, or call undocumented Alpine internals |
| URL and navigation history | Hedron navigation policy, executed by native navigation or HTMX | Let Alpine create a second canonical navigation/history mechanism |
| Semantic fallback and initial accessibility state | Server-rendered HTML and native elements | Make either library the only way to understand or operate essential content |
| Focus, busy state, announcements, and interaction presentation | One declared interaction policy, projected locally by Alpine when present | Let Alpine and the HTMX extension independently announce, focus, disable, or mark the same event |
| Browser assets and plugins | One immutable Hedron document feature plan | Install scripts, plugins, stores, or modules from a fragment response |
| Specialist browser subsystem | Its selected Web Component host under the public element ABI | Let Alpine traverse element-owned DOM or let the element acquire request/domain authority |

## Relationship to Web Components

Web Components remain a first-class Hedron 1.0 capability. They are selected for specialist,
independently reusable browser subsystems such as charts, maps, and the data editor—not as a wrapper
around every interactive control. The bidirectional selection rules and current tag dispositions
are defined in the
[component engine plan](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/COMPONENT_ENGINE_DISPOSITIONS_067_1_0.md).

Within a selected Web Component, the element owns its documented internal DOM, resources, typed
properties/events, and cleanup. Alpine may coordinate from outside through those properties and
events but cannot traverse or rewrite element-owned DOM. The element cannot boot a hidden Alpine
application, mutate an enclosing Alpine store, or originate application requests. HTMX may replace
the whole element or a declared server-owned light-DOM region; it cannot replace element-owned DOM
in place.

The one-writer rule applies across all three browser mechanisms. For example, Alpine may own which
tab exposes a chart, the chart element owns visualization rendering and viewport state, and HTMX
owns a server fragment replacement. None of them independently writes the other's selection,
pending, focus, or announcement state.

## Alpine's role

Alpine is Hedron's browser-local behavior engine for common components. It owns work that can be
completed using values already authorized and present in the current document:

- disclosure, tabs, menus, dialogs, popovers, tooltips, and local overlay state;
- focus movement, focus return, keyboard behavior, geometry, anchoring, and transitions;
- filtering or sorting an already-rendered bounded collection;
- input masks, character counts, copy controls, and non-authoritative validation hints;
- disposable pending/success/error presentation received from the lifecycle coordinator; and
- bounded, non-sensitive presentation preferences when the Persist plugin is explicitly admitted.

Alpine state is replaceable. Losing it during navigation, an ordinary HTMX replacement, asset
failure, or storage clearing must not corrupt domain state or change authorization. Alpine may
read native form values and reflect presentation, but the native control remains the submitted
value and the server remains the validation authority.

Alpine must not:

- originate application HTTP requests through a second request API;
- decide authorization, tenancy, CSRF validity, mutation success, or canonical form validity;
- hold secrets, tokens, complete user records, authoritative job state, or unsaved domain truth;
- generate authoritative response HTML from JSON or client templates;
- rewrite HTMX methods, URLs, targets, swap modes, synchronization, or history policy;
- preserve local state across server updates unless the interaction declares a bounded,
  versioned reconciliation contract; or
- use `x-cloak` or another pre-initialization hiding rule for essential content or the only usable
  control.

## HTMX's role

HTMX is Hedron's enhanced request and server-HTML transport. It owns:

- dispatching declared HTTP requests from links, forms, controls, and interaction handles;
- applying request headers and browser request lifecycle behavior;
- cancellation and synchronization according to the declared concurrency policy;
- placing authoritative HTML into a validated target with the declared swap mode;
- out-of-band updates, ordinary boosted navigation, and approved history behavior; and
- exposing documented request/swap lifecycle events to the Hedron coordinator.

The Hedron declaration—not arbitrary browser mutation—defines the request method, route identity,
target, swap, fallback, and concurrency policy. The server revalidates every security-sensitive
fact. HTMX transports and places the response; it does not become a client data layer.

HTMX must not:

- manage Alpine component data, stores, watchers, transitions, or local widget logic;
- directly mutate an Alpine value to communicate request state;
- execute scripts or register Alpine modules supplied by a response fragment;
- replace native/server fallback with extension-dependent correctness;
- independently move focus, announce, disable, or mark busy when the same concern is owned by the
  unified interaction policy; or
- force a server round trip for behavior that is entirely local presentation.

## Hedron's coordination role

The lifecycle coordinator is a protocol adapter, not another state framework. It translates
documented HTMX lifecycle events and Hedron operation identity into the one declared interaction
state, then lets the active presentation engine render that state.

When Alpine is active, Alpine is the sole writer of Alpine-backed local presentation. The
coordinator publishes a bounded state transition to the registered Alpine component; it does not
also toggle the same classes, attributes, hidden state, disabled state, or text itself. When a
request-only interaction does not use Alpine, the existing HTMX extension may project the same
bounded lifecycle contract directly into semantic DOM. These are two lowerings of one policy, not
two simultaneous writers.

The coordinator owns only:

- operation identity, generation/revision correlation, and stale-result presentation;
- the ordered handoff before removal and after HTMX settle;
- exactly-once root initialization and cleanup outcomes;
- reset, retain, or versioned transfer of explicitly declared local state;
- one focus/announcement outcome per interaction; and
- a bounded, redacted trace joining the Python/HDJ declaration, request, swap, and local lifecycle.

It does not own routing, network transport, application data, component business logic, or a
general client store.

## The three interaction forms

One public `Interaction` value has exactly one closed effect variant.

| Variant | Use it when | Runtime | Required fallback |
|---|---|---|---|
| `local` | The result needs no new server data and changes only disposable presentation | Alpine only | Semantic/native document remains understandable and usable |
| `request` | The result depends on server data, validation, authorization, mutation, navigation, or durable state | HTMX, with native HTTP fallback | Ordinary link/form/full-page or full-fragment behavior |
| `combined` | One user intent needs immediate local presentation and one authoritative server operation | Alpine + HTMX through the coordinator | The server operation still works through an ordinary link/form when either enhancement is absent |

Invalid combinations fail during construction and static checking. A value cannot claim `local`
while carrying a request, or claim `request` while attaching unrelated Alpine effects. A
`combined` interaction has one initiating event and at most one request dispatch; independent
`x-on` and `hx-trigger` handlers must not both react to the same event as separate operations.

### Decision test

1. Does correctness require new or authoritative server information? Use `request`.
2. Can the entire result be derived from already-rendered, authorized, bounded values? Use `local`.
3. Does the same intent need both immediate local presentation and a server operation? Use
   `combined`.
4. Would losing the browser state change permissions, saved data, money, audit history, or workflow
   truth? That state belongs on the server regardless of interaction form.

## DOM ownership and swap rules

The rendered document has explicit server-replaceable regions and Alpine-local roots. Nesting is
allowed, but concurrent ownership of the same concern is not.

1. The server renders semantic initial markup, stable target/root identity, HTMX attributes, and
   normalized Alpine directives.
2. Alpine may project local state inside its live root. It must not change the surrounding HTMX
   control plane or the identity of an authorized replacement region.
3. Before HTMX removes or replaces a subtree, the coordinator produces the documented cleanup
   outcome for outgoing Alpine roots exactly once.
4. HTMX performs the declared replacement or OOB update.
5. After the final settled DOM is available, new Alpine roots initialize exactly once through
   documented Alpine surfaces.
6. If Alpine creates nodes containing HTMX attributes through `x-if` or `x-for`, those nodes enter
   HTMX through its supported `htmx.process()` path.
7. Local state resets after ordinary replacement unless an exact root identity, versioned schema,
   size limit, and reconciliation rule declare preservation.

No DOM property has two independent writers. The compiler/checker rejects, for example, an Alpine
binding and an HTMX lifecycle projection that both own `hidden`, `disabled`, `aria-busy`, the same
class/state token, focus destination, or announcement for one interaction.

Ordinary HTMX replacement with reset is the Supported baseline. An Alpine-aware Morph path, if
admitted, remains Progressive and obeys the same ownership, stale-state, cleanup, focus, and
accessibility rules. Morph does not create a new state authority or relax the one-writer rule.

## State transfer rules

| State class | Owner | May cross an HTMX replacement? |
|---|---|---|
| Open/closed, active tab, transient menu/filter state | Alpine component | Reset by default; retain only through a declared bounded schema |
| Document-wide presentation coordination | Alpine store | Only within the current document and only for non-sensitive presentation |
| Native form value | Native control, interpreted by server binding | Yes through normal submission; server response is authoritative |
| Pending/stale/error operation presentation | Hedron interaction identity, projected by Alpine or HTMX extension | Yes by matching operation generation/revision, never by guessing from DOM timing |
| URL/shareable filter/navigation state | Server/native navigation/HTMX history policy | Yes through the declared URL/history contract, not an Alpine-only copy |
| Session, domain record, permission, audit, payment, durable job | Application server | Never transferred into Alpine as authority |

A preserved local payload is data-only, finite, versioned, non-sensitive, and associated with one
stable root identity. Schema mismatch, stale revision, target mismatch, or excessive size resets
the payload safely; it never blocks the authoritative response.

## Failure and progressive-enhancement contract

| Failure | Required behavior |
|---|---|
| JavaScript disabled or both libraries unavailable | Semantic content, links, and forms provide the ordinary server path |
| Alpine missing, refused by CSP/SRI, slow, or plugin registration fails | Essential content remains visible; request/combined interactions retain native or HTMX server behavior without relying on local preflight |
| HTMX missing or fails to initialize | Alpine local behavior may continue; every server interaction falls back to an ordinary link/form/navigation |
| Request/network/server failure | HTMX/native HTTP owns transport outcome; the coordinator projects one error state and Alpine must not suppress or reinterpret it as success |
| Fragment requires an uninstalled Alpine feature | Server rejects it with a focused plan-mismatch diagnostic; the response cannot install the missing feature |
| Repeated swap/history restoration | No duplicate requests, handlers, roots, cleanup, announcements, focus moves, or observers |

No enhancement failure may leave essential content permanently cloaked, strand focus in a removed
subtree, suppress an authoritative server error, or convert a failed mutation into apparent local
success.

## Security boundary

- The Supported Alpine path uses the pinned CSP build and does not require `unsafe-eval`.
- Alpine expressions and bindings pass through sink-specific typed validation. `x-html` is not a
  canonical response or user-content path.
- HTMX requests use registered routes/handles and server validation for targets, methods,
  authorization, tenancy, CSRF, and redirects. Client attributes are never trusted evidence.
- Response fragments contain declarative markup only. They cannot install executable assets,
  register stores/plugins, or weaken the document CSP.
- Alpine Persist stores presentation preferences only. It never stores secrets, credentials,
  authorization results, protected records, or values whose loss changes correctness.
- Browser traces and diagnostics preserve operation identity but redact sensitive values.

## Accessibility boundary

The server owns meaningful initial semantics, accessible names, native form behavior, reading
order, landmarks, and the no-JavaScript path. Alpine owns keyboard and focus behavior intrinsic to
local widgets. HTMX owns replacement timing. The coordinator ensures one deterministic focus and
announcement outcome across the handoff.

For a combined interaction:

- Alpine may expose immediate pending presentation, but cannot announce success before the server
  result;
- HTMX may replace content, but cannot independently move focus when the interaction policy has a
  focus destination;
- outgoing Alpine roots release focus/observers before removal;
- server errors and validation messages remain in the semantic response; and
- reduced-motion, forced-colors, zoom/reflow, RTL, keyboard, and no-JavaScript behavior remain
  valid when either enhancement is absent.

Automated browser/a11y evidence does not create an unqualified human assistive-technology or WCAG
conformance claim.

## Examples

| Need | Correct owner/form | Incorrect design |
|---|---|---|
| Toggle a disclosure | Alpine `local` | HTMX request solely to toggle visibility |
| Filter 20 already-rendered authorized rows | Alpine `local` | Server mutation or client ownership of unrendered data |
| Search a database | HTMX `request` | Alpine fetching JSON and rendering results |
| Submit and validate a form | HTMX `request`, native form fallback | Alpine declaring the record saved before the response |
| Open a dialog and submit its form | `combined`: Alpine dialog/focus, HTMX submission | Separate click handlers issuing duplicate operations |
| Delete a record with confirmation | `combined`: Alpine confirmation presentation, HTMX/server mutation | Removing the row locally as proof of deletion |
| Update an authorized server fragment inside tabs | Alpine owns tab selection; HTMX owns the requested panel swap | HTMX and Alpine both writing active tab/focus state independently |
| Persist density preference | Alpine Persist when admitted | Persisting permissions, form truth, or a complete record |

## Advanced direct use

Direct low-level `hx-*`, typed Alpine values, and registered custom modules remain Advanced escape
hatches only for distinct capabilities. They still participate in the single document feature
plan, typed security sinks, lifecycle protocol, one-writer rule, diagnostics, and fallbacks. They
cannot introduce another ordinary request API, plugin loader, client store, response templating
system, or undocumented lifecycle path.

If direct HTMX and Alpine attributes reproduce a task already represented by `Interaction`, the
checker treats them as a duplicate 0.67 compatibility path rather than a second 1.0 authoring
style.

## Conformance requirements

The 0.67 preview and 1.0 cut must prove all of the following:

- every public interaction is classified as `local`, `request`, or `combined`;
- local interactions emit no request machinery and request-only interactions require no Alpine;
- combined interactions produce one event identity, at most one request, one lifecycle trace, one
  focus outcome, and one announcement outcome;
- no Alpine code originates application requests or changes the HTMX control plane;
- no HTMX/lifecycle code mutates Alpine state or duplicates Alpine-owned presentation;
- document feature closure prevents response-time script/plugin/module registration;
- ordinary replacement, OOB, delete, history, errors, and Alpine-created HTMX content pass in
  Chromium, Firefox, and WebKit;
- reset/preserve behavior is deterministic and stale local state cannot override server HTML;
- no-JavaScript, Alpine failure, HTMX failure, CSP/SRI failure, plugin failure, and slow-start
  fixtures retain the required fallback; and
- static checks report dual writers, mixed authorities, duplicate event/request bindings, unsafe
  state transfer, undeclared feature demand, and missing fallback at the source declaration.

This boundary is part of the frozen 1.0 task graph. Implementation details may change after
`FREEZE-067`, but neither HTMX nor Alpine may acquire a second overlapping responsibility without
an explicit superseding decision.

## See also

- [Current Hedron HTMX extension](HTMX_HEDRON_EXTENSION.md)
- [Current interaction contract](INTERACTION.md)
- [Phase 0.62 interaction contracts](INTERACTION_062.md)
- [Hedron stability classifications](STABILITY.md)
