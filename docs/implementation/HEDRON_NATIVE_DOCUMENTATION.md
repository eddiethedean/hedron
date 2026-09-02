# `hedron-docs` and Hedron-native documentation implementation plan

**Status:** Draft / unassigned

**Owning proposal:**
[`RFC-0088`](../rfcs/RFC-0088-HEDRON-NATIVE-DOCUMENTATION.md)

**Production acceptance:**
[`HEDRON_NATIVE_DOCS_CUTOVER`](../acceptance/HEDRON_NATIVE_DOCS_CUTOVER.md)

## Outcome

Build an experimental `hedron-docs` compiler/runtime package and prove it through Hedron's public
documentation application, deployed to FastAPI Cloud behind a provider-neutral domain. Maintainers
continue to author Markdown, but the published site compiles supported Markdown constructs into
native Hedron component plans. Search, navigation, responsive chrome, themes, API reference, live
examples, error pages, and deployment behavior all exercise Hedron's supported public paths.

This plan intentionally does not assign a release number. Stage 0 ends with an accepted RFC,
measured prototype, frozen inventories, and tracked implementation work. Production cutover is a
separate evidence-backed decision.

## Delivery principles

1. **Vertical slices before corpus migration.** Prove one page of each difficult type before
   converting hundreds of pages.
2. **Native nodes, not an HTML-shaped shortcut.** The compiler lowers content to Hedron components;
   compatibility HTML is exceptional, inventoried, sanitized, and removable.
3. **One source corpus.** Markdown is not duplicated into Python or a second content tree.
4. **No information-architecture rewrite during renderer parity.** Navigation improvements follow
   the safe hosting cutover unless needed for accessibility or correctness.
5. **Stateless public runtime.** No database, shared process mutation, or instance affinity is
   required for pages, search, or first-cut live demos.
6. **Generic improvements earn promotion.** Docs-local helpers stay local until independent Hedron
   use cases and compatibility requirements are clear.
7. **Every milestone is reversible.** MkDocs remains buildable and deployable until production
   observation and rollback gates close.
8. **Experimental package, narrow surface.** `hedron-docs` begins outside the stable train; only the
   CLI, configuration, compiler entry point, manifest loader, and app factory are candidate public
   surfaces before the first-party migration closes.

## Proposed repository shape

The package and application names are selected; detailed module placement remains provisional until
RFC acceptance and the vertical-slice prototype.

```text
packages/hedron-docs/
├── pyproject.toml
├── README.md
├── CHANGELOG.md
├── src/hedron_docs/
│   ├── __init__.py
│   ├── config.py               # native config + bounded MkDocs import
│   ├── ast.py                  # typed, source-located document nodes
│   ├── markdown.py             # parser adapter
│   ├── lower.py                # AST -> Hedron document plan
│   ├── manifest.py             # immutable schema and serialization
│   ├── diagnostics.py
│   ├── navigation.py
│   ├── search.py               # deterministic bounded index
│   ├── app.py                  # manifest -> Hedron/ASGI app
│   ├── cli.py
│   └── components/
└── tests/
apps/hedron-docs/
├── pyproject.toml
├── hedron-docs.toml            # site policy and MkDocs migration input
├── src/hedron_docs_app/
│   ├── __init__.py
│   ├── main.py                 # app factory call and explicit entrypoint
│   ├── settings.py             # domain, environment, app budgets
│   ├── components/
│   │   └── shell.py
│   └── demos/
│       ├── registry.py
│       └── ...                 # explicit bounded examples
├── tests/
└── README.md
docs/
├── ...                         # existing canonical Markdown corpus
└── navigation.toml             # optional later replacement for mkdocs nav/excludes
build/hedron-docs/               # ignored local compiler output
```

The package and application are uv workspace members. The application depends on the in-tree
`hedron-docs` and `hedron` packages. The deployed application directory is `apps/hedron-docs`;
FastAPI Cloud resolves its dependencies through the root workspace lock. Packaging must include or
generate the public content manifest without relying on files outside the uploaded repository.

## Architectural flow

```text
Markdown + generated pages + release facts + current navigation
                              │
                              ▼
             validate roots, metadata, syntax, links
                              │
                              ▼
                   source-located document AST
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
          Hedron node plan  search data  route/nav/asset data
                 └────────────┼────────────┘
                              ▼
                  immutable document manifest
                              │
                              ▼
          Hedron pages + fragments + explicit live demos
                              │
                              ▼
                  local ASGI / CI / FastAPI Cloud
```

The manifest is the boundary between untrusted/complex compilation and bounded request handling.
Production requests resolve known identifiers and render known Hedron components; they do not parse
Markdown or import arbitrary Python targets.

## Provisional package surface

The initial plan reserves this small user-facing surface while leaving AST and lowering details
experimental:

```bash
hedron-docs check [CONFIG]
hedron-docs build [CONFIG]
hedron-docs serve [CONFIG]
hedron-docs import-mkdocs MKDOCS_CONFIG
```

```python
from hedron_docs import DocsBuildConfig, compile_site, create_docs_app, load_manifest
```

`check` validates without publishing output. `build` writes the deterministic manifest and
fingerprinted asset set. `serve` is a development convenience that builds before starting the same
app factory used in production. `import-mkdocs` translates only declared site metadata,
navigation, and exclusion policy; it does not execute arbitrary MkDocs plugins or reproduce a
theme. Exact names remain provisional until the parser/manifest prototype proves them.

## Workstreams

### W0 — Baseline and ownership

**Purpose:** turn assumptions about the current public site into machine-readable facts.

Deliverables:

- snapshot the strict MkDocs public route set, anchors, titles, navigation, redirects, search
  examples, local assets, and generated pages;
- inventory every admitted Markdown extension and every raw/custom HTML use;
- separate public documents from the maintainer corpus using the current exclusions and ownership
  configuration;
- count and classify API directives, admonitions, tabs, diagrams, generated demos, and custom
  hooks/assets;
- record current desktop/narrow, light/dark, search, 404, print, and performance baselines;
- resolve the RFC phase/cross-cutting owner, tracking issue, and workstream owners; and
- freeze the initial canonical-domain and version-retention decision.

Exit: no public syntax or route class is absent from an inventory disposition.

### W1 — Experimental package, workspace application, and production skeleton

**Purpose:** prove the repository and cloud deployment shape before building content features.

Deliverables:

- create `packages/hedron-docs` and `apps/hedron-docs` workspace members, supported Python pins,
  locked dependencies, and an explicit FastAPI entrypoint;
- establish experimental maturity metadata, a `py.typed` marker, clean wheel installation, and
  public-import smoke tests without adding the package to the stable support matrix;
- add the minimal CLI/config/compiler/manifest/app-factory seams with unsupported placeholders
  failing explicitly;
- construct `Hedron` with production-safe sessions, Explorer, security, CSP, and asset settings;
- add health/readiness, structured errors, a Hedron 404, and an immutable build identifier;
- run locally through the same entrypoint FastAPI Cloud will use;
- deploy a non-canonical preview with no DNS changes; and
- document ignore rules, environment variables, deploy configuration, and log access.

Exit: a clean-installed experimental package builds a minimal deterministic manifest, and its
first-party Hedron app deploys from the workspace, becomes healthy, and passes production-mode smoke
tests without secrets or a database.

### W2 — Package-owned typed document AST and diagnostics

**Implementation status:** Complete in the experimental `hedron-docs` 0.2 line. This records the
compiler milestone only; it does not imply RFC acceptance, public-site cutover, or completion of
W3–W12.

**Purpose:** select and contain the Markdown parsing boundary.

Deliverables:

- parser spike against representative and adversarial pages;
- native `hedron-docs.toml` configuration and a bounded current-`mkdocs.yml` importer;
- typed block/inline nodes with source file, line, column, and source-span identity;
- explicit nodes for extensions rather than post-render HTML rewriting;
- depth, node, source-byte, table, code-block, and directive budgets;
- deterministic normalization and heading-ID algorithm;
- diagnostics with code, title, location, explanation, and remediation; and
- parser golden tests on all Required constructs.

Exit: representative source parses deterministically without raw HTML rendering or silent syntax
loss.

The 0.2 implementation uses direct Markdown token lowering rather than an HTML round-trip. It
ships a closed node vocabulary with stable source spans; explicit admonition, details, tabs,
footnote, definition-list, API-directive, and demo-directive nodes; schema-2 native configuration
with normalized navigation import; and source-byte, node, depth, table-cell, code-block, and
directive budgets. The package golden/adversarial tests are the executable W2 evidence.

### W3 — Native Hedron content lowering

**Implementation status:** Complete in the experimental `hedron-docs` 0.3 line. This is an
intentional clean schema break from W2; the renderer does not retain a compatibility path for the
0.2 manifest or configuration contracts.

**Purpose:** render documentation content through actual Hedron primitives.

Deliverables:

- prose, heading, link, image, list, quote, code, table, alert, tabs, and footnote lowerers;
- docs-local finite variants where ordinary Hedron presentation is insufficient;
- stable anchor aliases and fragment-target styling;
- responsive overflow behavior for code and tables;
- code language labels and copy controls with no inline-script dependency;
- explicit compatibility-node registry for any temporarily admitted trusted markup; and
- render snapshots proving semantic structure, escaping, and expected public markers.

Exit: the vertical-slice document set renders with native nodes and no untracked opaque document
body.

The 0.3 implementation lowers every W3 construct through Hedron primitives or safe native
semantic elements. Headings emit canonical and alias anchors with fragment-target markers; links,
images, lists, quotes, alerts, tabs, tables, footnotes, and inline emphasis preserve typed
structure; code blocks use `CodeViewer` plus a native `ClipboardCopy` control and language label;
code and table output is wrapped for narrow-screen overflow. Package-owned CSS is served as an
immutable asset, and the renderer has an explicit empty compatibility-node registry: no trusted raw
HTML is admitted. Semantic render snapshots and security regressions are the W3 evidence.

### W4 — Content manifest, routes, and navigation

**Purpose:** make publication deterministic and request routing bounded.

Deliverables:

- versioned manifest schema with content/compiler hashes;
- normalized importer for current `mkdocs.yml` nav and exclusion policy;
- route collision, case, slash, Unicode, and reserved-prefix validation;
- breadcrumbs, current section, previous/next, edit/source link, and page TOC data;
- explicit asset inventory with jailed paths, MIME validation, and fingerprints;
- catch-all document routing that resolves only through the manifest;
- sitemap, robots, canonical, description, release banner, and Open Graph basics; and
- manifest determinism and stale-generated-output checks.

Exit: every preview route is declared by the manifest, every internal link resolves or has an
approved migration disposition, and two clean compiles match byte-for-byte.

### W5 — Hedron application shell

**Purpose:** make the site itself a convincing Hedron product application.

Deliverables:

- Hedron-native header, primary navigation, mobile navigation, main content, local TOC, and footer;
- skip link, breadcrumbs, current-page state, previous/next navigation, and source/edit action;
- responsive desktop/narrow layouts with no application-authored JavaScript framework;
- light/dark/system mode using the supported Hedron path;
- release/development banner driven by canonical release facts;
- Hedron-rendered 404 and compile-safe error presentation; and
- no-JavaScript ordinary navigation and form behavior.

Exit: home, quickstart, guide, API, component, and 404 vertical slices pass the visual/a11y matrix.

### W6 — Search

**Purpose:** replace Material/Read the Docs search without adding an external service.

Deliverables:

- deterministic normalized index from the public manifest;
- typed bounded query and filter models;
- full search-results page and progressively enhanced fragment endpoint;
- ranking classes for tutorials/guides, component/reference pages, generated signatures, diagnostic
  codes, and exact public symbols;
- accessible results count/status, keyboard behavior, focus behavior, and empty/no-result states;
- stable query URL for sharing and no-script use;
- ranking fixture set based on real adopter questions; and
- latency, memory, index-size, hostile-input, and redaction tests.

Exit: the frozen query corpus meets relevance and performance gates with and without JavaScript.

### W7 — API reference compiler

**Purpose:** replace `mkdocstrings` without evaluating client-controlled names.

Deliverables:

- parse current `:::` blocks and their admitted options;
- static package/module/symbol allowlist generated from the workspace;
- build-time public symbol import and signature/doc extraction;
- Hedron reference components for signature, parameters, returns, errors, stability, and source;
- diagnostics for missing/private/ambiguous symbols and import failures;
- deterministic output fixtures across the supported Python baseline; and
- coverage parity with existing API documentation checks.

Exit: all public API directives compile strictly and the API vertical slice is readable, linkable,
and searchable.

### W8 — Live feature showcase

**Purpose:** make real Hedron capability visible inside task-oriented docs.

Deliverables:

- explicit demo registry and source/embed synchronization contract;
- request-scoped typed form validation demo;
- fragment update and typed refresh/action demo;
- chart and map demos with textual/table alternatives;
- theme, loading, empty, error, and success-state demonstrations;
- demo-level budgets, audit events, error redaction, and abuse tests;
- no-script/static fallback or honest simulation label for every demo; and
- a local/CI Explorer or scenario view for maintainers without exposing the public Explorer.

Exit: the approved first-cut demo inventory is live, bounded, accessible, deterministic enough for
tests, and does not mutate shared infrastructure.

### W9 — Generated content and authoring loop

**Purpose:** keep documentation maintenance at least as reliable as today.

Deliverables:

- preserve component-doc and simulation generators or migrate their output contract explicitly;
- compiler watch/preview command with source-located diagnostics;
- documented `hedron-docs check`, `build`, `serve`, and migration-import behavior;
- fast narrow check for one edited page and strict full-corpus check for CI;
- documentation ownership, release-train SSOT, package inventory, API coverage, recipe sync, and link
  checks operating on the new public manifest;
- contributor guidance for syntax, live demos, assets, search metadata, and failure behavior; and
- migration lints that prevent new unsupported MkDocs-only constructs after the syntax freeze.

Exit: a normal prose edit has a documented package-backed local loop and docs-only CI does not
require the full package/browser matrix unless the change touches compiled behavior or demos.

### W10 — Compatibility and parity migration

**Purpose:** migrate the corpus without losing public behavior.

Deliverables:

- batch conversion ordered by page archetype, not directory size;
- route/anchor/metadata/link parity report on every batch;
- explicit disposition for every custom JavaScript/CSS/override behavior;
- replacement of provider-bound canonical links with the selected neutral domain only after that
  domain is approved;
- historical-version access and Read the Docs retention behavior;
- search relevance comparison for the frozen query corpus; and
- a zero-unclassified-difference cutover report.

Exit: the complete public corpus compiles; every parity difference is fixed or explicitly accepted.

### W11 — Browser, accessibility, security, and performance closure

**Purpose:** prove the flagship app meets the same bar it teaches.

Deliverables:

- three-engine browser matrix across the required page archetypes;
- keyboard, focus, history, fragment, no-JS, forced-colors, reduced-motion, zoom/reflow, text-spacing,
  RTL where applicable, and print evidence;
- axe checks with honest human-AT scope;
- Markdown/directive/search/demo/path/URL adversarial corpus;
- production CSP, headers, redaction, cache, multiple-instance, startup, and failure tests;
- compile/startup/warm/cold/search/asset budgets frozen from measured baselines; and
- leak checks across repeated HTMX navigation and demo use.

Exit: all non-cutover quality gates in the acceptance plan are Verified.

### W12 — FastAPI Cloud cutover and observation

**Purpose:** move public traffic safely and reversibly.

Deliverables:

- protected production deployment workflow and scoped credentials;
- preview smoke and production-like load/error observation;
- custom-domain/TLS setup and DNS record inventory;
- pre-cutover backup and verified Read the Docs fallback;
- timed DNS cutover, smoke checks, logs/metrics observation, and rollback thresholds;
- package metadata, README, badge, sitemap, and canonical-link updates; and
- post-cutover retention decision after the observation window.

Exit: the explicit go/no-go decision is recorded, DNS cutover succeeds, the observation window
closes without rollback criteria, and legacy access remains as promised.

## Vertical-slice milestone

Do not begin bulk corpus migration until this slice is complete:

| Page | Why it is selected | Required proof |
|---|---|---|
| Home | branding, calls to action, release facts | shell, metadata, responsive first screen |
| Quickstart | prose and copyable code | headings, code, links, tabs/admonitions |
| Styling or interaction guide | long task content | TOC, anchors, tables, deep navigation |
| `api/AUTODOC` subset | difficult generated content | API directives, signatures, source links |
| One component page | generated + interactive | generator ownership, live demo, code sync |
| Search results | typed interaction | ranking, fallback, focus/status behavior |
| 404 | error semantics | status code, recovery navigation, metadata |

The slice deploys to a preview hostname and runs against the in-tree workspace revision. It is not a
production cutover candidate until W0 inventories and W11 baseline evidence are complete.

## Dependencies and sequencing

```text
W0 ──► W1 ──► W12
 │      │
 ├──► W2 ──► W3 ──► W4 ──► W5 ──► W10 ──► W11 ──► W12
 │                   │       │
 │                   ├──► W6 ┘
 │                   ├──► W7 ┘
 │                   └──► W8 ┘
 └──────────────────────► W9 ───────────────► W10
```

- W1 can prove cloud/workspace viability while W2 evaluates parsers.
- W6, W7, and W8 can proceed after the manifest and shell boundaries are stable.
- W9 begins early but cannot freeze author guidance until admitted syntax is frozen.
- W10 starts with the vertical slice and expands only after native lowering is stable.
- W12 may create previews early; it may not change canonical DNS before W11 and all cutover gates.

## Provisional budgets

W0/W11 must measure and refine these before RFC acceptance. They are initial engineering targets,
not claims about the current app or FastAPI Cloud:

| Surface | Provisional target |
|---|---|
| Full public compile | no network; deterministic; no worse than the existing strict docs CI budget |
| Warm document render | p95 at or below 150 ms in the reference local benchmark |
| Warm search | p95 at or below 100 ms over the frozen query corpus |
| Search query | 1–200 Unicode code points; explicit empty and oversized behavior |
| Initial compressed first-party transfer | measured against current site; no unexplained regression over 10% |
| Runtime remote dependencies | zero for document render and search |
| Request-time source parsing/import | zero |
| Live demo request | explicit per-demo time, input-byte, output-byte, and concurrency budget |

Cold-start targets must be based on observed FastAPI Cloud behavior and separated from Hedron render
time. A provider cold start cannot be hidden inside a framework performance claim.

## Promotion rules for Hedron changes

When the docs app finds a missing capability:

1. Record the user-visible gap and the docs-local workaround.
2. Decide whether the gap is documentation policy or a generic application need.
3. If generic, add an independent non-docs use case and public API/compatibility proposal.
4. Implement and test it in the owning Hedron package.
5. Consume the public packaged-style API from the docs app.
6. Remove the docs-local workaround and retain a regression fixture.

The docs app may not import private Hedron modules simply to avoid this process.

## Stop conditions

Pause expansion and return to design review when any of these occurs:

- Required current syntax cannot be represented without a broad raw-HTML bypass.
- A selected parser cannot supply deterministic source-located structure or introduces a required
  Node/runtime service into the supported authoring loop.
- Live demos require shared mutable state, arbitrary code execution, or secrets to prove the first
  cut.
- Route/anchor parity cannot be expressed without breaking common inbound links.
- Search quality is materially worse for the frozen adopter queries.
- The preview cannot run from a locked uv workspace through the production entrypoint.
- Accessibility, no-JS, security, or performance regressions remain unclassified.
- FastAPI Cloud configuration requires a portability-breaking application design.

## Stage 0 completion checklist

- [ ] RFC-0088 accepted or explicitly revised/rejected.
- [ ] Roadmap/cross-cutting owner and tracking issue recorded.
- [ ] W0 syntax, route, anchor, asset, and behavior inventories frozen.
- [ ] Parser and manifest schema selected with prototype evidence.
- [ ] `hedron-docs` experimental package boundary, CLI, native config, and MkDocs adapter disposition
      reviewed.
- [ ] Clean wheel install builds and serves the vertical-slice manifest using public imports only.
- [ ] Vertical-slice app runs locally and on a non-canonical FastAPI Cloud preview.
- [ ] Initial threat, accessibility, and performance baselines reviewed.
- [ ] Canonical-domain, version-retention, deployment, and rollback decisions closed.
- [ ] Workstream issues have dependencies, owners, and acceptance gates.
- [ ] No package version, production URL, or implementation status is claimed by planning alone.
