# What is HTMX (for Hedron)

[HTMX](https://htmx.org) is a small browser library that issues HTTP requests from HTML
attributes (`hx-get`, `hx-post`, `hx-target`, …) and swaps the response HTML into a
page region — without writing a SPA or a Node build.

## Why Hedron uses it

Hedron is **server-rendered Python**. Routes return typed components that serialize to
HTML. For partial updates, Hedron returns a **fragment** (region HTML only). HTMX
performs the swap in the browser.

```text
Click RefreshButton
  → browser GET /status with HX-Request + HX-Target
  → Hedron returns only #service-status HTML
  → HTMX replaces that region
```

You do not ship a React/Vue app. You declare fragment regions in Python; HTMX is the
transport for those swaps. Hedron bundles HTMX under `/hedron-static/` so apps do not
need npm.

## What you need to know on day one

| Idea | Hedron term |
|---|---|
| Named place on the page that can be replaced | `app.region(...)` / `FragmentRegion` |
| Endpoint that returns region HTML | `@app.fragment` / fragment response via `swap(...)` |
| Control that issues `hx-get` to a region | `RefreshButton.for_region(...)` |
| Wrong target id | HTTP **403** (allowlist fail-closed) |

Classic full-page form POST (no `hx-*`) still works — see
[Minimal form POST](../guides/minimal-form.md). HTMX is for in-place updates; it is not
required for every page.

## What HTMX is not (in Hedron)

- Not a client-side component framework
- Not a replacement for your auth, ORM, or deployment
- Not the Supported path for pushing live updates — prefer **polling** for job status;
  SSE/WebSocket helpers are FastAPI-flagship and **experimental**

## Next

1. [Build your first app](quickstart.md) — Hello + **Refresh status**
2. [HTMX interactions](../guides/htmx-interactions.md) — second region on the same app
3. [Minimal form POST](../guides/minimal-form.md) — CSRF POST that updates the notes count
