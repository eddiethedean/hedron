# How-to guides

Task-oriented guidance from a working page to a maintainable Hedron project.

**0.30 train** (**Published**; last **v0.30.0**): fastapi-workbench extraction — [What’s ready](whats-ready.md).

Complete **Learn** first ([Learning path](../getting-started/learning-path.md):
First app → HTMX → Minimal form). HTMX and minimal form live under **Learn** — this
section continues with forms depth, polling / experimental live transports, data,
security, and ops.

**Help:** [FAQ](faq.md) · [Troubleshooting](troubleshooting.md) · [Error codes](error-codes.md).

Evaluating adoption? Use the **Evaluate** tab
([What’s ready](whats-ready.md) · [Evaluate Hedron](evaluate.md)).

<div class="hedron-grid">
  <a class="hedron-card" href="streamlit-migration/">
    <span class="hedron-card__icon" aria-hidden="true">→</span>
    <strong>Coming from Streamlit</strong>
    <p>Fit check, worked conversion, execution/state guide, API matrix, and production cutover.</p>
  </a>
  <a class="hedron-card" href="../getting-started/">
    <span class="hedron-card__icon" aria-hidden="true">→</span>
    <strong>Golden path (Learn)</strong>
    <p>First app, HTMX region refresh, and minimal form POST.</p>
  </a>
  <a class="hedron-card" href="faq/">
    <span class="hedron-card__icon" aria-hidden="true">?</span>
    <strong>FAQ</strong>
    <p>Versions, PATH / CLI, maturity labels, extras, and hosts.</p>
  </a>
  <a class="hedron-card" href="troubleshooting/">
    <span class="hedron-card__icon" aria-hidden="true">!</span>
    <strong>Troubleshooting</strong>
    <p>CSRF, assets, Explorer, production manifests, and live transports.</p>
  </a>
  <a class="hedron-card" href="mutations/">
    <span class="hedron-card__icon" aria-hidden="true">⚡</span>
    <strong>Mutations</strong>
    <p>Choose @action vs @component POST for forms and HTMX.</p>
  </a>
  <a class="hedron-card" href="forms-and-actions/">
    <span class="hedron-card__icon" aria-hidden="true">▣</span>
    <strong>Forms and actions</strong>
    <p>POST, CSRF, validation fragments, and typed InteractionResult.</p>
  </a>
  <a class="hedron-card" href="authentication/">
    <span class="hedron-card__icon" aria-hidden="true">⚿</span>
    <strong>Authentication</strong>
    <p>Login, logout, and gate pages with FastAPI dependencies.</p>
  </a>
  <a class="hedron-card" href="live-interaction/">
    <span class="hedron-card__icon" aria-hidden="true">◉</span>
    <strong>Polling (and experimental live)</strong>
    <p>Prefer Poll for job status. SSE, streaming, WebSocket, and preload stay experimental on FastAPI.</p>
  </a>
  <a class="hedron-card" href="dashboards/">
    <span class="hedron-card__icon" aria-hidden="true">▦</span>
    <strong>Dashboards</strong>
    <p>InteractionGraph / DashboardBinding (0.17+) with polling-first honesty.</p>
  </a>
  <a class="hedron-card" href="model-demos/">
    <span class="hedron-card__icon" aria-hidden="true">◇</span>
    <strong>Model demos</strong>
    <p>InferenceInterface, ModelDemo, InferencePolicy, and workflows (0.18).</p>
  </a>
  <a class="hedron-card" href="multi-tenant/">
    <span class="hedron-card__icon" aria-hidden="true">☰</span>
    <strong>Multi-tenant</strong>
    <p>App-owned isolation checklist for caches, jobs, and fragments.</p>
  </a>
  <a class="hedron-card" href="jobs-celery-rq/">
    <span class="hedron-card__icon" aria-hidden="true">⏳</span>
    <strong>Durable jobs</strong>
    <p>Celery / RQ + Redis backends for multi-worker status.</p>
  </a>
  <a class="hedron-card" href="hardened-sessions/">
    <span class="hedron-card__icon" aria-hidden="true">⚿</span>
    <strong>Hardened sessions</strong>
    <p>Cookie flags, rotation, and production session secrets.</p>
  </a>
  <a class="hedron-card" href="data-apps/">
    <span class="hedron-card__icon" aria-hidden="true">▦</span>
    <strong>Data applications</strong>
    <p>Auto, DataTable, InMemoryDataSource, and SQLAlchemy.</p>
  </a>
  <a class="hedron-card" href="charts-and-htmx/">
    <span class="hedron-card__icon" aria-hidden="true">↗</span>
    <strong>Charts and HTMX</strong>
    <p>Supported static/Matplotlib charts, plus clearly labeled experimental interactive adapters.</p>
  </a>
  <a class="hedron-card" href="component-composition/">
    <span class="hedron-card__icon" aria-hidden="true">⧉</span>
    <strong>Compose built-ins</strong>
    <p>Layout, surfaces, and reusable component patterns.</p>
  </a>
  <a class="hedron-card" href="cookbook/">
    <span class="hedron-card__icon" aria-hidden="true">☰</span>
    <strong>Cookbook</strong>
    <p>Short pasteable recipes for common patterns.</p>
  </a>
  <a class="hedron-card" href="security/">
    <span class="hedron-card__icon" aria-hidden="true">◇</span>
    <strong>Security</strong>
    <p>Profiles, CSRF, CSP, redirects, and Explorer modes.</p>
  </a>
  <a class="hedron-card" href="threat-model/">
    <span class="hedron-card__icon" aria-hidden="true">⛨</span>
    <strong>Threat model</strong>
    <p>Trust boundaries, CSRF, XSS, and live-transport risks.</p>
  </a>
  <a class="hedron-card" href="deployment/">
    <span class="hedron-card__icon" aria-hidden="true">⇪</span>
    <strong>Deployment</strong>
    <p>Build manifests, Docker, reverse proxy, and multi-worker notes.</p>
  </a>
  <a class="hedron-card" href="performance/">
    <span class="hedron-card__icon" aria-hidden="true">⏱</span>
    <strong>Performance</strong>
    <p>Budgets, caching, and live-transport backpressure guidance.</p>
  </a>
  <a class="hedron-card" href="testing/">
    <span class="hedron-card__icon" aria-hidden="true">✓</span>
    <strong>Test your UI</strong>
    <p>render helpers, TestClient, and optional browser suite.</p>
  </a>
  <a class="hedron-card" href="best-practices/">
    <span class="hedron-card__icon" aria-hidden="true">★</span>
    <strong>Best practices</strong>
    <p>Defaults and anti-patterns for production apps.</p>
  </a>
  <a class="hedron-card" href="plugin-consumer/">
    <span class="hedron-card__icon" aria-hidden="true">⬡</span>
    <strong>Using plugins</strong>
    <p>Install, enable, deny-by-default, and review third-party plugins.</p>
  </a>
  <a class="hedron-card" href="plugin-authoring/">
    <span class="hedron-card__icon" aria-hidden="true">⬡</span>
    <strong>Plugin authoring</strong>
    <p>Entry points, capabilities, and Explorer panels.</p>
  </a>
  <a class="hedron-card" href="project-workflow/">
    <span class="hedron-card__icon" aria-hidden="true">☰</span>
    <strong>Project workflow</strong>
    <p>Scaffold layout, build, check, and day-to-day CLI.</p>
  </a>
  <a class="hedron-card" href="media-downloads/">
    <span class="hedron-card__icon" aria-hidden="true">⬇</span>
    <strong>Media downloads</strong>
    <p>Safe download responses, zip, and Range requests.</p>
  </a>
  <a class="hedron-card" href="upgrade/">
    <span class="hedron-card__icon" aria-hidden="true">↑</span>
    <strong>Upgrade</strong>
    <p>Upgrade to the living 0.30 train (also under Project → Upgrade).</p>
  </a>
  <a class="hedron-card" href="openapi/">
    <span class="hedron-card__icon" aria-hidden="true">{ }</span>
    <strong>OpenAPI</strong>
    <p>How HTML routes appear beside JSON in /docs.</p>
  </a>
  <a class="hedron-card" href="observability/">
    <span class="hedron-card__icon" aria-hidden="true">⌀</span>
    <strong>Observability</strong>
    <p>Logging, health/readiness, and HED-* diagnostics.</p>
  </a>
  <a class="hedron-card" href="accessibility/">
    <span class="hedron-card__icon" aria-hidden="true">♿</span>
    <strong>Accessibility</strong>
    <p>0.19 contracts, Explorer a11y, PE forms, AT matrix (human AT → 0.21).</p>
  </a>
  <a class="hedron-card" href="plain-fastapi/">
    <span class="hedron-card__icon" aria-hidden="true">{ }</span>
    <strong>Plain FastAPI</strong>
    <p>HedronRouter without the Hedron() facade.</p>
  </a>
  <a class="hedron-card" href="hdj-authoring/">
    <span class="hedron-card__icon" aria-hidden="true">⌜</span>
    <strong>HDJ authoring</strong>
    <p>Optional trusted .hdj templates (hedron[jinja]).</p>
  </a>
</div>
