# Hedron-native documentation acceptance and cutover plan

**Status:** Draft / no production change authorized

**Owning proposal:**
[`RFC-0088`](../rfcs/RFC-0088-HEDRON-NATIVE-DOCUMENTATION.md)

**Implementation plan:**
[`HEDRON_NATIVE_DOCUMENTATION`](../implementation/HEDRON_NATIVE_DOCUMENTATION.md)

## Purpose

Define the evidence required to replace the Read the Docs/MkDocs Material public site with the
Hedron-native FastAPI Cloud application. This document is both an acceptance specification and the
outline of the production runbook. It does not authorize a deployment, custom-domain attachment,
DNS edit, redirect, or retirement of the existing site.

Every gate begins **Planned**. A gate becomes **Verified** only when its evidence is attached or
linked from a future tracking ledger. **Deferred** is not sufficient for production cutover unless
this plan explicitly marks the capability optional and records an accepted fallback.

## Release decision model

There are four independent decisions:

1. **Prototype:** may a non-canonical preview be deployed?
2. **Migration:** may the full public corpus be migrated and kept in parity?
3. **Cutover:** may the canonical domain move to the Hedron application?
4. **Retirement:** may the Read the Docs fallback or historical content be removed?

Passing an earlier decision never implies a later one. Retirement occurs only after the observation
and rollback windows and a separate retention decision.

## Gate index

| Gate | Requirement | Evidence | Cutover blocker |
|---|---|---|---|
| `BASELINE-DOCS` | Current public routes, anchors, nav, syntax, assets, generated pages, search fixtures, and custom behavior captured | machine-readable inventories + baseline report | Yes |
| `APP-DOCS` | Locked workspace install, explicit entrypoint, production Hedron skeleton, health/readiness, no database | clean install/start/smoke logs | Yes |
| `COMPILER-DOCS` | Source-located typed AST, native lowering, deterministic manifest, strict diagnostics | compiler tests + repeat-build hash | Yes |
| `SYNTAX-DOCS` | Every public Markdown construct has Required, compatibility, migrated, or accepted Deferred disposition | syntax inventory with zero unknown rows | Yes |
| `ROUTES-DOCS` | Public route, slash, anchor, redirect, canonical, edit/source, and status behavior preserved | old/new route and anchor diff | Yes |
| `SHELL-DOCS` | Hedron-native responsive shell, nav, TOC, breadcrumbs, themes, release banner, 404 | browser/visual evidence | Yes |
| `SEARCH-DOCS` | Typed search meets relevance, fallback, security, latency, and accessibility contract | frozen query corpus + measurements | Yes |
| `API-DOCS` | All admitted API directives compile through the allowlisted build-time path | API directive inventory + strict build | Yes |
| `DEMO-DOCS` | First live-demo inventory is explicit, bounded, accessible, and free of shared state/arbitrary execution | demo threat/test matrix | Yes |
| `AUTHOR-DOCS` | Maintainer preview, narrow checks, full strict checks, generated ownership, and contributor guidance work | docs-only CI logs + guidance review | Yes |
| `SECURITY-DOCS` | Path/URL/content/directive/search/demo adversarial tests, CSP, headers, redaction, budgets | security report + test logs | Yes |
| `A11Y-DOCS` | Semantic/no-JS/keyboard/focus/history/fragment/preferences/zoom/print matrix passes with honest AT scope | three-engine browser and axe packet | Yes |
| `PERF-DOCS` | Compile, startup, warm/cold, search, transfer, memory, cache, and repeated-nav budgets pass | benchmark and deploy observations | Yes |
| `OPS-DOCS` | Deployment protection, credentials, logging, cache, multiple-instance behavior, alerts, owner, and runbook ready | operations review + drill | Yes |
| `PREVIEW-DOCS` | Full candidate runs at non-canonical FastAPI Cloud hostname and passes production smoke | immutable deployment ID + smoke log | Yes |
| `DOMAIN-DOCS` | Provider-neutral domain, DNS/TLS records, canonical policy, and package-link change set approved | domain checklist + reviewed diff | Yes |
| `ROLLBACK-DOCS` | Existing site retained; DNS/app/content rollback rehearsed within the target recovery window | timed drill log | Yes |
| `GO-DOCS` | Named maintainer reviews all evidence and records go/no-go | signed decision record | Yes |
| `OBSERVE-DOCS` | Post-cutover observation window closes without rollback thresholds | observation log | Retirement only |
| `RETIRE-DOCS` | Historical-version and old-host retention decision implemented without broken promises | retention decision + external link audit | Retirement only |

## Required baseline inventories

Before implementation claims parity, capture:

- the strict MkDocs output path and HTTP-status expectations;
- every heading ID and inbound fragment referenced inside the repository;
- navigation labels, hierarchy, ordering, hidden-but-published pages, and exclusions;
- metadata, canonical URL, description, edit/source link, sitemap, robots, and 404 behavior;
- Markdown extensions and option forms, raw HTML, attribute syntax, API directives, diagrams,
  generated pages, simulations, custom hooks, JavaScript, CSS, and template overrides;
- representative search queries with expected result classes and important top results;
- public assets, MIME types, references, and large-file warnings;
- current desktop/narrow/light/dark/print screenshots for the vertical-slice pages;
- current compile, transfer, search, and page-load measurements; and
- all provider-bound URLs in README files, package metadata, docs, badges, and generated output.

Inventories must distinguish the public site from the maintainer corpus. File count alone is not a
parity metric.

## Acceptance matrices

### Page archetypes

Every row must pass route, content, metadata, search, no-JS, keyboard, responsive, theme, print,
security-header, and performance checks unless a cell is explicitly not applicable with a reason.

| Archetype | Required candidate |
|---|---|
| Landing | Home |
| Tutorial | Quickstart / first app |
| Long how-to | Styling or interaction guide with deep headings |
| Reference narrative | One task-oriented API page |
| Generated API | `AUTODOC` subset with signatures and source links |
| Generated component | One page with demo, code, and parameter/reference content |
| Data-heavy | Wide table and long code sample |
| Interactive | Form + fragment/action demo |
| Visualization | Chart and map with accessible alternatives |
| Search | empty, populated, no-result, exact symbol, diagnostic code |
| Failure | unknown route, bad fragment, invalid/oversized search |

### Browser and preference matrix

| Dimension | Required values |
|---|---|
| Engine | pinned Chromium, Firefox, WebKit |
| Width | desktop and narrow mobile fixture |
| Color mode | light, dark, system |
| Input | keyboard-only and pointer |
| Enhancement | JavaScript/HTMX enabled and JavaScript disabled |
| Preferences | reduced motion and forced colors; contrast/transparency where supported |
| Text/layout | 200% zoom, reflow, text spacing, long unbroken content |
| Navigation | direct load, back/forward, HTMX path, fragment link, copied URL |
| Output | screen and print/PDF fixture |

The matrix verifies visible focus, skip link, semantic landmarks, heading order, current navigation,
tab behavior, search status, swap focus, error recovery, code/table overflow, and absence of hidden
content traps.

### Search relevance fixtures

The frozen corpus must include at least:

- beginner intent: install, first app, form submission, deployment;
- conceptual intent: HTMX, state, security, theming;
- task intent: authentication, charts, maps, testing, troubleshooting;
- exact symbol: `Hedron`, `Page`, `ActionHandle`, and one satellite symbol;
- exact diagnostic code and exception name;
- punctuation, case, Unicode, partial word, empty query, no match, and oversized query; and
- markup-looking and script-looking hostile input.

Broad queries should rank narrative task pages ahead of generated signatures; exact symbols and
diagnostic codes should remain directly discoverable. Expected results are relevance classes and
important top candidates, not an overfit total ordering of every result.

### Live-demo inventory

Every public live demo records:

| Field | Required fact |
|---|---|
| Identifier | stable explicit registry key |
| Purpose | Hedron capability demonstrated |
| Routes/methods | complete bounded route family |
| Inputs | types, lengths, bytes, content types, allowed values |
| Effects | declared updates/refreshes and absence of hidden side effects |
| State | request-scoped or integrity-protected; no shared mutable process state |
| Security | CSRF/auth/egress/file policy and why each is applicable |
| Accessibility | keyboard, status, focus, alternative content, fallback |
| Performance | time, output, concurrency, and asset budgets |
| Failure | validation, timeout, internal error, and redaction behavior |
| Source sync | owning source file and displayed-code check |

No live demo may import or execute a name supplied by the visitor.

## Provisional performance gates

These values are frozen or revised after baseline evidence and before `PERF-DOCS` can be Verified:

- production requests perform zero Markdown parsing and zero documentation-target imports;
- document rendering and search require zero database or remote-service requests;
- two clean full-corpus compiles produce byte-identical manifests;
- warm document-render p95 target is at most 150 ms in the reference benchmark;
- warm search p95 target is at most 100 ms over the frozen query corpus;
- first-party compressed transfer does not regress more than 10% from the agreed current-site
  baseline without an accepted, itemized reason;
- repeated enhanced navigation does not duplicate global assets or event listeners;
- search index and manifest memory remain measured and bounded per public document; and
- FastAPI Cloud cold-start time is reported separately from Hedron render time and receives an
  operational threshold after preview measurement.

Performance evidence reports hardware/runtime/provider context. It must not attribute provider
cold starts or CDN behavior to Hedron.

## Security acceptance corpus

Required cases include:

- source and asset `..`, absolute, symlink, encoded, Unicode-confusable, and separator traversal;
- duplicate/case-conflicting routes and anchors;
- script/event/style/raw-HTML payloads in every Markdown position;
- dangerous and protocol-relative URLs, data URLs, remote assets, and malformed encodings;
- API directive expressions, private names, wildcard/module walks, import failures, and expensive
  objects;
- unknown demo IDs, route confusion, method confusion, CSRF cases, oversized bodies, and repeated
  concurrency;
- search control characters, markup, bidi text, long Unicode, log injection, and expensive token
  patterns;
- compiler recursion, nesting, node, table, code, directive, source-byte, and output-byte limits;
- error redaction for paths, environment, tokens, cookies, query values, and stack traces; and
- production CSP/headers with no inline-script exception added merely for documentation.

## Pre-cutover checklist

- [ ] RFC accepted and owner/tracking recorded.
- [ ] All gates through `PREVIEW-DOCS` are Verified.
- [ ] Candidate deployment is pinned to a reviewed commit and immutable deployment ID.
- [ ] Public route/anchor/link/canonical diff has zero unclassified rows.
- [ ] Search relevance and all page/browser matrices pass against the candidate.
- [ ] FastAPI Cloud logs and health are visible to the named operator.
- [ ] Custom domain is added; exact DNS records and current TTL are captured.
- [ ] TLS issuance/renewal path and DNS-provider requirements are understood.
- [ ] Existing Read the Docs build is green and its last known-good revision is recorded.
- [ ] Rollback deployment and DNS values are recorded without unresolved variables or globs.
- [ ] Package metadata/README/badge/link update is prepared but not merged prematurely.
- [ ] Communication and observation owners are available for the cutover window.
- [ ] `ROLLBACK-DOCS` timed drill passes.
- [ ] `GO-DOCS` decision explicitly authorizes the production-domain change.

## Cutover runbook outline

Exact provider commands and DNS values are filled only after the domain is known. Do not place
tokens or reusable credentials in this document or its evidence.

1. Freeze documentation-affecting merges for the cutover window.
2. Re-run strict corpus, route/anchor, link, compiler, browser, security, accessibility, and
   performance checks on the candidate commit.
3. Deploy that exact commit to the production FastAPI Cloud app.
4. Record deployment ID, build logs, health, canonical headers, asset headers, and smoke results on
   the FastAPI Cloud hostname.
5. Confirm the existing Read the Docs site remains healthy and unchanged.
6. Lower DNS TTL in advance if the approved DNS plan requires it.
7. Apply only the exact reviewed FastAPI Cloud domain records.
8. Wait for provider verification and TLS readiness before advertising the domain.
9. Run canonical-domain smoke checks for home, quickstart, API, component, search, demo, 404,
   sitemap, robots, assets, fragments, and no-JS navigation.
10. Merge/activate provider-neutral package metadata, README, badge, sitemap, and canonical links.
11. Observe logs, status codes, latency, search failures, asset failures, and external-link checks
    through the defined window.
12. Roll back immediately when a threshold below is met; otherwise close `OBSERVE-DOCS` after the
    approved window.

## Rollback triggers

Rollback is mandatory when any of these persists beyond the short diagnosis interval selected in
the final runbook:

- TLS or canonical domain is unavailable or invalid;
- health/readiness fails or deployments repeatedly restart;
- common public routes, anchors, assets, search, or 404 return incorrect status/content;
- security headers/CSP differ from the reviewed candidate or sensitive details appear in output;
- error rate, cold/warm latency, or asset failures exceed the frozen threshold;
- keyboard/no-JS navigation or primary tutorial access is broken;
- a live demo permits cross-user state, unintended effects, unbounded work, or code/import control;
- redirects loop or high-value historical links cannot reach an intended document; or
- the operator cannot see enough logs/health information to distinguish a working deployment from
  a failing one.

Rollback means restoring the prior reviewed DNS/application state, confirming the Read the Docs
site, reverting provider-neutral link activation if necessary, and recording the incident. It does
not mean deleting the candidate deployment or evidence during diagnosis.

## Observation and retirement

The final plan sets an observation window based on traffic and DNS behavior; it must include at
least one normal documentation release/update cycle. During that window:

- Read the Docs remains buildable and available as the recorded fallback;
- external and repository link checks include both new canonical links and important old URLs;
- error, latency, search, and asset observations are reviewed by a named maintainer; and
- content changes prove the new authoring and deployment loop, not only the initial build.

After `OBSERVE-DOCS` is Verified, a separate decision selects one of:

1. retain Read the Docs for historical versions and provider-owned legacy URLs;
2. retain a minimal migration/redirect project; or
3. retire it only after historical content and inbound links have another verified home.

No option allows silently breaking `hedron.readthedocs.io/en/latest/` links already published in
package metadata, released READMEs, external articles, or cached search results.

## Evidence record template

Future tracking may move this into TOML, but each gate record must contain:

```text
gate:
disposition: Planned | Verified | Deferred | Failed
owner:
candidate_commit:
environment:
commands:
artifacts:
measured_results:
known_limitations:
reviewed_by:
reviewed_at:
```

Planning prose, screenshots without a candidate revision, and a successful manual page load are not
sufficient production evidence.
