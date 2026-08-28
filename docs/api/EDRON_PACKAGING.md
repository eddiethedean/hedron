---
status: verified
---

# Edron packaging contract

**Status:** Published and stable in Edron `1.0.0`<br>
**Target:** Edron `1.0.x`; Hedron `>=1.0.0,<1.1`<br>
**Historical 0.1 target metadata:** Edron `0.1.0`; compatible Hedron train and release phase unassigned<br>
**Roadmap:** [Edron `0.x` release roadmap](../EDRON_ROADMAP.md)<br>
**Public API:** [Edron 0.1 public API](EDRON.md)<br>
**State and interaction:** [Edron 0.1 state and interaction](EDRON_STATE_INTERACTION.md)<br>
**Capability inventories:** [Edron 0.1 capability inventories](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_CAPABILITY_INVENTORIES.md)<br>
**Implementation:** [Edron 0.1 implementation specification](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_001.md)<br>
**Acceptance:** [Edron 0.1 acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_001.md)<br>
**Architecture:** [RFC-0094](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md)<br>
**Fixtures:** [Edron golden applications](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_GOLDEN_APPS.md)

This document began as the 0.1 packaging design and now defines what installing Edron installs
through 1.0, how Edron composes separately owned Hedron
packages, how optional third-party capabilities activate, and what artifacts and evidence are
required for release. It complements the Python and interaction contracts. Python packaging
metadata remains the installation authority; native Hedron packages remain the implementation,
plugin, component, asset, and runtime authorities for their features.

## Installation promise

The beginner path is one ordinary command:

```console
pip install "edron>=1.0.0,<1.1"
```

That command must be sufficient to import Edron, run the development server, and use every
first-party feature exercised by the base golden applications, including semantic tables/data
views, first-party charts, first-party maps, safe Markdown, and HTMX interactions. It also installs
the Supported native `hedron-data` editing APIs for direct composition, although a simplified
Edron-owned editor method is deferred from the 0.1 public surface. A user must not need to discover
and install another `hedron-*` distribution for those documented base/native features.

Third-party integrations remain direct optional dependencies. Either command below activates the
same Plotly adapter:

```console
pip install "plotly>=5.18,<7"
pip install "edron[plotly]>=1.0.0,<1.1"
```

The second command is only an installation shortcut. Edron does not require, record, or inspect
which spelling was used.

## Normative principles

1. **One command, separately owned distributions.** The base installation aggregates compatible
   Hedron wheels through dependency metadata; Edron does not copy their source or assets into its
   wheel.
2. **The base is useful without extras.** Tables, first-party charts, maps, Markdown, the server,
   and the documented core interface cannot be extra-gated.
3. **An installed compatible dependency is the capability.** An extra name is never a runtime
   feature flag, entitlement, import namespace, or alternate adapter path.
4. **Direct installation is first-class.** Installing the documented third-party requirements
   directly must activate exactly the same adapter as the matching shortcut.
5. **No runtime environment mutation.** Edron never runs an installer, invokes a package manager,
   modifies environment metadata, or contacts a package index.
6. **Native ownership remains visible.** Objects, entry points, assets, diagnostics, maturity, and
   limitations retain their owning Hedron package identity.
7. **One compatibility source.** Package metadata, runtime detection, diagnostics, documentation,
   and release tests must be generated from or checked against one accepted requirement manifest.
8. **Imports are bounded and inert.** `import edron` does not import optional ecosystems, discover
   arbitrary plugins, start services, register a global app, or perform network/file I/O.
9. **Failures are precise.** Missing, incompatible, and broken optional capabilities are distinct
   and preserve exact actionable remediation without misreporting internal import failures.
10. **Published artifacts are the product.** Acceptance runs against built wheel and source
    distribution installations, not only an editable monorepo where undeclared packages can leak
    onto `sys.path`.

## Terms

| Term | Meaning |
|---|---|
| Distribution | An installable package-metadata unit such as `edron`, `hedron-data`, or `plotly` |
| Import package | A Python namespace such as `edron`, `hedron_data`, or `plotly` |
| Base battery | A documented Edron feature guaranteed after plain `pip install edron` |
| Capability | A named optional Edron behavior backed by one native adapter and a declared dependency set |
| Adapter | The implementation owned by a Hedron package that converts a supported third-party value |
| Shortcut extra | A PEP 621 optional-dependency key whose only behavior is installing a capability's requirements |
| Required train | The bounded set of mutually compatible Edron and Hedron distribution versions |
| Broken capability | Compatible distribution metadata is present, but import or adapter initialization fails |

Distribution names and import names are not assumed to be equal. Detection uses canonical
distribution metadata; loading uses a hard-coded adapter/import plan. Request data never chooses a
distribution, module, entry point, or import string.

## Artifact and namespace contract

The project publishes one top-level distribution named `edron` and one beginner import package:

```python
import edron as ed
```

The published distribution contains:

- the `edron` Python package;
- the `py.typed` marker and complete typing metadata;
- Edron-owned static/templates/schema data that is explicitly listed as package data;
- its README, license, changelog, and package metadata in the source distribution; and
- the `edron` console script defined by the public CLI contract.

The Edron wheel does not contain copied `hedron`, `hedron_core`, `hedron_data`, `hedron_charts`,
`hedron_maps`, or third-party source trees. It does not claim their modules, entry points,
distribution names, licenses, changelogs, or asset paths. Those distributions are installed by the
resolver and remain directly importable by advanced users.

The initial Edron wheel is pure Python and must be publishable as a universal Python wheel for the
supported Python range. A compiled optional dependency does not change the Edron wheel's platform
tag. If a future Edron-owned compiled extension is proposed, that is a separate packaging design
change with a platform, fallback, build, and support matrix.

## Dependency direction and authority

The dependency graph is one-way:

```text
application
    -> edron
        -> hedron
        -> hedron-data
        -> hedron-charts
        -> hedron-maps
        -> Markdown/sanitization dependencies
        -> development server dependencies
            -> hedron-core through owning Hedron packages

application (optional)
    -> third-party distribution
        <- native adapter owned by a Hedron package
```

The following are forbidden:

- a Hedron package depending on `edron`;
- a dependency cycle between Edron and a native package;
- copying a Hedron implementation into Edron to avoid declaring a dependency;
- Edron monkey-patching a native package during import;
- an Edron-only component, plugin, asset, or interaction registry that competes with Hedron; and
- using Edron packaging metadata as runtime authorization or feature entitlement.

An Edron convenience may select/configure a native object, but its runtime explanation must retain
the native owner and identity. Installing Edron must not alter behavior of an application that only
imports Hedron.

## Base installation contents

The base `Requires-Dist` set contains compatible ranges for these responsibilities:

| Required distribution/responsibility | Beginner-facing guarantee | Ownership |
|---|---|---|
| `hedron` | ASGI/FastAPI host, semantic components, forms, fragments, actions, HTMX, styling, assets, security | Hedron |
| `hedron-data` | semantic static/data tables through Edron plus the Supported native data-editing subset for direct composition | `hedron-data` |
| `hedron-charts` | dependency-light first-party chart components and native chart asset lifecycle | `hedron-charts` |
| `hedron-maps` | first-party map components and declared local/remote data-source behavior | `hedron-maps` |
| Markdown parser + sanitizer | `self.markdown(...)` with the accepted safe policy | selected maintained dependencies + Hedron policy |
| Development server | `edron run` including the documented reload behavior | selected maintained server dependencies |

`hedron-core` may arrive transitively through `hedron` and package requirements; Edron does not
need a redundant direct requirement unless it imports a public `hedron-core` symbol directly or the
release resolver needs the constraint to prevent an invalid train. The accepted release manifest
records that decision explicitly.

The base install is intentionally not every `hedron-*` package. Explorer, notebook, MCP, framework
bridges, workbench, simulation, conformance tooling, experimental UI, browser-test tooling, worker
backends, database drivers, and third-party plotting/dataframe ecosystems are excluded unless a
future public Edron feature makes one a deliberate base battery. “Batteries included” means the
curated beginner surface works, not that the whole Hedron repository is installed.

### Base behavior cannot be secretly optional

A base method may not catch a missing required Hedron package and present an optional-capability
message. A missing or incompatible required distribution means the Edron installation is broken.
`edron doctor`, application construction, and release smoke tests report it as a required-train
failure with the resolver/upgrade command for the complete environment.

Plain `import edron` should remain useful to packaging tools even though a corrupt environment can
still fail normal required imports. The implementation must not hide a required-package failure by
shipping a degraded private replacement.

## Required version train

Edron supports the same Python range as its compatible Hedron train. The first release targets
Python 3.10 through 3.14 unless the accepted upstream packet changes the complete train
consistently.

Before RFC acceptance, the packaging packet freezes:

- Edron's `requires-python` value;
- lower and exclusive upper bounds for every required direct distribution;
- the compatible `hedron-core` schema/ABI range, including transitive resolution;
- platform/environment markers;
- minimum server, Markdown, and sanitizer versions;
- every public extra's complete requirement closure; and
- a resolver lock/constraints snapshot used by CI for each supported Python/platform lane.

Edron is a library and does not exact-pin all transitive dependencies in published metadata.
Published ranges are bounded tightly enough to reject unverified native trains, while applications
use a lockfile/constraints file for reproducible deployment.

### Single-source requirement manifest

The project maintains one machine-readable accepted manifest containing at least:

| Field | Purpose |
|---|---|
| Distribution/canonical name | Metadata lookup and resolver requirement |
| Accepted specifier and marker | Build metadata and compatibility decision |
| Required versus optional | Base-train or capability behavior |
| Capability/adapter ID | Stable diagnostic and native adapter lookup |
| Owning package and native maturity | Provenance and support claim |
| Import probe | Hard-coded bounded import/initialization check |
| Direct and shortcut install templates | Exact remediation |
| Assets/platform limitations | Honest availability and deployment report |

The implementation representation is private. CI compares the manifest with built `METADATA`,
the owning adapter ranges, generated documentation, capability diagnostics, and extras. A mismatch
blocks publication; hand-maintained divergent copies are not accepted.

## Optional capability registry

Optional Edron methods remain importable and type-checkable without their third-party distribution.
The method resolves its named capability only when registration/use requires the adapter. Root
import does not import optional libraries merely to populate a registry.

The initial curated shortcut registry is:

| Capability ID | Direct requirements | Shortcut | Native owner/maturity |
|---|---|---|---|
| `data.pandas` | `pandas>=2.0`, `narwhals>=1.1` | `edron[pandas]` | `hedron-data`, beta |
| `data.polars` | `polars>=1.0`, `narwhals>=1.1` | `edron[polars]` | `hedron-data`, beta |
| `data.pyarrow` | `pyarrow>=15.0`, `narwhals>=1.1` | `edron[pyarrow]` | `hedron-data`, beta |
| `chart.plotly` | `plotly>=5.18,<7` | `edron[plotly]` | `hedron-charts`, experimental |
| `chart.altair` | `altair>=6,<7`, `vl-convert-python>=1.0` | `edron[altair]` | `hedron-charts`, experimental |
| `chart.matplotlib` | `matplotlib>=3.8,<4` | `edron[matplotlib]` | `hedron-charts`, beta/static Supported scope |
| `data.sqlalchemy` | `sqlalchemy>=2,<3` | `edron[sqlalchemy]` | `hedron-data`, beta |

These are release candidates until the accepted packet verifies the owning packages' exact ranges.
The Edron range cannot be broader than the native adapter's tested range or narrower without a
documented Edron-specific reason and acceptance evidence.

### Capability resolution algorithm

For a declared capability, Edron performs these bounded steps:

1. Look up each hard-coded canonical distribution name through installed distribution metadata.
2. If required metadata is absent, classify the capability as `missing`; do not attempt its import.
3. Compare every discovered version with the accepted specifier and environment marker.
4. If a version is outside the range, classify it as `incompatible`; do not initialize the adapter.
5. Import the owning native adapter and declared third-party module using the fixed plan.
6. If compatible metadata exists but import/initialization fails, classify it as `broken` and
   preserve the safe causal chain.
7. Resolve the public native adapter through Hedron's catalog/registration authority.
8. Cache only bounded environment/capability facts appropriate to an immutable process
   environment; never cache request values or hide a prior broken cause.

Broadly catching `ImportError` around an adapter import and reporting “not installed” is forbidden:
an internal missing subdependency, binary-loader failure, or import-time exception is `broken`, not
`missing`.

Installing or upgrading packages underneath a running process is unsupported. Remediation tells the
user to update the environment and restart the process; Edron does not attempt hot rediscovery as a
substitute for reproducible process startup.

### Explicit backend selection

When the author explicitly chooses `backend="plotly"`, missing/incompatible/broken Plotly fails
with that capability diagnostic. Edron must not silently render a first-party, Matplotlib, Altair,
or other chart instead. When no third-party backend is requested, Edron's documented first-party
chart is the base behavior and requires no optional plotting library.

## Extras are installer shortcuts

Published Edron extras use standard PEP 621 optional dependencies. For a capability shortcut:

```toml
[project.optional-dependencies]
plotly = ["plotly>=5.18,<7"]
```

The implementation may delegate to an owning stable extra such as
`hedron-charts[plotly]` only when the resolved dependency closure, version range, markers, and
adapter behavior are proven equivalent. The user-facing missing-capability diagnostic still lists
the direct third-party requirements so the shortcut is never mandatory.

The following invariants apply:

- installing the direct requirements after/beside `edron` activates the capability;
- installing the shortcut activates the same capability and code path;
- an extra does not set an environment variable, write a marker file, install an Edron plugin, or
  expose a different import;
- runtime code does not ask whether an extra was requested;
- shortcut requirements include every necessary dependency and no unrelated capability bundle;
- requirement markers and bounds match the accepted capability manifest;
- empty/deprecated stub extras are not introduced in Edron 0.1;
- no `edron[all]` or equivalent unbounded aggregate is published; and
- documentation recommends explicit application dependencies/lockfiles for production.

Edron's own test, docs, lint, and release tools use repository dependency groups, not public extras
that users could mistake for runtime capabilities.

Adding a shortcut is a packaging convenience. It does not promote an Experimental native adapter
to Beta/Supported. Removing a shortcut does not disable direct compatible installation; shortcut
removal requires the compatibility process described below.

## Capability diagnostics

The public exception shapes are defined in the public API contract. Packaging freezes their
behavior:

| State | Detection | Exception | Required remediation |
|---|---|---|---|
| Missing | Distribution metadata absent | `MissingCapabilityError` | Exact direct and shortcut install commands |
| Incompatible | Installed version outside accepted range | `IncompatibleCapabilityError` | Discovered versions, accepted range, and safe upgrade/downgrade commands |
| Broken | Compatible metadata present but import/adapter init failed | `BrokenCapabilityError` | Capability/owner plus preserved cause and troubleshooting reference |
| Available | Metadata, version, import, and native adapter resolution succeed | No error | Native adapter executes with its own maturity/limitations |

A missing Plotly development diagnostic is conceptually:

```text
EDR-CAP-0001: Plotly support is not installed
Capability: chart.plotly
Required: plotly>=5.18,<7
Direct:   pip install "plotly>=5.18,<7"
Shortcut: pip install "edron[plotly]>=1.0.0,<1.1"
uv:       uv add "plotly>=5.18,<7"
Shortcut: uv add "edron[plotly]>=1.0.0,<1.1"
Restart the Edron process after changing the environment.
```

Commands are inert diagnostic text, never shell-executed. They use quoted exact compatible
requirements and normalized distribution/extra names. Multi-distribution capabilities list one
copy-paste-safe direct command containing the complete set.

Diagnostics include capability ID, adapter/native owner, accepted ranges, installed versions when
known, Edron call site when known, maturity/limitations, and an offline documentation anchor. A
`BrokenCapabilityError` preserves `__cause__` for trusted development tooling but redacts secrets,
absolute private paths, environment contents, and unrestricted exception representations from
production HTTP output.

Install commands appear in CLI/development/authorized diagnostics. A public production error page
uses the stable capability code and operator-facing reference without telling an untrusted remote
user how the server environment is assembled.

## Import and initialization behavior

`import edron` must not:

- import pandas, Polars, PyArrow, Plotly, Altair, Matplotlib, SQLAlchemy, or another optional
  ecosystem;
- enumerate arbitrary third-party entry points;
- instantiate `App`, page classes, native plugins, server objects, or dependency providers;
- scan application modules/files;
- start a server, thread, worker, event loop, or file watcher;
- open sockets/files, read user configuration, contact a CDN/index, or fetch an asset;
- mutate global Hedron registries or logging configuration; or
- emit stdout/stderr output in a valid environment.

Import may define Edron descriptors and identity re-exports and import the minimum required native
modules needed for those promises. First-party data/chart/map implementations and their assets
should remain lazy until application registration or use where native contracts allow it; base
availability must not require eagerly importing every package subtree.

Native plugin/feature registration occurs through the owning Hedron APIs while constructing or
sealing an explicit application. Edron may request deterministic inclusion of its required native
features, but it does not perform process-global import-time registration or invent another plugin
catalog. Arbitrary installed Hedron plugins remain governed by Hedron's own discovery/allowlist
policy, not silently enabled because Edron is installed.

## Native package and object interoperability

Packaging aggregation must preserve normal native use:

```python
import edron as ed
from hedron_charts import LineChart
from hedron_data import DataTable


class Dashboard(ed.Page):
    def render(self) -> None:
        self.include(LineChart(data=[1, 3, 2]))
        self.include(DataTable(rows=[{"name": "Ada"}]))
```

The classes in that example are the objects from their installed owning wheels. Edron does not
subclass, serialize-copy, proxy, or re-export them under private replacements. Native package
versions, maturity labels, diagnostics, component IDs, handles, assets, Explorer metadata, and
security/accessibility limits remain observable.

Mixed Edron/native application registration uses one Hedron app/catalog. Dependency aggregation
does not imply automatic re-export of every native symbol from `edron`; advanced authors continue
to import package-native APIs from their owners.

## Assets and offline behavior

Every first-party package owns and ships its required browser assets in its own wheel. Edron
references them through Hedron's native asset registry/planner so full pages and HTMX fragments
deduplicate the same asset identity. Edron must not copy a chart/map/data asset into its wheel under
a second path or version.

Base acceptance requires:

- no Node/npm installation to use or build the published Edron wheel/sdist;
- no CDN/package-index fetch to import Edron, construct an app, or render the base semantic UI;
- locally packaged first-party runtime JavaScript/CSS with native integrity/CSP behavior;
- package-data manifests that include every required asset/schema/template/type marker;
- deterministic missing-asset diagnostics that identify the owning distribution; and
- wheel/sdist parity for asset identity and bytes where reproducible build policy applies.

An explicit map tile/data provider or third-party adapter may require application network access.
That requirement is declared by the native feature and is not confused with Edron package or UI
asset installation. No adapter downloads browser libraries during a request as a hidden install.

## CLI and installer boundary

The `edron` console script is installed by the base distribution. `edron run` uses the bundled
development server dependency; the documented base reload path must work without asking the user to
install `edron[server]` or another Hedron package.

`edron doctor [APP]` reports:

- Edron/Python/platform information;
- every required distribution, installed version, accepted range, and owner;
- required-train conflicts or missing package data/assets;
- each curated optional capability as available, missing, incompatible, or broken;
- native adapter identity and maturity when available; and
- exact remediation appropriate to the diagnostic audience.

`doctor` never installs, upgrades, removes, resolves, or downloads a package. It does not treat
successful metadata lookup as proof that an import/adapter works. Plain static `edron check` reads
source/metadata without importing optional application libraries; trusted registration/doctor
paths clearly disclose when imports will execute.

Edron is package-manager neutral at runtime. Documentation and diagnostics may render approved
commands for `pip` and `uv`; adding another renderer does not change capability semantics.

## Reproducible environments

Edron's library metadata supplies compatible ranges, not an application lock. Production guidance
requires applications to declare their direct optional dependencies and commit a lockfile or
constraints set appropriate to their package manager and platforms.

Installing `edron[plotly]` is convenient for exploration. A production project should normally
record both Edron and its chosen backend in its dependency declaration so the application intent is
visible without knowing Edron's shortcut registry.

Release CI resolves from empty environments with caches disabled where practical. Tests must not
inherit the repository workspace, editable sibling packages, globally installed distributions,
unpublished local versions, or build outputs. Resolver tests cover both supported `pip` and `uv`
workflows without making either tool a runtime dependency.

## Wheel and source-distribution requirements

Every release publishes a wheel and source distribution built from the same tagged source. The
release gate verifies:

- normalized name/version and matching wheel/sdist metadata;
- supported `Requires-Python`, classifiers, license files, project URLs, and README;
- exact `Requires-Dist` base ranges and `Provides-Extra` shortcut metadata;
- no undeclared files, secrets, caches, tests, local paths, editable references, or sibling source
  trees in the wheel;
- `py.typed`, annotations/stubs, CLI entry point, offline diagnostics, and Edron-owned package data;
- build/install without repository-only files or undeclared build dependencies;
- wheel and sdist installation into clean environments;
- reproducible asset/manifests and software-composition/license inventory; and
- a smoke import with no network and no optional third-party distributions installed.

Published artifacts must not contain direct URL/path dependencies. The source distribution must
build without Node or a network asset compilation step; any generated Edron-owned frontend artifact
is committed/versioned and verified before publication.

Release provenance, hashes, trusted-publisher configuration, vulnerability/license review, and
rollback/yank procedure follow the repository release policy. Packaging acceptance records the
actual artifact hashes and resolved dependency matrix rather than treating a successful workspace
test as publication evidence.

## Security and supply-chain constraints

- Capability IDs, distribution names, modules, adapters, extras, and commands come from the sealed
  manifest, never a request or arbitrary application string.
- Distribution metadata is compatibility input, not trusted executable policy; the owning adapter
  still validates values and native security contracts.
- Entry-point loading follows Hedron's declared plugin trust/allowlist policy and never scans or
  executes arbitrary plugins merely to answer an unauthenticated request.
- Optional imports occur only after fixed metadata/range checks and never through `eval`, dynamic
  request-derived import, or shell execution.
- Diagnostic commands are rendered text with safe quoting; no “Install” HTTP/button action invokes
  them.
- Required and optional dependency ranges are scanned for advisories and license compatibility at
  release. A known critical incompatible dependency blocks publication.
- Package artifacts exclude credentials, local configuration, absolute build paths where avoidable,
  signing keys, `.env` files, private indexes, and source-control metadata.
- First-party assets use the native CSP/integrity/version policy. Optional remote assets/data retain
  an explicit native disposition and cannot silently weaken the application policy.

## Performance and size constraints

Stage 0 freezes numeric budgets for:

- compressed/uncompressed Edron wheel and complete clean base environment size;
- `import edron` cold/warm time and modules imported;
- application construction and required native feature registration;
- optional capability metadata detection, successful import, and negative-result caching;
- first-party asset count, raw/gzip bytes, and duplication across package boundaries;
- `edron doctor` cold/warm runtime and bounded diagnostic output; and
- installation resolver time in the supported clean-environment lanes.

The base must not include heavyweight third-party dataframe/plotting/database ecosystems merely to
avoid capability errors. Optional modules are not imported on the base path. Packaging convenience
cannot add a second component tree, asset copy, plugin scan, or repeated per-request metadata scan.

## Compatibility and upgrade rules

Edron `0.x` supports a documented bounded Hedron train. An incompatible manually assembled
environment fails with a clear required-train diagnostic during doctor/application startup rather
than continuing with guessed private APIs.

Compatibility promises include:

- the `edron` distribution/import/CLI names;
- the documented Python and native dependency train for each release;
- base availability of the curated first-party batteries;
- direct compatible dependency activation independent of shortcut use;
- stable capability IDs and error categories;
- identity/provenance of native objects and adapters; and
- extras remaining installation conveniences rather than runtime flags.

Range widening and support for a newly verified third-party version may ship compatibly when the
owner adapter evidence passes. Tightening a range requires a documented correctness/security
reason, migration command, and clean upgrade evidence. Required-train changes must be coordinated
across all base dependencies.

A new shortcut may be added without changing runtime behavior. Renaming/removing a shortcut is a
breaking packaging change and cannot make direct compatible installation stop working. It follows
the project's major-version/deprecation policy unless an urgent security reason makes the shortcut
unsafe; the underlying adapter has its own native deprecation record.

Removing Edron from an application leaves separately installed native packages usable through
their documented imports. Generated Edron paths/IDs are not packaging compatibility promises.

## Testing strategy

The packaging acceptance suite includes:

1. **Artifact tests:** wheel/sdist contents, metadata parity, `py.typed`, CLI, licenses, package
   data, forbidden paths/secrets, and build from the published sdist.
2. **Base clean-install tests:** plain `pip install edron` and `uv add edron` in empty environments
   run the hello, table/data-edit, first-party chart, map, Markdown, server, and HTMX golden paths.
3. **No-leak tests:** artifact tests run outside the monorepo without editable/global sibling
   packages; removing any required declared distribution produces a required-train failure.
4. **Python/platform tests:** every supported Python and platform lane resolves, imports, runs the
   CLI, renders, and builds/installs the sdist.
5. **Optional matrix:** for every capability, absent, direct-installed, shortcut-installed,
   incompatible-low/high, broken-import, and platform-marker cases are exercised.
6. **Equivalence tests:** direct and shortcut environments have equivalent relevant resolved
   requirements, native adapter identity, output, assets, maturity, and diagnostics.
7. **Drift tests:** built metadata, owning adapter ranges, sealed manifest, docs tables, commands,
   extras, and doctor output match exactly.
8. **Import tests:** root import side-effect/module budget, no optional imports, no network/file
   access, no global registration, and clear corrupt-base behavior.
9. **Interop tests:** native imports/identity, one catalog, mixed registration, plugin policy,
   asset ownership/deduplication, and uninstall/rollback behavior.
10. **Diagnostic tests:** missing/incompatible/broken classification, preserved causes, quoting,
    redaction, audience-specific output, offline anchors, JSON/SARIF stability, and no installer.
11. **Asset tests:** wheel/sdist assets, offline base rendering, CSP/integrity, fragment
    deduplication, owner provenance, and explicit remote-data limitations.
12. **Upgrade/security tests:** compatible upgrades, invalid mixed trains, range changes, yanked/
    advisory releases, dependency confusion resistance, artifact inventory, and rollback.
13. **Performance tests:** artifact/environment size, resolver/import/registration/doctor budgets,
    optional lazy-load cost, and comparison with equivalent native Hedron installations.

## Acceptance criteria

- **EDR-PKG-ARTIFACT-001:** Wheel and sdist contents, metadata, typing, CLI, licenses, package data,
  reproducibility, clean build/install, and provenance evidence pass.
- **EDR-PKG-BASE-001:** Plain `pip install edron` provides every documented base battery and
  development-server path without another Hedron/feature installation command.
- **EDR-PKG-TRAIN-001:** Python support and exact bounded required-distribution ranges are frozen,
  mutually resolvable, native-compatible, and verified on the supported platform matrix.
- **EDR-PKG-AUTHORITY-001:** Edron aggregates but does not vendor, fork, shadow, or re-register
  native packages; object, adapter, plugin, asset, maturity, and diagnostic ownership remain native.
- **EDR-PKG-CAPABILITY-001:** Every optional capability follows fixed metadata/version/import/native
  resolution and distinguishes available, missing, incompatible, and broken states.
- **EDR-PKG-EXTRA-001:** Each shortcut's resolved requirements and behavior equal direct compatible
  installation; runtime never detects the requested extra and no `all`/empty feature extra exists.
- **EDR-PKG-DIAGNOSTIC-001:** Capability errors contain exact safe direct/shortcut remediation,
  call-site/owner facts, preserved safe causes, offline references, and audience redaction without
  executing an installer.
- **EDR-PKG-IMPORT-001:** Root import meets side-effect/module/time budgets and imports no optional
  ecosystem, discovers no arbitrary plugin, registers no global app, and performs no I/O/network.
- **EDR-PKG-ASSET-001:** First-party assets remain in owning wheels, work on the offline base path,
  use one native asset authority, deduplicate across full/fragment responses, and pass CSP/integrity.
- **EDR-PKG-DRIFT-001:** The sealed requirement manifest, built metadata, owning adapter ranges,
  docs, extras, commands, and runtime/doctor diagnostics cannot diverge.
- **EDR-PKG-SECURITY-001:** Fixed imports/entry points, advisory/license review, artifact hygiene,
  dependency-confusion controls, diagnostic quoting/redaction, and no-runtime-installer tests pass.
- **EDR-PKG-COMPAT-001:** Clean install, direct/shortcut, upgrade, invalid-train, uninstall,
  rollback, wheel/sdist, and application-lock guidance pass without disabling native use.
- **EDR-PKG-PERF-001:** Numeric artifact, environment, import, registration, detection, asset,
  doctor, and resolver budgets are frozen and pass.

## See also

- [Edron 0.1 public API](EDRON.md)
- [Edron state and interaction](EDRON_STATE_INTERACTION.md)
- [Edron capability inventories](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_CAPABILITY_INVENTORIES.md)
- [Edron implementation specification](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_001.md)
- [Edron acceptance packet](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/EDRON_001.md)
- [RFC-0094](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md)
- [Edron golden applications](https://github.com/eddiethedean/hedron/blob/main/docs/implementation/EDRON_GOLDEN_APPS.md)
- [Hedron package-native workflows](PACKAGE_WORKFLOWS.md)
- [Hedron curated extras](EXTRAS.md)
- [Current release and support](../guides/current-release.md)
