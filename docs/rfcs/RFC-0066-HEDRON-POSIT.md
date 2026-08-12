# RFC-0066: `hedron-posit` unified Posit deployment adapter

**Status:** Draft

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

The phase first makes the current native Connect contract production-grade. An authenticated
request-cookie bridge is a separately enabled compatibility lane for Connect deployments that can
prove native application cookies are unavailable. The bridge does not turn Connect identity into
Hedron identity and never activates from product detection alone.

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
- `ConnectCookieMode`: `native`, `authenticated_header_v1`;
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

## Authenticated legacy cookie bridge v1

### Support boundary

`authenticated_header_v1` is off by default. It is Supported only for the documented reference
proxy topology and the exact Connect versions exercised by `BRIDGE-033`; every other topology is
Experimental. The 0.33 release cannot call the bridge Supported without a live licensed test that
first demonstrates the native-cookie failure and then passes the repaired end-to-end session flow.

Enabling the bridge requires all of the following at startup:

- explicit `ConnectCookieMode.AUTHENTICATED_HEADER_V1`;
- protected Connect runtime evidence;
- a bridge secret containing at least 32 random bytes;
- a non-empty, frozen allowlist of application-owned cookie names; and
- the matching base-header / `root_path` native Connect contract.

Missing or weak configuration fails startup. Request-time protocol violations fail the request and
never fall back to accepting the bridged cookies.

### Wire contract

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

### Reference topology and secret operations

The reference proxy must overwrite both bridge headers, be the only network path to Connect, use TLS
on untrusted hops, forward WebSocket upgrades, and prevent direct access around the proxy. The same
secret is supplied from the proxy secret store and Connect's masked runtime environment; it is never
checked into an app bundle or proxy template. Connect documents runtime environment values as
encrypted and masked, but operators remain responsible for access control and rotation.

Rotation uses an overlap window with `current` and `previous` secret references; new requests use
`current`, both may validate for at most 15 minutes, and `previous` is then removed. Status output
reports only key slots and rotation age. Operators must keep Connect proxy-header logging disabled
during normal operation and treat any diagnostic capture as sensitive.

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

1. **Contract probe:** capture sanitized real Connect scopes for the cut matrix; verify the
   2024.11 protocol floor, native request-cookie behavior, base header, root path, response cookies,
   redirects, and WebSockets; accept RFC-0066 only after the bridge need is reproduced.
2. **Package extraction:** create `hedron-posit`, move Hedron-specific deployment code, establish the
   one-way dependency graph, and make all inactive/Workbench/compatibility tests pass without new
   Connect behavior.
3. **Native Connect:** add product resolution, typed configuration/status, native URL/mount/cookie
   behavior, CLI diagnostics, live native matrix, and performance measurements.
4. **Bridge v1:** implement the frozen cookie registry and bounded authenticated carrier; publish and
   adversarially test the reference proxy, bypass prevention, rotation, logging, and rollback.
5. **Release closure:** finish clean-package/offline installs, upgrade/rollback, docs, independent
   security review, SBOM/provenance, full regressions, and the 0.33 release rehearsal.

The detailed work breakdown, file ownership, and stop/go conditions are in
[HEDRON_POSIT_033](../implementation/HEDRON_POSIT_033.md).

## Performance and accessibility

The adapter adds no visual UI. Existing Hedron error semantics and accessibility contracts apply.
The package must add no middleware in `inactive` mode beyond a single cheap product-resolution
branch, no second normalizer in Workbench or Connect, and no bridge decode or cookie parsing in
native mode.

`PERF-033` records p50/p95 request overhead and allocations for inactive, Workbench, native Connect,
and bridge modes under one and multiple workers. Budgets are fixed in the acceptance packet before
implementation measurements are used for optimization.

## Non-goals

- Posit Connect publishing, bundle construction, server administration, license management, or
  proxy installation automation.
- A second generic path normalizer, a renamed `fastapi-workbench`, or a plain FastAPI
  `FastAPIPosit` facade.
- Treating Connect login, `RStudio-Connect-Credentials`, or
  `Posit-Connect-User-Session-Token` as Hedron authentication or authorization.
- Restoring Connect platform or arbitrary third-party cookies from the legacy carrier.
- Auto-enabling the bridge, trusting caller forwarding headers, or supporting an untested proxy
  topology.
- Immediate deprecation or removal of `hedron-workbench`.

## Acceptance criteria

- RFC-0066 is Accepted only after the contract probe records the exact Connect cut matrix and either
  reproduces the legacy cookie failure or removes bridge support from the RFC.
- Package/import/API/CLI/extras/stability metadata and the one-way dependency graph agree.
- Inactive parity passes against `Hedron`; Workbench and compatibility parity pass against the 0.32
  `HedronWorkbench` contract.
- Native Connect passes the declared live and simulated matrix for URLs, mounts, HTTP/WebSocket,
  assets, redirects, sessions, CSRF, response/request cookies, scaling, failure, and rollback.
- Bridge v1 passes live repaired-session evidence plus spoof, bypass, weak/missing secret,
  duplicate, conflict, oversize, malformed, late registration, rotation, log, and redaction tests.
- Independent review has no unresolved critical/high finding; fixed performance budgets pass.
- Local, Workbench, native Connect, and reference-bridge operations include copyable setup, health,
  security, rollback, and troubleshooting instructions.
- Every 0.33-owned row in `release-gate-0.33.toml` is Verified with zero Deferred at cut.
