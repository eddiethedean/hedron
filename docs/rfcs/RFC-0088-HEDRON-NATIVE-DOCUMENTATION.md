# RFC-0088: `hedron-docs` compiler and Hedron-native documentation application

**Status:** Draft
**Phase:** Unassigned; roadmap ownership requires a later decision
**Planning baseline:** Published `v1.0.5`
**Target:** Preview and production cutover are evidence-gated, not version-gated in this draft

**Implementation plan:**
[`HEDRON_NATIVE_DOCUMENTATION`](../implementation/HEDRON_NATIVE_DOCUMENTATION.md)

**Acceptance and cutover plan:**
[`HEDRON_NATIVE_DOCS_CUTOVER`](../acceptance/HEDRON_NATIVE_DOCS_CUTOVER.md)

## Summary

Introduce an experimental `hedron-docs` package that compiles a bounded Markdown documentation
corpus into an immutable site manifest consumed by a Hedron application. Its first proving consumer
is Hedron's own public documentation application, deployed on FastAPI Cloud. The application uses
Hedron for page rendering, application chrome, navigation, search, responsive behavior, typed
interactions, live component examples, themes, and error pages. The documentation corpus remains
Markdown so maintainers keep a reviewable, diff-friendly authoring format, but the compiler lowers
supported constructs into native Hedron component plans rather than returning one opaque HTML
document.

The package begins as an explicitly experimental tooling surface, not a stable extension of the
Hedron 1.0 contract. The site is its flagship proving consumer and must demonstrate the same public
Hedron APIs and deployment story that Hedron recommends to adopters. Generic compilation and
runtime behavior belongs in `hedron-docs`; Hedron-site information architecture, branding, ranking
fixtures, release banners, and demo selection remain in the application. Missing generic Hedron
capability discovered by the site should be fixed in Hedron and evidenced independently.

The migration is not a hosting wrapper around the current MkDocs output. MkDocs remains the
production fallback and parity oracle during migration, then leaves the published runtime after the
cutover gates are Verified.

## Motivation and background

The existing site is a mature MkDocs Material application configured in `mkdocs.yml` and hosted by
Read the Docs. It provides task-oriented navigation, search, API extraction, admonitions, content
tabs, syntax highlighting, stable heading anchors, custom JavaScript and CSS, generated component
pages and demonstrations, a release banner, and a custom 404 page. Those behaviors are user-facing
contracts even when their implementation is not a Hedron API.

Hedron is intended to build typed, server-rendered Python applications with FastAPI and HTMX. Its
own public documentation is therefore the best sustained test of application chrome, content
presentation, responsive layout, navigation, typed search, fragments, charts, maps, forms,
accessibility, security, performance, and deployment. A Hedron-native site provides stronger
evidence than a component gallery because it must remain usable across a large, frequently edited
corpus.

The current `hedron.content.Markdown` component is deliberately narrow. It enables fenced code and
tables, sanitizes the result, and returns it inside one `hedron-markdown` container. That remains a
useful application component, but it does not preserve all current documentation syntax and does
not exercise the native Hedron primitives inside the document. This proposal therefore introduces
a documentation compiler rather than broadening `Markdown` into an implicit static-site framework.

FastAPI Cloud is a suitable deployment target because the docs are a normal FastAPI/Hedron
application. Its application-directory feature supports monorepos and uv workspaces, including
workspace dependencies. Its GitHub integration can deploy the default branch, and custom domains
can be attached after a successful deployment:

- [Application directory and uv workspace support](https://fastapicloud.com/docs/builds-and-deployments/application-directory/)
- [GitHub integration](https://fastapicloud.com/docs/source-control/github-integration/)
- [Custom domains](https://fastapicloud.com/docs/advanced-features/custom-domains/)

Provider behavior is deployment context, not a Hedron runtime dependency. The app must remain
runnable under ordinary ASGI hosting and testable without a FastAPI Cloud account.

## Goals

1. Publish a real Hedron application whose ordinary use visibly exercises Hedron.
2. Preserve Markdown as the canonical prose source and preserve generated-file ownership rules.
3. Compile supported document constructs to native Hedron components with deterministic output.
4. Preserve public URLs, linkability, search usefulness, metadata, and accessibility through the
   provider migration.
5. Make live examples safe, bounded, representative, and usable without arbitrary code execution.
6. Keep production rendering stateless and compatible with multiple instances and scale-to-zero.
7. Establish repeatable parity, preview, cutover, observation, and rollback evidence.
8. Establish a narrow reusable package boundary without promising stable APIs before the corpus
   and first-party application validate it.
9. Separate reusable Hedron capability gaps from documentation-application policy.

## Non-goals

- Reproduce MkDocs Material's DOM or visual design pixel for pixel.
- Turn all Markdown or static-site behavior into public `hedron` APIs.
- Provide a drop-in MkDocs plugin, theme, or complete compatibility implementation.
- Declare `hedron-docs` Stable before a separately accepted compatibility review.
- Require Python source files for ordinary prose authoring.
- Execute arbitrary Python, shell, browser, or network code supplied by a documentation page.
- Make the public documentation application a general multi-tenant content-management system.
- Add a database, user accounts, comments, analytics, or personalization to the first cutover.
- Move the internal RFC, acceptance, implementation, research, or maintainer ledger into the public
  navigation when it is currently excluded.
- Claim FastAPI Cloud portability features as Hedron features.
- Remove the Read the Docs deployment before the rollback window closes.
- Assign this initiative to a release phase without an accepted decision and tracking issue.

## Terminology and ownership

- **Source document:** a Markdown file and its declared metadata under an authorized documentation
  root.
- **Document AST:** a typed, source-located intermediate representation produced without rendering
  raw HTML.
- **Documentation compiler:** the build/startup pipeline that validates source documents and lowers
  supported AST nodes into an immutable document manifest.
- **Compiler package:** the experimental `hedron-docs` distribution containing configuration,
  parsing, diagnostics, lowering, manifest, search, runtime, and CLI boundaries.
- **Document manifest:** the route, navigation, metadata, heading, search, asset, API-reference, and
  demo facts consumed by the runtime.
- **Docs shell:** the Hedron application chrome around document content.
- **Live demo:** an explicitly registered, bounded Hedron route family embedded by identifier.
- **Parity oracle:** the current strict MkDocs build and its route/content inventory during
  migration. It is not the target runtime.

The `hedron-docs` package owns generic source configuration, parsing, diagnostics, lowering,
manifest schemas, bounded search mechanics, and application construction. The documentation
application owns Hedron-specific navigation policy, ranking fixtures, site branding, release
banners, canonical URL policy, and demo selection. Hedron owns reusable components, rendering,
interactions, security boundaries, styling, and diagnostics promoted through their own contracts
and tests.

## Proposed design

### Package boundary

Add an experimental workspace package named `hedron-docs`, imported as `hedron_docs`. It is a
tooling package outside the stable Hedron 1.0 package set. Its initial supported workflow is:

```text
Markdown + hedron-docs.toml + optional normalized mkdocs.yml import
                              │
                  hedron-docs check/build
                              │
               immutable versioned site manifest
                              │
             create_docs_app(manifest_path)
                              │
                    ordinary ASGI application
```

The provisional command surface is `hedron-docs check`, `hedron-docs build`, and `hedron-docs
serve`. The provisional Python surface is deliberately small: a build configuration model, a
`compile_site(...)` entry point, a versioned manifest loader, and
`create_docs_app(manifest_path, ...)`. Development serving may compile before startup; production
request handling may not.

`hedron-docs.toml` is the native configuration authority for new adopters. A bounded
`import-mkdocs` adapter translates the current `mkdocs.yml` site metadata, navigation, and exclusion
policy during migration. The adapter does not promise arbitrary MkDocs plugin execution or Material
theme compatibility. Compiler internals, document nodes, and lowerers remain private or explicitly
experimental until the first-party migration demonstrates a reusable contract.

### Application boundary

Add a workspace application at `apps/hedron-docs`, with its own `pyproject.toml`, site configuration,
and configured FastAPI entrypoint. It depends on the in-workspace `hedron-docs` and Hedron packages
so the deployed preview exercises the repository revision being documented. FastAPI Cloud uses the
application directory for that workspace member; local development uses the same entrypoint.

The runtime is a `Hedron` application with:

- explicit production security settings;
- no required database or process-global mutable user state;
- the Component Explorer disabled on the public deployment unless a separately authenticated
  operator route is approved;
- a health endpoint that does not compile content or expose internal metadata;
- explicit document, search, asset, demo, and not-found route families; and
- an immutable compiled manifest loaded before serving traffic.

The app must not discover and serve an arbitrary filesystem path from a request. A request resolves
only through the validated route table in the manifest.

### Markdown authoring and native lowering

Markdown stays canonical because it is readable on GitHub, reviewable without the application, and
already owns the current corpus. The compiler parses it into a typed AST with source locations and
then lowers supported nodes into Hedron components.

Required first-cut mappings include:

| Source construct | Hedron result |
|---|---|
| Paragraph and inline text | semantic prose containers and `Text` |
| Heading | `Heading` plus deterministic explicit anchor |
| Link and image | validated `Link` / media component and authorized asset reference |
| Ordered/unordered list | semantic list components or typed native HTML composition |
| Block quote | a finite quotation/callout presentation |
| Fenced code | `CodeBlock` with language, highlighting, and copy affordance |
| Table | accessible `Table` with header ownership and overflow handling |
| Admonition | finite `Alert` variant with title and semantic role |
| Content tabs | `Tabs` with keyboard and no-script content access |
| Footnote | bidirectionally linked note and reference components |
| API directive | an allowlisted API-reference component generated from imported public symbols |
| Live-demo directive | an embed that references an explicitly registered demo identifier |

Raw HTML is not a general escape hatch. Existing pages that require trusted custom HTML receive an
inventory disposition: migrate to components, transform through an allowlisted compatibility node,
or remain blocked from cutover. Unsupported syntax fails with file, line, column, construct, and a
remediation; it is never silently dropped.

The compiler produces deterministic heading IDs. Existing public anchor IDs are fixtures. Where a
new algorithm differs, an alias anchor preserves the old inbound link unless it would create a
collision or security issue.

### Content and route manifest

The immutable manifest records at least:

- source path, public path, title, description, canonical URL, and publication state;
- navigation group, order, breadcrumb ancestry, previous/next relationships, and page labels;
- heading IDs, hierarchy, local table of contents, and compatibility aliases;
- normalized search text, headings, keywords, rank class, and result excerpt boundaries;
- local assets with content fingerprints and MIME types;
- API symbol and live-demo references;
- outbound and inbound internal links; and
- compiler version and source/content hashes.

Only public documents enter the public manifest. Existing `exclude_docs` behavior and
`docs/documentation.toml` ownership remain parity inputs until a replacement publication manifest
is accepted. Generated pages remain generated outputs whose owning scripts are unchanged or
explicitly migrated.

Compilation runs in CI and may run during an application build. Production request handling never
parses the source corpus. The deployable app contains or deterministically generates the manifest
from the repository revision before health verification succeeds.

### Hedron docs shell

Every document renders inside one Hedron-native shell with:

- skip navigation and semantic header, navigation, main, complementary TOC, and footer landmarks;
- responsive primary navigation with current-page and expanded-section state;
- breadcrumbs and previous/next task navigation;
- page title, description, release status, edit/source link, and local table of contents;
- explicit light, dark, and system theme behavior using Hedron's supported color-mode path;
- a search control that remains usable as an ordinary form without HTMX;
- release and development banners driven by existing canonical release facts; and
- a useful Hedron-rendered not-found page that returns HTTP 404.

Navigation and prose remain server rendered. HTMX may improve search, navigation, table-of-contents
state, and live examples, but ordinary links and forms are the canonical fallback. Browser history,
document title, focus, scroll position, and copied fragment URLs must remain correct after enhanced
navigation.

### Search

The first production search is a deterministic, bounded, in-memory index compiled from the public
manifest. It requires no external search service. A typed query model validates length and filters.
The same search operation supports:

- a full results page for ordinary form submission; and
- a Hedron component/fragment response for enhanced suggestions and result updates.

Ranking must favor task-oriented narrative pages before generated API signatures for broad
queries, while exact public symbols and diagnostic codes remain discoverable. Search excerpts are
derived from normalized source text and rendered as text; query terms never become trusted HTML.

Initial limits, ranking fixtures, and latency budgets are frozen in the acceptance plan before
production cutover. Empty, oversized, Unicode, markup-looking, and adversarial queries receive
explicit behavior.

### API reference

Existing `:::` directives are compiled through an allowlisted importer that resolves public
symbols from declared workspace packages. It must not evaluate expressions, execute examples, or
walk private modules based on request input.

The generated Hedron reference surface preserves the useful current contract: public name,
qualified name, signature, summary, parameter and return documentation, documented exceptions,
stability/maturity metadata where available, and a source link when configured. Import failures and
missing symbols are compile errors under strict CI.

API extraction remains build-time. A production request never imports a symbol selected by the
client.

### Live examples and feature showcase

The application includes an explicit demo registry. Each identifier binds a documented embed to a
known Hedron page, component, action, or static example. Initial showcase coverage should include:

- component composition and theme/color-mode behavior;
- a typed form with validation and a no-script submission path;
- an HTMX fragment update with correct focus and status behavior;
- a typed action/refresh workflow;
- a chart and map with accessible non-visual content;
- loading, empty, error, and success states; and
- an inspectable example whose source is synchronized with the displayed code.

Public demos are request-scoped or carry bounded, integrity-protected client state. They do not
write shared process memory, the repository, a database, or an external service. They do not accept
arbitrary imports, templates, URLs, files, code, or component names. Destructive, authentication,
upload, remote-data, and background-job examples use inert fixtures or a clearly isolated
deployment approved by a separate threat review.

`hedron-sim` may remain useful for documentation that must be static or deterministic, but a page
must label a simulation and must not present it as a live backend. The flagship feature path should
prefer real bounded Hedron interactions.

### Metadata, versions, and public URLs

The production domain should be provider-neutral, provisionally `docs.hedron.dev`; the exact domain
is an open decision. The FastAPI Cloud hostname is a preview and fallback, not the long-term URL in
package metadata.

The manifest must render canonical links, Open Graph basics, robots policy, a sitemap, edit/source
links, and correct status codes. Public paths and anchors from the current stable site are captured
before migration. Each receives one disposition: preserved, redirected, intentionally retired with
a replacement, or excluded because it was never public.

The first cutover may serve only the current stable documentation at the canonical root if older
versions remain available on Read the Docs and are linked clearly. Removing historical version
access is not implicit. A later multi-version design must use immutable manifests and explicit
version routes; it must not dynamically check out repository revisions inside the server.

### Deployment and operations

Preview deployments use FastAPI Cloud without changing public DNS. Production deployment is
automated from a protected, tested revision using either the native GitHub integration or a scoped
deploy-token workflow. Because native repository integration currently deploys only the default
branch and does not provide pull-request previews, branch preview policy must be selected
explicitly rather than assumed.

Required operational behavior includes:

- local and CI startup using the same application entrypoint;
- build/compile failure before a broken manifest becomes healthy;
- zero secrets in the content manifest, rendered pages, search index, logs, or client assets;
- structured request, compile, search, and demo diagnostics without query-value leakage;
- immutable cache headers for fingerprinted assets and safe policy for HTML/fragment responses;
- readiness and liveness behavior compatible with multiple instances and scale-to-zero;
- a documented deploy, smoke, observe, and rollback runbook; and
- retained Read the Docs production fallback through the acceptance window.

## Alternatives considered

### Serve the existing MkDocs build through FastAPI

This is the smallest hosting migration and remains a useful infrastructure probe, but it does not
make the docs a Hedron application or exercise Hedron's authoring and interaction surface. Rejected
as the target; permitted only as a temporary deployment diagnostic.

### Wrap rendered Markdown in `hedron.content.Markdown`

This keeps a Hedron page shell but turns the document body into one sanitized HTML blob and loses
current extensions. It does not meet the native-component dogfooding goal. Rejected as the general
lowering strategy; a bounded compatibility node may be inventoried for rare constructs.

### Rewrite every document as Python component code

This maximizes component use but makes prose editing, GitHub reading, external contributions, and
large-scale maintenance substantially worse. Rejected. Python remains appropriate for live demos
and generated component definitions, not ordinary prose.

### Publish a stable generic documentation framework before the site

The reusable boundary is not yet evidenced. Promising a stable, broadly compatible framework would
risk encoding Hedron's site policy as permanent API. Rejected. The selected approach uses an
experimental `hedron-docs` package with one first-party proving consumer; stability and broader
compatibility require later evidence and a separate decision.

### Name the package `hedron-mkdocs`

That name conventionally implies an MkDocs plugin, theme, or runtime integration. The selected
architecture replaces MkDocs at runtime and uses it only through a bounded migration adapter and
parity oracle. Rejected for the compiler package. The name remains available for a future dedicated
MkDocs integration if one is independently justified.

### Keep Read the Docs permanently

This is operationally mature and remains the rollback option, but it cannot satisfy the goal of a
production Hedron application demonstrating Hedron. Rejected as the long-term primary host.

### Use a client-side documentation framework

This would add a frontend build/runtime authority and weaken the server-rendered Hedron proof.
Rejected. Small progressive client enhancements remain allowed through Hedron's existing asset and
web-component contracts.

## Security implications

The trusted boundary is repository-reviewed documentation at a pinned deployment revision. Content
is still treated as structured input during compilation:

- source and asset paths are jailed beneath declared roots after symlink resolution;
- Markdown raw HTML, URLs, API directives, and demo directives are deny-by-default;
- internal links and route names are normalized and collision checked;
- API imports use a static allowlist and run only during compilation;
- live demos expose fixed handlers with request, field, byte, time, and response budgets;
- search terms remain untrusted text and are never interpolated into raw HTML, selectors, logs, or
  filesystem paths;
- public production uses a strict security profile and an explicit CSP-compatible asset path;
- public docs do not expose Explorer, development diagnostics, filesystem details, source roots, or
  secret environment values; and
- compilation, rendering, and live-demo adversarial corpora cover XSS, URL confusion, path
  traversal, directive injection, oversized input, expensive nesting, and error redaction.

Content authors are trusted maintainers, but a compromised pull request must still be reviewable;
the compiler may not turn an innocent-looking Markdown construct into arbitrary code execution or
an unbounded remote fetch.

## Accessibility implications

The site must preserve or improve the current documentation quality bar:

- semantic landmarks, heading order, lists, tables, code, quotations, and alerts;
- a skip link and visible keyboard focus;
- keyboard-operable responsive navigation, content tabs, search, theme selection, and demos;
- correct focus and status announcements after HTMX swaps;
- stable fragment navigation and visible target headings;
- non-color state, forced-colors behavior, reduced motion, zoom/reflow, text spacing, and narrow
  viewport support;
- meaningful chart/map alternatives and no interaction that requires pointer precision;
- a useful 404 page and understandable compile-time errors for authors; and
- print output that retains document content, link destinations, code, tables, and warnings while
  omitting nonessential interactive chrome.

Automated axe checks are required but do not replace the project's honest human-assistive-
technology disposition. The migration must not claim that outstanding project-wide human AT gates
have been completed.

## Performance implications

Production requests must not parse the corpus, import documentation targets, build the search
index, or read arbitrary source files. Those operations occur before readiness and produce an
immutable in-memory/on-disk manifest.

The acceptance plan baselines and freezes budgets for:

- compile time and peak memory over the complete public corpus;
- application startup and cold response behavior;
- warm page and search latency;
- initial compressed HTML, CSS, JavaScript, font, and image transfer;
- route/search index size and resident memory;
- repeated HTMX navigation without asset duplication or listener leaks; and
- large tables, code blocks, API pages, and live demos at desktop and narrow widths.

There is no mandatory database, remote search request, client-side SPA bundle, or runtime syntax
highlighter on the Supported path. Static assets use content fingerprints and CDN-compatible cache
headers. HTML remains complete enough for direct navigation and no-script use.

## Testing strategy

### Compiler and manifest

- Golden AST and Hedron-render tests for every admitted Markdown construct.
- Clean wheel installation and public-import smoke tests for the experimental `hedron-docs`
  package.
- Source-location diagnostics for malformed and unsupported syntax.
- Determinism checks across two clean compilations.
- Route, anchor, navigation, asset, API-symbol, and demo-reference collision checks.
- Adversarial path, URL, raw HTML, directive, and size/depth corpora.

### Application

- FastAPI/Hedron request tests for every route class, status, headers, canonical metadata, and
  ordinary-form fallback.
- Typed search ranking fixtures and hostile-query tests.
- Live-demo tests proving declared effects, bounded state, CSRF behavior where applicable, and
  absence of shared mutable state.
- Production-mode startup, health, redaction, CSP, and multiple-instance tests.

### Browser and accessibility

- Chromium, Firefox, and WebKit coverage for the home page, quickstart, long guide, API reference,
  component page, search, live examples, and 404.
- Desktop/narrow, light/dark/system, forced-colors, reduced-motion, zoom/reflow, keyboard, history,
  fragment, print, and no-JavaScript checks.
- Axe evidence plus the existing human-AT honesty boundary.

### Migration and deployment

- Current MkDocs route and anchor snapshot.
- Link, redirect, canonical, sitemap, source/edit-link, and search-query parity fixtures.
- Clean uv workspace install and `fastapi dev` startup from the selected application directory.
- FastAPI Cloud preview smoke tests before DNS changes.
- Production-domain smoke, observation, and rollback drills.

## Compatibility and migration

The Markdown corpus and documentation ownership config remain canonical during migration. The
compiler initially consumes a normalized import of the current navigation and exclusion policy so
that a renderer rewrite does not also become an information-architecture rewrite. The checked-in
native authority becomes `hedron-docs.toml`; `mkdocs.yml` remains the parity oracle and fallback
input until cutover. Replacing it requires a reviewed migration and parity check.

Existing public routes, anchors, package metadata links, README links, badges, edit links, and
external references are inventoried before cutover. The provider-neutral canonical domain is added
before broad link replacement. Read the Docs remains available for historical versions and
rollback until the retention decision is accepted and verified.

Public Hedron APIs are not created merely because the package or docs app has a helper. Likewise,
an experimental `hedron-docs` helper becomes a supported package API only after it is generic,
independently tested, documented, and assigned to an accepted compatibility/stability contract.

## Open questions

1. Which release phase, if any, owns the initiative and any generic Hedron changes?
2. Is `docs.hedron.dev` available and should it be the canonical domain?
3. Which Markdown parser provides source-located AST coverage while preserving the pure-Python
   Supported installation?
4. Which current MkDocs extensions are Required for first cutover, and which can receive an
   explicit compatibility-node or Deferred disposition?
5. Does the first production release serve only current stable docs, or must it also serve an
   immutable development channel?
6. How long must Read the Docs remain active, and can its project serve redirects or a migration
   banner for provider-owned historical URLs?
7. Which live demos are safe enough for the first public deployment?
8. Should the public deployment expose any authenticated Explorer surface, or should Explorer
   evidence remain CI/local only?
9. What evidence is required before `hedron-docs` can publish beyond an experimental `0.x` line?
10. Should native GitHub deployment or a deploy-token workflow own production promotion and branch
    previews?
11. Which measured cold-start, warm-latency, and asset budgets become release blockers after the
    baseline prototype?

## Acceptance criteria

This RFC may move from Draft to Accepted only when:

- roadmap ownership or an explicitly cross-cutting disposition is recorded;
- the experimental `hedron-docs` distribution/import/command names, native configuration schema,
  bounded MkDocs adapter, candidate public API, and maturity claim are frozen;
- the source syntax inventory has a Required/compatibility/Deferred disposition for every current
  public construct;
- the parser, manifest schema, native lowering boundary, route policy, and canonical domain policy
  are frozen;
- live-demo trust boundaries and the first allowlisted demo inventory are reviewed;
- initial performance baselines refine the provisional budgets;
- the production deployment and rollback owner is named; and
- all open questions that alter public compatibility or security are closed.

Production cutover additionally requires every gate in
[`HEDRON_NATIVE_DOCS_CUTOVER`](../acceptance/HEDRON_NATIVE_DOCS_CUTOVER.md) to be Verified, a
successful rollback drill, and an explicit maintainer go/no-go decision. A successful preview alone
does not authorize DNS changes or removal of Read the Docs.
