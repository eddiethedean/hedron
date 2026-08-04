# Guides

Task-oriented guidance for moving from a working page to a maintainable Hedron project.

<div class="hedron-grid">
  <a class="hedron-card" href="component-composition/">
    <span class="hedron-card__icon" aria-hidden="true">⧉</span>
    <strong>Component composition</strong>
    <p>Shared children/id/class_ contracts, nested FormField a11y, and layout gaps.</p>
  </a>
  <a class="hedron-card" href="best-practices/">
    <span class="hedron-card__icon" aria-hidden="true">★</span>
    <strong>Best practices</strong>
    <p>Pages vs fragments, CSRF, SafeUrl, secrets, and OOB regions.</p>
  </a>
  <a class="hedron-card" href="../api/JINJA/">
    <span class="hedron-card__icon" aria-hidden="true">{ }</span>
    <strong>HDJ authoring</strong>
    <p>Native HTML, CSS, JavaScript, Jinja, and HTMX with typed Hedron bridges.</p>
  </a>
  <a class="hedron-card" href="plugin-authoring/">
    <span class="hedron-card__icon" aria-hidden="true">⬡</span>
    <strong>Plugin authoring</strong>
    <p>Entry points, PLUGIN_META, version gates, and testing.</p>
  </a>
  <a class="hedron-card" href="project-workflow/">
    <span class="hedron-card__icon" aria-hidden="true">↗</span>
    <strong>Project workflow</strong>
    <p>Scaffold, develop, inspect, check, and create a sealed production build.</p>
  </a>
  <a class="hedron-card" href="streamlit-migration/">
    <span class="hedron-card__icon" aria-hidden="true">⇥</span>
    <strong>Migrate from Streamlit</strong>
    <p>Rewrite a rerun-based dashboard as typed routes, forms, metrics, charts, and tables.</p>
  </a>
  <a class="hedron-card" href="charts-and-htmx/">
    <span class="hedron-card__icon" aria-hidden="true">⌀</span>
    <strong>Charts and HTMX</strong>
    <p>Install charts, render LineChart, Markdown, and typed InteractionResult fragments.</p>
  </a>
  <a class="hedron-card" href="htmx-interactions/">
    <span class="hedron-card__icon" aria-hidden="true">⇄</span>
    <strong>HTMX interactions</strong>
    <p>Refresh a declared region, return a typed fragment, inspect headers, and test the boundary.</p>
  </a>
  <a class="hedron-card" href="live-interaction/">
    <span class="hedron-card__icon" aria-hidden="true">◉</span>
    <strong>Live interaction</strong>
    <p>SSE, focused streaming, WebSocket channels, Chat/Dialog, and opt-in preload (0.10).</p>
  </a>
  <a class="hedron-card" href="whats-new-0.10/">
    <span class="hedron-card__icon" aria-hidden="true">✦</span>
    <strong>What's new in 0.10</strong>
    <p>Release highlights, Deferred gaps, and upgrade path from 0.8/0.9.</p>
  </a>
  <a class="hedron-card" href="testing/">
    <span class="hedron-card__icon" aria-hidden="true">✓</span>
    <strong>Test your UI</strong>
    <p>Render components directly, exercise HTMX fragments, and keep snapshots stable.</p>
  </a>
  <a class="hedron-card" href="security/">
    <span class="hedron-card__icon" aria-hidden="true">◇</span>
    <strong>Security</strong>
    <p>Profiles, CSRF, CSP, redirects, and Explorer modes.</p>
  </a>
  <a class="hedron-card" href="support/">
    <span class="hedron-card__icon" aria-hidden="true">✉</span>
    <strong>Support</strong>
    <p>Where to ask, Beta expectations, and security disclosure.</p>
  </a>
  <a class="hedron-card" href="deployment/">
    <span class="hedron-card__icon" aria-hidden="true">⇪</span>
    <strong>Deployment</strong>
    <p>Production env, build manifests, assets, and uvicorn.</p>
  </a>
  <a class="hedron-card" href="upgrade/">
    <span class="hedron-card__icon" aria-hidden="true">↑</span>
    <strong>Upgrade</strong>
    <p>0.8 → 0.9 HDJ authoring break, then 0.10 live interaction notes.</p>
  </a>
  <a class="hedron-card" href="faq/">
    <span class="hedron-card__icon" aria-hidden="true">?</span>
    <strong>FAQ</strong>
    <p>Short answers to common installer and adopter questions.</p>
  </a>
  <a class="hedron-card" href="troubleshooting/">
    <span class="hedron-card__icon" aria-hidden="true">!</span>
    <strong>Troubleshooting</strong>
    <p>Fix CSRF, Explorer, build, and import failures.</p>
  </a>
  <a class="hedron-card" href="https://github.com/eddiethedean/hedron/tree/main/examples/reference-app">
    <span class="hedron-card__icon" aria-hidden="true">{ }</span>
    <strong>Reference application</strong>
    <p>Clone and run the FastAPI reference app for a live, cumulative example.</p>
  </a>
</div>

Looking for callable APIs in this release? Start with [Shipped through 0.10](../api/README.md).
For your first server interaction, see [HTMX interactions](htmx-interactions.md); then add
visualization with [Charts and HTMX](charts-and-htmx.md).
Stability classifications live under [STABILITY.md](../api/STABILITY.md); Deferred contracts are
listed there and in the [upgrade guide](upgrade.md).
