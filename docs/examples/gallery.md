---
hide:
  - toc
---

# Simulated UI patterns (not a Hedron server)

These in-docs demos show layout and interaction *patterns*. They are **browser
simulations**—not a running Hedron process. Authentication, CSRF, persistence, HTMX,
charts, and Markdown need a real Python server.

!!! warning "Not a live Hedron app"

    Filtering, tabs, dialogs, and form updates below are client-side JavaScript only.
    For CSRF, HTMX fragments, and persistence, run a [runnable example](runnable.md)
    (clone and `uv sync`; not available from `pip install hedron` alone).

## Run a real app first

Prefer this before scrolling to the simulations:

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
uv run uvicorn app:app --app-dir examples/reference-app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Walkthrough:
[reference app](reference-app.md) · all [runnable examples](runnable.md).

| App | Framework | Notes |
|---|---|---|
| [reference-app](https://github.com/eddiethedean/hedron/tree/main/examples/reference-app) | FastAPI flagship | CRUD, CSRF, charts |
| [flask-reference](https://github.com/eddiethedean/hedron/tree/main/examples/flask-reference) | Flask adapter | Home + fragment |
| [django-reference](https://github.com/eddiethedean/hedron/tree/main/examples/django-reference) | Django adapter | Home + fragment |
| [hdj-progressive](https://github.com/eddiethedean/hedron/tree/main/examples/hdj-progressive) | Optional HDJ | Prints HTML to stdout (not a web server) |
| [workbench-reference](https://github.com/eddiethedean/hedron/tree/main/examples/workbench-reference) | FastAPI + Workbench | Ordinary-app launcher and `HedronWorkbench` variants |

Quickstarts: [FastAPI](../getting-started/quickstart.md) ·
[Flask](../getting-started/flask.md) · [Django](../getting-started/django.md) ·
[HDJ API](../api/JINJA.md) · [Live interaction](../guides/live-interaction.md).

## Simulated patterns

Decorative preview chrome below is **not** a real `localhost` server.

<section class="hedron-demo" data-hedron-demo="team-admin" aria-label="Simulated team administration pattern">
  <div class="hedron-demo__chrome" aria-hidden="true">
    <span></span><span></span><span></span>
    <div class="hedron-demo__address">docs simulation · not a server</div>
  </div>
  <div class="hedron-app-shell">
    <aside class="hedron-app-nav">
      <div class="hedron-app-brand">
        <img src="../../assets/hedron-mark.svg" alt="">
        <span>Acme Console</span>
      </div>
      <nav aria-label="Example application">
        <a href="#demo-team" class="is-active" aria-current="page"><span aria-hidden="true">◎</span> Team</a>
      </nav>
      <div class="hedron-app-user"><span>AM</span><div><strong>Admin</strong><small>admin@acme.test</small></div></div>
    </aside>
    <div class="hedron-app-main" id="demo-team">
      <header class="hedron-app-heading">
        <div><span class="hedron-app-kicker">Workspace</span><h2>Team members</h2><p>Manage access to the Acme workspace.</p></div>
        <button class="hedron-ui-button hedron-ui-button--primary" type="button" data-demo-open>Add member</button>
      </header>
      <div class="hedron-app-metrics" aria-label="Team summary">
        <div><span>Members</span><strong data-demo-count>3</strong><small>2 active today</small></div>
        <div><span>Administrators</span><strong>1</strong><small>Full workspace access</small></div>
        <div><span>Pending invites</span><strong>0</strong><small>All caught up</small></div>
      </div>
      <section class="hedron-app-panel" aria-labelledby="team-table-title">
        <div class="hedron-app-toolbar">
          <div><h3 id="team-table-title">People</h3><p>Roles and contact details</p></div>
          <label class="hedron-demo-search"><span class="sr-only">Filter team members</span><span aria-hidden="true">⌕</span><input type="search" placeholder="Filter people…" data-demo-filter></label>
        </div>
        <div class="hedron-demo-table-wrap">
          <table>
            <thead><tr><th scope="col">Member</th><th scope="col">Email</th><th scope="col">Role</th><th scope="col">Status</th></tr></thead>
            <tbody data-demo-rows>
              <tr><td><span class="hedron-avatar hedron-avatar--violet">AL</span><strong>Ada Lovelace</strong></td><td>ada@example.com</td><td><span class="hedron-role">Admin</span></td><td><span class="hedron-status">Active</span></td></tr>
              <tr><td><span class="hedron-avatar hedron-avatar--blue">GH</span><strong>Grace Hopper</strong></td><td>grace@example.com</td><td><span class="hedron-role hedron-role--muted">Member</span></td><td><span class="hedron-status">Active</span></td></tr>
              <tr><td><span class="hedron-avatar hedron-avatar--amber">AT</span><strong>Alan Turing</strong></td><td>alan@example.com</td><td><span class="hedron-role hedron-role--muted">Member</span></td><td><span class="hedron-status">Active</span></td></tr>
            </tbody>
          </table>
          <p class="hedron-demo-empty" data-demo-empty hidden>No team members match that filter.</p>
        </div>
      </section>
    </div>
  </div>
  <dialog class="hedron-demo-dialog" data-demo-dialog aria-labelledby="add-member-title">
    <form method="dialog" data-demo-form>
      <div class="hedron-dialog-heading"><div><span class="hedron-app-kicker">New teammate</span><h2 id="add-member-title">Add a member</h2></div><button type="button" class="hedron-dialog-close" data-demo-close aria-label="Close dialog">×</button></div>
      <label>Full name<input name="name" autocomplete="off" required placeholder="Katherine Johnson"></label>
      <label>Email address<input name="email" type="email" autocomplete="off" required placeholder="katherine@example.com"></label>
      <label>Workspace role<select name="role"><option>Member</option><option>Admin</option></select></label>
      <div class="hedron-dialog-actions"><button type="button" class="hedron-ui-button" data-demo-close>Cancel</button><button type="submit" class="hedron-ui-button hedron-ui-button--primary">Add member</button></div>
    </form>
  </dialog>
  <p class="sr-only" role="status" aria-live="polite" data-demo-status></p>
</section>

Try filtering for `grace`, then add a member. The table updates locally and announces the
change to assistive technology.

## Component Explorer

Hedron Explorer explains what the framework registered and why it will render a given
response. Switch between the preview, typed props, and request contract below.

<section class="hedron-demo hedron-explorer-demo" data-hedron-demo="explorer" aria-label="Interactive Component Explorer example">
  <div class="hedron-demo__chrome" aria-hidden="true">
    <span></span><span></span><span></span>
    <div class="hedron-demo__address" data-demo-address>docs simulation · not a server</div>
  </div>
  <div class="hedron-explorer-shell">
    <aside class="hedron-explorer-nav" aria-label="Registered components">
      <div class="hedron-app-brand"><img src="../../assets/hedron-mark.svg" alt=""><span>Explorer</span></div>
      <label class="hedron-explorer-mobile-select"><span class="sr-only">Component</span>
        <select data-demo-component-select aria-label="Select component">
          <option value="UserCard" selected>UserCard</option>
          <option value="StatusBanner">StatusBanner</option>
          <option value="TeamTable">TeamTable</option>
        </select>
      </label>
      <small>COMPONENTS</small>
      <button type="button" class="hedron-explorer-item is-selected" data-demo-component="UserCard" aria-current="true">UserCard <span aria-hidden="true">›</span></button>
      <button type="button" class="hedron-explorer-item" data-demo-component="StatusBanner">StatusBanner <span aria-hidden="true">›</span></button>
      <button type="button" class="hedron-explorer-item" data-demo-component="TeamTable">TeamTable <span aria-hidden="true">›</span></button>
    </aside>
    <div class="hedron-explorer-main">
      <div class="hedron-explorer-heading"><div><span class="hedron-app-kicker">hedron-reference</span><h2 data-demo-title>UserCard</h2></div><span class="hedron-stable-pill" data-demo-stability>Beta</span></div>
      <div class="hedron-demo-tabs" role="tablist" aria-label="Explorer panels">
        <button role="tab" aria-selected="true" aria-controls="explorer-preview" id="tab-preview" tabindex="0" data-demo-tab="preview">Preview</button>
        <button role="tab" aria-selected="false" aria-controls="explorer-props" id="tab-props" tabindex="-1" data-demo-tab="props">Props</button>
        <button role="tab" aria-selected="false" aria-controls="explorer-request" id="tab-request" tabindex="-1" data-demo-tab="request">Request</button>
      </div>
      <section class="hedron-explorer-panel" id="explorer-preview" role="tabpanel" aria-labelledby="tab-preview" data-demo-panel="preview">
        <div class="hedron-preview-canvas" data-demo-preview><article><span class="hedron-avatar hedron-avatar--violet">AL</span><div><strong>Ada Lovelace</strong><p>Platform administrator</p></div><span class="hedron-status">Active</span></article></div>
        <div class="hedron-explorer-facts">
          <div><span>Render mode</span><strong data-demo-fact-mode>FRAGMENT</strong></div>
          <div><span>HTML nodes</span><strong data-demo-fact-nodes>6</strong></div>
          <div><span>Diagnostics</span><strong class="is-clean" data-demo-fact-diagnostics>0</strong></div>
        </div>
      </section>
      <section class="hedron-explorer-panel" id="explorer-props" role="tabpanel" aria-labelledby="tab-props" data-demo-panel="props" hidden>
        <table><thead><tr><th>Prop</th><th>Type</th><th>Required</th></tr></thead><tbody data-demo-props></tbody></table>
      </section>
      <section class="hedron-explorer-panel" id="explorer-request" role="tabpanel" aria-labelledby="tab-request" data-demo-panel="request" hidden>
        <div class="hedron-request-line"><span class="hedron-method">GET</span><code data-demo-path>/components/user-card</code><span class="hedron-ok">200 OK</span></div>
        <pre><code data-demo-headers>HX-Request: true
HX-Target: #team-list
Accept: text/html</code></pre>
        <p data-demo-request-note>Returns a fragment, applies private caching, and exposes no source path.</p>
      </section>
    </div>
  </div>
</section>

## Run the backend examples

Clone the repository and start a real application:

```bash
# FastAPI reference (full demo)
uv sync
uv run uvicorn app:app --app-dir examples/reference-app

# Flask slice
uv run python examples/flask-reference/app.py

# Django slice (ASGI)
cd examples/django-reference && uv run uvicorn asgi:application --port 8000
```

FastAPI reference credentials: `admin` / `secret`. That server exercises strict security
headers, CSRF-protected actions, lazy HTMX resources, typed Python composition, scoped styles, and the
sealed asset build.

[Reference app walkthrough](reference-app.md){ .md-button }
[Build your first app](../getting-started/quickstart.md){ .md-button .md-button--primary }
