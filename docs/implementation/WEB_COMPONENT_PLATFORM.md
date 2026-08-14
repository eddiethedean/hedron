# Web Component platform implementation

**Planning status:** Normative under Accepted
[RFC-0060](../rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md) (D-064).

This document specifies implementation boundaries for phases 0.36–0.41. Names are descriptive
unless the RFC and public API review promote them; private class/function names are not frozen.
The program moved from 0.34–0.39 to 0.35–0.40 under D-058, then to 0.36–0.41 under D-061;
scope and ordering are unchanged.
The companion [interaction-contract specification](WEB_COMPONENT_INTERACTION_CONTRACTS.md) defines
state ownership, asynchronous interaction, optimistic mutation, gesture/overlay, and React-migration
behavior on top of this platform.

## Distribution boundary

`hedron-elements` is a framework-neutral Python distribution containing:

- Python wrappers and typed element metadata;
- native ES modules and component CSS;
- registry/plugin contributions for assets, examples, diagnostics, and conformance;
- no FastAPI, Flask, Django, ASGI, or WSGI imports; and
- no install-time or application-time Node.js requirement.

It depends on `hedron-core`. Host packages mount its resources through the existing asset manifest.
Data, chart, extras, and future third-party packages may depend on its public metadata/authoring
surface without importing a host framework.

Browser source may use repository build tooling. Published wheels contain already-built, auditable
modules and source maps according to release policy. Phase 0.39 may publish identical module content
to npm with matching provenance and hashes.

## Registry records

The shared registry gains an element record with at least:

| Field | Meaning |
|---|---|
| `tag_name` | Valid custom-element name; `hedron-*` reserved for first party |
| `abi_version` | Element protocol version understood by markup and module |
| `module_asset_id` | Fingerprinted module resolved through the asset graph |
| `attributes` | Observed scalar attribute schemas and reflection rules |
| `structured_inputs` | Inert/property payload schemas, encodings, and byte/item limits |
| `properties` / `methods` | Explicit browser API, normally empty or small |
| `state_ownership` | Controlled/local/draft/preference modes and incoming-update policy |
| `events` | Detail schema, version, bubbles/composed/cancelable flags |
| `dom_policy` | Light/Shadow choice and server/element-owned regions |
| `form_contract` | **0.36:** reserved metadata stub only (association/value/reset/validation fields may be absent or null). **0.37+:** association, value, reset, restore, validation, fallback |
| `a11y_contract` | Semantics, keyboard/focus, states, live regions, limitations |
| `style_contract` | Scoped classes or supported tokens/parts/slots |
| `resources` | CSS, workers, fonts, WASM, adapters, remote origins, licenses |
| `lifecycle` | Cleanup and history obligations |
| `fallback` | Pre-upgrade/failed-upgrade behavior and capability label |

Registry sealing checks valid names, duplicate/conflicting definitions, missing assets, incompatible
ABI ranges, event/schema collisions, undeclared executable resources, and first-party prefix misuse.
Diagnostics redact structured values and never print element payloads by default.

## Markup protocol

Server markup includes the semantic fallback and only the configuration needed to initialize the
element. It identifies the ABI and logical definition without encoding executable behavior.

**Frozen public syntax (ABI-036):**

```html
<hedron-example
  data-hedron-abi="1"
  data-hedron-element="hedron-example"
  status="ready"
>
  <p data-hedron-server-region="content">Ready</p>
</hedron-example>
```

| Attribute / region | Rule |
|---|---|
| Tag name | First-party tags use the reserved `hedron-` prefix. The 0.36 reference element is **`hedron-example`**. |
| `data-hedron-abi` | Required positive integer ABI major understood by markup and module. |
| `data-hedron-element` | Logical definition id; must match the registered definition for the tag. |
| Scalar attrs (e.g. `status`) | Validated/contextually escaped strings; controlled fields reflect server authority. |
| `data-hedron-server-region` | Marks a server-owned light-DOM region eligible for authorized HTMX inner swaps. |
| Element-owned DOM | Must not use `data-hedron-server-region`; disjoint from server regions. |

Structured inputs (when declared) use one of two sealed paths:

1. an inert, escaped payload associated by collision-safe instance ID via
   `data-hedron-input="<instance-id>"` pointing at a sibling
   `<script type="application/json" data-hedron-input-for="<instance-id>" nonce="…">` (or host
   equivalent) that is never executed as JavaScript; or
2. a loader property assignment from a response-owned, validated value performed by the registered
   bridge after upgrade.

The serializer escapes `<`, closing-tag sequences, and context delimiters appropriate to the inert
container. The loader enforces the declared content type, schema, item/byte/depth limit, and instance
association before parsing. Payloads never create script text, handlers, CSS, arbitrary attributes,
trusted HTML, URLs, or methods.

The 0.36 reference element exercises controlled `status` text and disposable local UI state only;
it is **not** form-associated.

## Module protocol

Every module exposes static definition metadata and a deterministic registration entry. Registration
uses `customElements.get()` before `define()`:

- absent tag: validate metadata, then define;
- same definition and compatible ABI: no-op;
- existing incompatible/unknown definition: emit a diagnostic and leave fallback content intact.

Modules may share a small bridge, but definitions do not require a global singleton for correctness.
The bridge owns manifest negotiation, early HTMX cleanup hooks, diagnostics, and optional typed-event
mapping. It does not own rendering, routing, application state, or full-document mutation observation.

## Lifecycle state machine

```text
server fallback -> connected -> upgrading -> active
                       |           |          |
                       |           v          v
                       +------ failed <--- disposing -> disconnected
```

- `connected` may occur repeatedly; initialization is idempotent per connection.
- `upgrading` reads only declared configuration and retains fallback until success.
- `active` may modify only element-owned DOM and declared reflected state.
- `failed` reports a bounded diagnostic and preserves or restores fallback.
- `disposing` aborts owned asynchronous work before references are released.
- `disconnected` retains no listener, timer, observer, worker, object URL, focus trap, or adapter
  handle unless an explicit reconnect cache with a bounded lifetime is declared.

An `AbortController` per active connection is the default cancellation primitive. External adapters
must expose a deterministic dispose hook. Cleanup is called from `disconnectedCallback`; the HTMX
`beforeCleanupElement` bridge may call it early but cannot be the sole cleanup path.

## HTMX ownership rules

Each element declares zero or more server-owned light-DOM regions. HTMX may replace those regions
using the existing `FragmentRegion` authorization contract. Element-owned DOM is not an HTMX target.

- outer replacement: old element disposes; new markup upgrades as a new instance;
- inner server-region replacement: element receives normal DOM/connect callbacks and may reconcile
  only declared derived state;
- OOB replacement: follows the same ownership and authorization rules;
- history save: the element restores a canonical serializable view or marks disposable ephemera;
- history restore: correctness comes from saved server DOM, then a fresh idempotent upgrade.

The bridge attaches no inline handlers and evaluates no `hx-*` value as JavaScript. Typed element
events map only to already-registered actions/graph triggers and existing target allowlists.

## DOM and focus rules

Light DOM is the implementation default. An element-owned subtree is marked in metadata and in
rendered structure so tests can detect server/element ownership overlap. The element may not move or
delete server-owned children except through a documented slot-projection operation that is reversible
on failure and before history save.

Shadow roots are open unless an accepted exception demonstrates why a closed root is necessary.
Shadow elements expose documented slots and `part` names, consume public design tokens, delegate or
manage focus explicitly, and keep labels/descriptions programmatically connected. HTMX targets stop
at the host; server updates use host attributes/properties or declared light-DOM regions.

Focus restoration records an element-local stable focus key, not an arbitrary selector. On swap,
focus returns only when the target still exists and remains permitted; otherwise it follows the
component's documented fallback focus target.

## Events and server actions

The event catalog is generated from registry records and included in Explorer/conformance output.
Runtime detail validation is required at element boundaries in development and may be optimized in
production only when server validation remains complete.

The bridge translates an event to an HTMX request only when markup or registry metadata names a
registered action, request method, region, and payload mapping. The server treats all mapped fields
as ordinary untrusted request input and applies CSRF, authentication, authorization, tenancy, size,
and validation policy.

Asynchronous event/action flows use the shared `InteractionState` state machine. Components do not
invent unrelated loading, retry, cancellation, or progress flags. Mutations remain server-confirmed
unless they opt into the bounded `OptimisticMutation` contract.

Canceling a cancelable event stops only the documented local default. It does not undo a request
already accepted by the server or grant mutation authority.

## Form-associated controls

Controls use native inputs when they can satisfy the contract. A form-associated custom element:

- declares `static formAssociated = true` and uses `ElementInternals` where supported;
- supplies an equivalent native control/fallback in server HTML;
- synchronizes name/value, disabled, required, readonly, reset, and restore states;
- maps server field errors to visible text and programmatic descriptions;
- calls native validity/reporting APIs without suppressing server-returned errors;
- participates in ordinary navigation and HTMX submission with the same payload; and
- never stores or manufactures CSRF/authentication material.

Multiple-value controls specify their `FormData` encoding. File controls retain browser `File`
objects only for the active user gesture/session and apply existing upload limits.

## State classes and interaction ownership

Browser state is classified as:

| Class | Examples | Authority / persistence |
|---|---|---|
| Controlled | Canonical record value, selected server view | Server-owned; user interaction emits intent and waits for canonical response |
| Local | Open panel, measured width, adapter viewport | Disposable; initialize/recompute on connect |
| Draft | Unsubmitted edit, staged selection | User-local and bounded; explicit submit/discard/conflict and optional 0.40 transfer |
| Preference | Theme, density | Existing namespaced `BrowserStorage`; never secret/authoritative |
| Capability | CSRF, auth, signed URL, permissions | Never element-owned or persisted in public element state |

Every mutable field declares one mode plus reflection and incoming-update behavior. Dirty drafts use
replace, preserve, proven rebase, or explicit conflict handling; conflict is the default when a safe
merge is unavailable. Programmatic controlled updates do not emit user-intent events by default.

The phase 0.40 transfer protocol keys eligible draft state by component instance, schema version,
route/history identity, and bounded expiry. It requires explicit opt-in, clears on authorization or
identity changes, and cannot transfer capabilities or server authority. Full behavior lives in
[the interaction contracts](WEB_COMPONENT_INTERACTION_CONTRACTS.md#1-elementstateownership).

## Assets and loading

The renderer collects module asset IDs from elements present in the node tree. Page responses emit
deduplicated module references in dependency order. Fragment responses use the existing asset/head
policy; a required module already present is reused, and a newly required module is loaded through
the registered local manifest path.

Rich adapters, workers, WASM, CSS, fonts, and locale data are separate assets and load only when the
owning element is rendered. Module load failure times out to fallback and a diagnostic; it never
leaves content indefinitely hidden behind an upgrade marker.

Production rejects missing/mismatched manifest entries. Development may serve readable modules but
still runs registry conflict and ABI checks.

## Diagnostics and Explorer

The diagnostic family reserves `HED-ELEMENT-*` for definition, ABI, payload, lifecycle, ownership,
form, event, asset, and fallback failures. Records include safe tag/module/ABI/phase identifiers and
exclude user payloads.

Explorer shows definition metadata, SSR fallback, upgrade state, attributes/properties/events,
light/Shadow ownership, form behavior, tokens/parts/slots, assets, performance, accessibility,
lifecycle traces, controlled/local/draft ownership, `InteractionState`, optimistic reconciliation,
gesture/overlay catalog membership, and simulated failure/version-skew states. Mutation controls
remain subject to server authorization.

## Compatibility

The element ABI has an explicit supported range. Additive attributes/events may remain compatible;
changed semantics, event shapes, DOM ownership, form encoding, or fallback require an ABI transition.
Stable tag/event contracts begin only with the 0.41 inventory.

Servers and assets publish compatibility metadata in package manifests. Clean-install and mixed
version tests cover supported combinations. Unknown-new attributes are ignored only when the
declared ABI permits them; incompatible required features fail to fallback.

## Verification hooks

The implementation exposes test-only observation for active connection count, registered tags,
owned resources, emitted diagnostics, loaded assets, and lifecycle transitions. It does not expose
user payload contents. Browser leak tests compare listeners, workers, timers, observers, object URLs,
and retained element instances after repeated swap/disconnect cycles.

Exact evidence IDs and phase ownership are defined by
[the acceptance specification](../acceptance/WEB_COMPONENT_PLATFORM.md).
