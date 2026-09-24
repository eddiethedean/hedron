---
description: Introduce Hedron to teams that know Streamlit, FastAPI, and Posit Workbench or Connect.
search:
  boost: 1.7
---

# Hedron for Streamlit and Posit teams

Hedron lets Python teams build server-rendered interfaces on FastAPI. A team can
develop one application in Posit Workbench and publish it as FastAPI content on
Posit Connect using the optional `hedron-posit` adapter. This section explains
the idea for managers, data specialists, software engineers, and platform teams.

[Download the 10-slide introduction](../../assets/hedron-introduction.pptx)
(PowerPoint, with presenter notes and cited sources). The pages below also work
as a standalone introduction.

## The core idea

A Hedron page is a Python function that returns components. FastAPI handles the
request, input validation, dependencies, and ordinary API routes. Hedron renders
HTML on the server. When a user refreshes a view or submits a form, the browser
sends a request to a named route; Hedron can return only the HTML region that
needs to change.

This model suits a dashboard that is becoming a maintained application: it needs
shareable URLs, validated inputs, explicit writes, access rules, and tests. It
does not require replacing Python data logic or operating a separate frontend
application. [How Hedron works](how-it-works.md) shows the request path and a
small example.

## What each audience should take away

- **Management and program owners:** Which maintained internal tool is worth
  piloting, and what would count as success?
- **Data scientists and visualization developers:** Which queries,
  calculations, and displays can remain in Python? Which interactions need
  redesign?
- **Data and software engineers:** Where do FastAPI routes, validated input,
  background work, and tests fit?
- **Platform and security teams:** How will Workbench and Connect host the app?
  Who owns authorization, secrets, and data controls?

## Follow the introduction

1. [How Hedron works](how-it-works.md) — pages, views, actions, and the difference
   from Streamlit's default execution model.
2. [Workbench and Connect](workbench-connect.md) — develop behind the Workbench
   proxy, then publish one application object as FastAPI content.
3. [Migration pilot](migration-pilot.md) — choose a candidate, preserve domain
   code, compare user outcomes, and assign security responsibilities.

For the complete implementation guides, continue to
[Migrate a Streamlit app](../../guides/streamlit-migration.md) and
[Posit deployments](../../guides/posit.md). Check the
[current compatibility matrix](../../COMPATIBILITY.md) against your installed
Workbench and Connect versions before a deployment decision.
