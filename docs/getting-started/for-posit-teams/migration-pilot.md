---
description: Choose and evaluate one Streamlit-to-Hedron pilot on Posit.
search:
  boost: 1.5
---

# A Streamlit migration pilot

Choose one maintained internal dashboard or workflow that has a clear data
owner, useful filters, and a small write or review path. Build the Hedron
candidate alongside the current Streamlit app so users can compare the same
tasks before any cutover.

## Choose a candidate

Consider Hedron when stable URLs, validated filters, explicit writes, or
FastAPI routes matter to a maintained application. It also fits a team that can
own tests and publish on an approved ASGI platform.

Retain Streamlit for now when the work is a short-lived analysis, its
notebook-style rerun loop is the main benefit, or essential custom components
have no acceptable replacement. A team also needs an owner for deployment and
operations before moving to Hedron.

Hedron is not a call-for-call Streamlit compatibility layer. The
[migration guide](../../guides/streamlit-migration.md) gives a fuller fit check.

## Build and compare one workflow

1. Inventory the current app's pages, widgets, state, caches, writes, and
   external components. The [static migration assistant](../../guides/streamlit-migration.md#start-with-the-migration-assistant)
   can help without executing the Streamlit app.
2. Move reusable queries, calculations, models, and writes into ordinary Python
   services with no Streamlit imports.
3. Make one read-only Hedron page work. Put shareable filters in validated GET
   parameters; add an explicit POST action for a write.
4. Compare user outcomes and test page responses, validation, fragment updates,
   authorization, and failure behavior. Run both applications separately during
   acceptance and keep a rollback path.

The runnable [sales-dashboard migration](../../guides/streamlit-migration.md#worked-migration-sales-dashboard)
shows this progression. Use the [production cutover guide](../../guides/streamlit-cutover.md)
when the pilot becomes a deployment candidate.

## Assign the operating responsibilities

Hedron supplies HTML escaping, typed trust boundaries, CSRF profiles, declared
fragment targets, FastAPI routing, and diagnostics.

The application and organization own identity integration, authorization of
protected data and actions, storage, tenancy, transactions, audit retention,
secrets, network policy, monitoring, deployment, and approvals.

Workbench or Connect sign-in does not by itself authorize a Hedron action. A
government deployment still follows the organization's normal security and
platform review. See [Security](../../guides/security.md),
[Posit deployments](../../guides/posit.md), and
[What is ready today](../../guides/whats-ready.md) for the current boundaries.

## Pilot decision

Ask whether users can complete the same tasks, whether the team can explain
each state and write boundary, and whether platform staff can publish,
observe, and roll back the Connect content. Keep the Streamlit app available
until those outcomes and the organization's access requirements are verified.
