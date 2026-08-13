# RFC-0066: `hedron-posit` unified Posit deployment adapter

**Status:** Accepted

**Accepted:** 2026-08-13 (Stage 0 licensed Connect probe;
[`realconnect-033`](../acceptance/realconnect-033/RESULT.log);
`BRIDGE_DECISION=drop_supported`)

**Target phase:** 0.33

**Stability:** proposed `beta` package and public API

**Related:** [RFC-0062](RFC-0062-POSIT-WORKBENCH-ADAPTER.md),
[RFC-0063](RFC-0063-FASTAPI-WORKBENCH-EXTRACTION.md), D-057, D-058, D-061; tracking
[#167](https://github.com/eddiethedean/hedron/issues/167)

**Implementation plan:** [HEDRON_POSIT_033](../implementation/HEDRON_POSIT_033.md)

**Acceptance packet:** [RELEASE_0_33](../acceptance/RELEASE_0_33.md)

## Summary

Add a `hedron-posit` distribution with a `hedron_posit` import package and one application facade:

```python
from hedron_posit import HedronPosit

app = HedronPosit()
```

The same application object runs as ordinary Hedron, in Posit Workbench, and on Posit Connect. The
package owns Posit product resolution and Hedron-specific integration while delegating generic
Workbench discovery, mounting, path normalization, and launch behavior to `fastapi-workbench`.

The phase makes the current native Connect contract production-grade. Stage 0 licensed evidence on
Connect **2026.07.0** shows application-owned request cookies (`session`, `hedron_csrf`) round-trip
to Python content, so **`authenticated_header_v1` is not a Supported 0.33 surface**. The wire
contract below remains a documented extension point for a future phase if loss is reproduced on a
named topology; 0.33 does not ship a Supported bridge implementation.

## Why this phase exists

`hedron-workbench` proved the deployment facade and `fastapi-workbench` extracted the generic ASGI
normalizer and launcher. The Workbench-specific public name now hides already implemented Connect
behavior, and operators do not have one diagnostic or compatibility matrix spanning local,
Workbench, and Connect deployments.

The change is primarily a package-boundary and deployment-contract change, not a new router or
hosting runtime. Applications should move between the three environments without branching their
application construction or weakening Hedron's mount, URL, cookie, session, and CSRF contracts.

## Platform facts and compatibility floor

This RFC relies on the following published Posit contracts:

- Connect sets non-customizable `POSIT_PRODUCT=CONNECT`; `RSTUDIO_PRODUCT=CONNECT` is the deprecated
  compatibility marker. `CONNECT_SERVER` is not trusted product evidence because content owners can
  override it. See the [Connect environment-variable contract](https://docs.posit.co/connect/user/content-settings/#environment-variables).
- Connect documents `RStudio-Connect-App-Base-URL` as the runtime base for FastAPI content. Hedron
  accepts it only when it is singular and its path agrees exactly with ASGI `root_path`. See the
  [Connect FastAPI guide](https://docs.posit.co/connect/user/fastapi/).
- Connect 2024.11.0 fixed FastAPI request scopes so they reflect the mounted content URL and added
  lifespan support. This is the protocol floor for native mode. At release cut, the Supported floor
  is the newer of 2024.11.0 and the oldest Connect release still in Posit's support window. See the
  [Connect release notes](https://docs.posit.co/connect/news/#2024110).
- Posit user-session and credentials headers are platform inputs, not proof of a Hedron principal.
  `hedron-posit` passes them through to application code but never consumes, logs, or maps them to
  Hedron authentication.

The cut matrix contains the exact minimum Supported Connect release, the current stable release,
on-host execution, off-host execution where licensed, GUID and vanity mounts, public and private
content, HTTP, and WebSocket traffic. A simulated fixture cannot replace at least one licensed live
native-Connect run.

**Stage 0 result (2026-08-13):** licensed on-host Connect **2026.07.0**
(`posit/connect@sha256:ae5753745ddc576cca06ad7466a370e18bc54580b154f4b5bcbef9390f1c54a9`)
passed GUID mount product/base/`root_path`, HTTP/HTMX/CSRF/session, assets, OpenAPI, redirect,
WebSocket, and **native request-cookie** echo (`NATIVE_COOKIES=ok`). Off-host Kubernetes was not
exercised and remains **Experimental**. Vanity-URL expansion beyond synthetic fixtures remains
Experimental until live vanity evidence is attached at `CONNECT-033`. See
[RELEASE_0_33 Exact cut matrix](../acceptance/RELEASE_0_33.md#exact-cut-matrix).

## Locked package architecture

The dependency graph is one-way:

```text
hedron-workbench -> hedron-posit -> hedron
                                -> fastapi-workbench
```

More precisely:

- `hedron-posit` depends on the coordinated `hedron` train and `fastapi-workbench>=1,<2`.
- `hedron-posit` must not import `hedron-workbench`.
- `hedron-workbench` depends on the same-train `hedron-posit` and contains only compatibility
  adapters, re-exports, CLI branding, and migration documentation.
- `fastapi-workbench` remains framework-neutral and does not acquire Connect- or Hedron-specific
  policy.

The Hedron-specific implementation currently under `hedron_workbench` moves without semantic
change before Connect features are added. Existing Workbench parity must be green at that commit so
package movement and behavioral changes are independently reviewable.

## Public API

The new supported surface is deliberately small:

```python
from hedron_posit import (
    ConnectConfig,
    ConnectCookieMode,
    HedronPosit,
    PositConfig,
    PositProduct,
)

app = HedronPosit(
    title="My app",
    session_secret="replace-me",
    posit=PositConfig(
        product=PositProduct.AUTO,
        connect=ConnectConfig(cookie_mode=ConnectCookieMode.NATIVE),
    ),
)
```

Public records and enums:

- `PositProduct`: `auto`, `inactive`, `workbench`, `connect`;
- `ConnectCookieMode`: `native` (Supported); `authenticated_header_v1` remains an
  **Experimental extension-point enum value only** in 0.33 — constructors that select it must fail
  closed / refuse startup until a future Accepted decision ships Supported bridge evidence;
- frozen `PositConfig` containing product selection, a `WorkbenchConfig`, and a `ConnectConfig`;
- frozen `ConnectConfig` containing cookie mode, explicitly trusted proxy peers, and custom
  application-cookie names;
- frozen `ResolvedPositDeployment` and `PositStatus` records with secret-free `as_dict()` output;
- `HedronPosit`, `posit_status()`, and `deployment_capabilities()`; and
- `hedron-posit run`, `check`, and `doctor` commands.

The constructor retains ordinary `Hedron` keyword arguments. Posit-specific options live under the
single `posit=` object; the new facade does not add a second set of flat mount, host, worker, or
cookie arguments. Workbench configuration continues to use the existing `WorkbenchConfig` type.

`hedron-posit run APP` performs Workbench discovery before application import when Workbench
evidence exists. Otherwise it delegates to the ordinary Hedron/Uvicorn launch path. Connect imports
the application through its platform entry point; the CLI does not publish or administer content.

## Product resolution and trust

Resolution is pure, deterministic, and records its evidence:

1. An explicit `PositConfig.product` other than `auto` selects behavior for tests and unusual
   deployments but does not, by itself, make request headers trusted.
2. `POSIT_PRODUCT=CONNECT` selects Connect. Deprecated `RSTUDIO_PRODUCT=CONNECT` is accepted with a
   diagnostic only when `POSIT_PRODUCT` is absent.
3. Existing launcher handoff or Workbench discovery evidence selects Workbench.
4. No evidence resolves to `inactive` and must be behaviorally equivalent to ordinary `Hedron`.

Conflicting explicit, Connect, and Workbench evidence is a startup error; the resolver never guesses
an order. Broad variables such as `CONNECT_SERVER`, `HOST`, `PORT`, or an uncorroborated forwarded
header do not select a product or grant trust.

Primary environment keys are `HEDRON_POSIT_PRODUCT`,
`HEDRON_POSIT_CONNECT_COOKIE_MODE`, and `HEDRON_POSIT_BRIDGE_SECRET`. Existing
`FASTAPI_WORKBENCH_*` and `HEDRON_WORKBENCH_*` keys remain Workbench inputs. Security-boundary
choices, including bridge enablement and trusted peers, never auto-detect.

## Workbench mode

Workbench mode delegates to the existing `fastapi-workbench` resolver, middleware, and launcher and
retains:

- launch-time session URL discovery before application import;
- exactly one HTTP/WebSocket scope normalizer;
- correct `root_path`, browser mount, redirect, asset, OpenAPI, cookie, session, and CSRF behavior;
- rejection of ephemeral Workbench session URLs for durable callbacks; and
- local no-op behavior when Workbench is inactive.

The extraction is complete only when the existing Workbench resolver, path, runner, URL, security,
integration, Docker, and upgrade corpora pass through both `HedronPosit` and the compatibility
package.

## Native Connect mode

Native mode is the default Connect lane. It requires:

- protected Connect runtime evidence (`POSIT_PRODUCT=CONNECT`, or the deprecated protected marker
  only for the declared compatibility lane);
- exactly one `RStudio-Connect-App-Base-URL` header;
- a normalized base-header path exactly equal to non-empty ASGI `root_path`; and
- the existing Hedron mount and response-cookie repair path to run exactly once.

It uses neither `Host` nor `CONNECT_SERVER` as an implicit public origin. It does not modify request
cookies. Connect is expected to deliver application-owned request cookies natively. A bounded
diagnostic may report a probable cookie loop after an owned session cookie was set but was absent on
subsequent same-client requests; it must not record cookie values, session identifiers, CSRF
material, or user metadata.

The live matrix covers login/logout/session continuity, CSRF, redirects, assets, OpenAPI, HTMX,
WebSockets, workers, scaling/restart, GUID and vanity mounts, and rolling back to ordinary
`Hedron`/`hedron-workbench`.

## Authenticated legacy cookie bridge v1 (extension point; not Supported in 0.33)

### Support boundary

Stage 0 recorded `BRIDGE_DECISION=drop_supported`: on Connect 2026.07.0 with the licensed on-host
GUID topology, application-owned request cookies round-trip to Python content. Therefore
**0.33 does not ship a Supported `authenticated_header_v1` implementation**, does not require a
reference proxy topology, and treats `BRIDGE-033` as proof of that negative claim (inventory
excludes Supported bridge; extension-point docs only).

The historical wire contract below is retained so a future phase can Accept Supported bridge
behavior only after reproducing native request-cookie loss on a named topology. Enabling the
bridge must never activate from product detection alone and must never map Connect identity into
Hedron identity.

### Reserved wire contract (future; not implemented as Supported in 0.33)

If a later Accepted decision restores Supported bridge scope, enabling it would require all of:

- explicit `ConnectCookieMode.AUTHENTICATED_HEADER_V1`;
- protected Connect runtime evidence;
- a bridge secret containing at least 32 random bytes;
- a non-empty, frozen allowlist of application-owned cookie names; and
- the matching base-header / `root_path` native Connect contract.

Missing or weak configuration fails startup. Request-time protocol violations fail the request and
never fall back to accepting the bridged cookies.

The v1 wire names are fixed:

- `X-Hedron-Posit-Bridge-Auth: v1 <base64url-secret>`
- `X-Hedron-Posit-Bridge-Cookie: v1 <base64url-raw-cookie-header>`

Exactly one value for each header is required. The authentication value is compared with
`secrets.compare_digest`. The cookie envelope uses unpadded base64url so cookie delimiters and
control characters cannot alter the carrier header.

Decoded input is limited to 16 KiB, 128 cookie pairs, 128 bytes per name, 4096 bytes per value, and
32 registered custom names. Cookie names must use the HTTP token grammar. Malformed base64,
controls, invalid names, overflow, or duplicate bridge headers reject the request before parsing
application state.

Hedron session, CSRF, and color-mode names register automatically. Plugins and applications may
register custom owned names only before lifespan startup freezes the registry. From the bridge
payload, all Connect platform and unregistered cookies are discarded. An owned value already
present in the native `Cookie` header may be merged only when byte-identical; conflicts reject the
request. The adapter emits one canonical downstream `Cookie` header and removes both bridge headers
before calling application middleware.

A future reference proxy would overwrite both bridge headers, be the only network path to Connect,
use TLS on untrusted hops, forward WebSocket upgrades, and prevent direct access around the proxy.
Rotation would use an overlap window with `current` and `previous` secret references (at most 15
minutes). Operators must keep Connect proxy-header logging disabled during normal operation.

## Compatibility contract

`HedronWorkbench` remains a real class in `hedron_workbench`, implemented as a thin subclass of
`HedronPosit` that translates the existing constructor keywords into `PositConfig`. This preserves a
distinct class name, `issubclass(HedronWorkbench, HedronPosit)`, existing markers, and old
Workbenches and Connect behavior without alias ambiguity.

The following remain supported through at least phase 0.35:

- `from hedron_workbench import HedronWorkbench` and documented public re-exports;
- `hedron-workbench run/check/doctor`;
- `hedron[workbench]` and direct `hedron-workbench` installation; and
- existing `HEDRON_WORKBENCH_*` configuration.

Phase 0.33 emits no runtime deprecation warning. Documentation may call `hedron-posit` preferred.
Removal or deprecation after 0.35 requires a separate Accepted decision, migration evidence, and a
release boundary that permits the change. The old package never imports back from a private
`hedron-posit` module and no dependency cycle is permitted.

## Diagnostics and error taxonomy

`posit_status()` returns `PositStatus`, not an untyped bag. It contains only product, evidence kind,
mount source, normalized mount, cookie strategy, bridge enabled/disabled, registered-cookie count,
normalizer count, compatibility facade state, and capability booleans.

Stable diagnostic families:

| Range | Meaning |
|---|---|
| `HED-POSIT-01xx` | product resolution and conflicting evidence |
| `HED-POSIT-02xx` | Workbench handoff and compatibility facade |
| `HED-POSIT-03xx` | Connect base path, scope, URL, and native cookie loop |
| `HED-POSIT-04xx` | bridge startup, authentication, bounds, parsing, and conflicts |
| `HED-POSIT-05xx` | CLI, doctor, and deployment operations |

Secrets, bridge headers, cookies, credentials/user-session headers, content GUIDs, session IDs,
CSRF values, and token-shaped path/query values are redacted in exceptions, text/JSON diagnostics,
logs, metrics, and evidence artifacts.

## Delivery sequence

Implementation follows five reviewable stages. A later stage may not compensate for failed earlier
parity.

1. **Contract probe (complete):** capture sanitized real Connect scopes for the cut matrix; verify the
   2024.11 protocol floor, native request-cookie behavior, base header, root path, response cookies,
   redirects, and WebSockets; Accept RFC-0066 after bridge keep/drop from live evidence
   (`BRIDGE_DECISION=drop_supported` on 2026.07.0).
2. **Package extraction:** create `hedron-posit`, move Hedron-specific deployment code, establish the
   one-way dependency graph, and make all inactive/Workbench/compatibility tests pass without new
   Connect behavior.
3. **Native Connect:** add product resolution, typed configuration/status, native URL/mount/cookie
   behavior, CLI diagnostics, live native matrix, and performance measurements.
4. **Bridge v1:** **skipped for Supported 0.33 scope** per Stage 0; retain extension-point docs only.
   Do not implement Supported bridge middleware in this phase.
5. **Release closure:** finish clean-package/offline installs, upgrade/rollback, docs, independent
   security review, SBOM/provenance, full regressions, and the 0.33 release rehearsal.

The detailed work breakdown, file ownership, and stop/go conditions are in
[HEDRON_POSIT_033](../implementation/HEDRON_POSIT_033.md).

## Performance and accessibility

The adapter adds no visual UI. Existing Hedron error semantics and accessibility contracts apply.
The package must add no middleware in `inactive` mode beyond a single cheap product-resolution
branch, no second normalizer in Workbench or Connect, and no bridge decode or cookie parsing in
native mode.

`PERF-033` records p50/p95 request overhead and allocations for inactive, Workbench, and native
Connect under one and multiple workers. Bridge-mode budgets apply only if a future phase restores
Supported bridge scope. Budgets are fixed in the acceptance packet before implementation
measurements are used for optimization.

## Non-goals

- Posit Connect publishing, bundle construction, server administration, license management, or
  proxy installation automation.
- A second generic path normalizer, a renamed `fastapi-workbench`, or a plain FastAPI
  `FastAPIPosit` facade.
- Treating Connect login, `RStudio-Connect-Credentials`, or
  `Posit-Connect-User-Session-Token` as Hedron authentication or authorization.
- Shipping Supported `authenticated_header_v1` in 0.33 after Stage 0 drop.
- Restoring Connect platform or arbitrary third-party cookies from a legacy carrier.
- Auto-enabling any bridge, trusting caller forwarding headers, or supporting an untested proxy
  topology.
- Immediate deprecation or removal of `hedron-workbench`.

## Acceptance criteria

- RFC-0066 is Accepted after the contract probe records the exact Connect cut matrix and either
  reproduces the legacy cookie failure or removes Supported bridge from the RFC (**done:** removed).
- Package/import/API/CLI/extras/stability metadata and the one-way dependency graph agree.
- Inactive parity passes against `Hedron`; Workbench and compatibility parity pass against the 0.32
  `HedronWorkbench` contract.
- Native Connect passes the declared live and simulated matrix for URLs, mounts, HTTP/WebSocket,
  assets, redirects, sessions, CSRF, response/request cookies, scaling, failure, and rollback.
- `BRIDGE-033` Verifies the Stage 0 drop (no Supported bridge implementation; inventory/extension-point
  agreement) rather than a live repaired-proxy suite.
- Independent review has no unresolved critical/high finding; fixed performance budgets pass.
- Local, Workbench, and native Connect operations include copyable setup, health, security,
  rollback, and troubleshooting instructions (bridge recipes only as Experimental extension-point
  notes).
- Every 0.33-owned row in `release-gate-0.33.toml` is Verified with zero Deferred at cut.
