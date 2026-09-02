---
description: Build production-minded, server-rendered Python interfaces on FastAPI with Hedron.
hide:
  - toc
search:
  boost: 2
---

<div class="docs-home" markdown>

<header class="docs-home__hero" markdown>

<div class="docs-home__hero-copy" markdown>

<span class="docs-home__eyebrow">Python UI, without the black box</span>

<img class="hedron-theme-wordmark" src="assets/hedron-logo-hero.svg" alt="Hedron">

# Build clear, durable interfaces in Python.

[Hedron](guides/why-hedron.md) gives FastAPI applications a server-rendered UI layer.
Compose views in Python, keep ordinary HTTP underneath, and add rich interaction only
where it earns its place.

<div class="docs-home__actions">
  <a class="md-button md-button--primary" href="getting-started/installation/">Get started <span aria-hidden="true">→</span></a>
  <a class="md-button" href="guides/why-hedron/">Why Hedron?</a>
</div>

<div class="docs-home__signals" aria-label="Key project qualities">
  <span>FastAPI native</span>
  <span>Server rendered</span>
  <span>Progressively enhanced</span>
</div>

</div>

<aside class="docs-home__quickstart" aria-label="Quick install">
  <div class="docs-home__quickstart-bar">
    <span aria-hidden="true"></span><span aria-hidden="true"></span><span aria-hidden="true"></span>
    <strong>quickstart.py</strong>
  </div>
  <div class="docs-home__quickstart-body">
    <span class="docs-home__quickstart-label">01 · Install</span>
    <code><span class="prompt">$</span> pip install hedron</code>
    <span class="docs-home__quickstart-label">02 · Compose</span>
    <pre><code><span class="kw">from</span> hedron <span class="kw">import</span> Page, Text

page = Page(
    Text(<span class="str">"Hello, Hedron."</span>)
)</code></pre>
    <a href="getting-started/quickstart/">Build your first app <span aria-hidden="true">↗</span></a>
  </div>
</aside>

</header>

<div class="docs-home__section-heading" markdown>

## Choose your starting point

<p>Follow the shortest path to the thing you want to build.</p>

</div>

<div class="docs-home__featured">
  <a class="docs-home-card docs-home-card--start" href="getting-started/installation/">
    <span class="docs-home-card__icon" aria-hidden="true">00</span>
    <strong>Start a new project</strong>
    <span>Install Hedron, scaffold an app, and render your first page.</span>
  </a>
  <a class="docs-home-card docs-home-card--fastapi" href="guides/plain-fastapi/">
    <span class="docs-home-card__icon" aria-hidden="true">01</span>
    <strong>Add Hedron to FastAPI</strong>
    <span>Keep your routes, dependencies, middleware, lifespan, and OpenAPI.</span>
  </a>
  <a class="docs-home-card docs-home-card--reference" href="api/by-task/">
    <span class="docs-home-card__icon" aria-hidden="true">10</span>
    <strong>Find an API by task</strong>
    <span>Find the right component, route, action, or helper by task.</span>
  </a>
  <a class="docs-home-card docs-home-card--examples" href="examples/recipes/">
    <span class="docs-home-card__icon" aria-hidden="true">11</span>
    <strong>Work from a recipe</strong>
    <span>Use focused patterns for common UI and application workflows.</span>
  </a>
</div>

<div class="docs-home__section-heading" markdown>

## Browse by goal

<p>The documentation follows the way a real project moves from idea to production.</p>

</div>

<div class="docs-home__routes">
  <a class="docs-route" href="getting-started/">
    <span class="docs-route__icon docs-route__icon--start" aria-hidden="true">00</span>
    <span>
      <strong>Learn the model</strong>
      Understand pages, views, actions, components, and the request lifecycle.
    </span>
  </a>
  <a class="docs-route" href="guides/">
    <span class="docs-route__icon docs-route__icon--build" aria-hidden="true">01</span>
    <span>
      <strong>Build an interface</strong>
      Add forms, interactions, data, visuals, authentication, and reusable components.
    </span>
  </a>
  <a class="docs-route" href="guides/ship/">
    <span class="docs-route__icon docs-route__icon--operate" aria-hidden="true">10</span>
    <span>
      <strong>Prepare for production</strong>
      Deploy, test, observe, secure, and scale a production Hedron application.
    </span>
  </a>
  <a class="docs-route" href="api/by-task/">
    <span class="docs-route__icon docs-route__icon--reference" aria-hidden="true">11</span>
    <span>
      <strong>Look something up</strong>
      Look up public APIs, components, configuration, compatibility, and packages.
    </span>
  </a>
</div>

<div class="docs-home__section-heading" markdown>

## Current in Hedron

<p>Release status, major changes, and practical migration guidance.</p>

</div>

<div class="docs-home__updates">
  <a href="guides/current-release/">
    <span>Stable release</span>
    <strong>Hedron 1.0.5 is available</strong>
    <p>Review supported versions, install pins, and package maturity.</p>
  </a>
  <a href="guides/whats-new-1.0/">
    <span>Hedron 1.0</span>
    <strong>One canonical authoring model</strong>
    <p>Pages, views, and actions now define the stable application model.</p>
  </a>
  <a href="guides/streamlit-migration/">
    <span>Migration guide</span>
    <strong>Moving beyond Streamlit</strong>
    <p>Translate reruns and session state into explicit routes and interactions.</p>
  </a>
</div>

<aside class="docs-home__help" markdown>

## Need a hand?

Start with the [FAQ](guides/faq.md) or [troubleshooting guide](guides/troubleshooting.md).
For bugs and documentation gaps, see [support](guides/support.md) and open a reproducible
issue on [GitHub](https://github.com/eddiethedean/hedron/issues).

</aside>

</div>
