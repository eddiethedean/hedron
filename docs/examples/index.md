---
hide:
  - toc
---

# Component gallery

Explore complete interface states directly in the documentation. These demos use the
same semantic HTML patterns as Hedron's runnable examples; their interactions stay in
your browser so they work on Read the Docs without an application server.

!!! info "Simulated in the browser — not a live Hedron server"

    Filtering, tabs, dialogs, and form updates below are real client-side interactions.
    Authentication, CSRF enforcement, persistence, HTMX requests, charts, and Markdown
    require a runnable example from the repository (clone and `uv sync`; not available from
    `pip install hedron` alone).

## Run a real app first

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
uv sync
uv run uvicorn app:app --app-dir examples/reference-app --reload
```

| App | Framework | Notes |
|---|---|---|
| [reference-app](https://github.com/eddiethedean/hedron/tree/main/examples/reference-app) | FastAPI flagship | CRUD, CSRF, charts |
| [flask-reference](https://github.com/eddiethedean/hedron/tree/main/examples/flask-reference) | Flask adapter | Home + fragment |
| [django-reference](https://github.com/eddiethedean/hedron/tree/main/examples/django-reference) | Django adapter | Home + fragment |
| [hdj-progressive](https://github.com/eddiethedean/hedron/tree/main/examples/hdj-progressive) | Optional HDJ | Prints HTML to stdout (not a web server) |

Quickstarts: [FastAPI](../getting-started/quickstart.md) ·
[Flask](../getting-started/flask.md) · [Django](../getting-started/django.md) ·
[HDJ API](../api/JINJA.md) · [Live interaction](../guides/live-interaction.md).

## Simulated gallery

The sections below are in-docs simulations for layout and interaction patterns.

<section class="hedron-demo" data-hedron-demo="team-admin" aria-label="Interactive team administration example">
  <div class="hedron-demo__chrome" aria-hidden="true">
    <span></span><span></span><span></span>
    <div class="hedron-demo__address">localhost:8000/team</div>
  </div>
  <div class="hedron-app-shell">
    <aside class="hedron-app-nav">
      <div class="hedron-app-brand">
        <img src="../assets/hedron-mark.svg" alt="">
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
    <div class="hedron-demo__address">localhost:8000/hedron-explorer/components/UserCard</div>
  </div>
  <div class="hedron-explorer-shell">
    <aside class="hedron-explorer-nav">
      <div class="hedron-app-brand"><img src="../assets/hedron-mark.svg" alt=""><span>Explorer</span></div>
      <small>COMPONENTS</small>
      <div class="hedron-explorer-item is-selected">UserCard <span>›</span></div>
      <div class="hedron-explorer-item">StatusBanner <span>›</span></div>
      <div class="hedron-explorer-item">TeamTable <span>›</span></div>
    </aside>
    <div class="hedron-explorer-main">
      <div class="hedron-explorer-heading"><div><span class="hedron-app-kicker">hedron-reference</span><h2>UserCard</h2></div><span class="hedron-stable-pill">Stable</span></div>
      <div class="hedron-demo-tabs" role="tablist" aria-label="Explorer panels">
        <button role="tab" aria-selected="true" aria-controls="explorer-preview" id="tab-preview" tabindex="0" data-demo-tab="preview">Preview</button>
        <button role="tab" aria-selected="false" aria-controls="explorer-props" id="tab-props" tabindex="-1" data-demo-tab="props">Props</button>
        <button role="tab" aria-selected="false" aria-controls="explorer-request" id="tab-request" tabindex="-1" data-demo-tab="request">Request</button>
      </div>
      <section class="hedron-explorer-panel" id="explorer-preview" role="tabpanel" aria-labelledby="tab-preview" data-demo-panel="preview">
        <div class="hedron-preview-canvas"><article><span class="hedron-avatar hedron-avatar--violet">AL</span><div><strong>Ada Lovelace</strong><p>Platform administrator</p></div><span class="hedron-status">Active</span></article></div>
        <div class="hedron-explorer-facts"><div><span>Render mode</span><strong>FRAGMENT</strong></div><div><span>HTML nodes</span><strong>6</strong></div><div><span>Diagnostics</span><strong class="is-clean">0</strong></div></div>
      </section>
      <section class="hedron-explorer-panel" id="explorer-props" role="tabpanel" aria-labelledby="tab-props" data-demo-panel="props" hidden>
        <table><thead><tr><th>Prop</th><th>Type</th><th>Required</th></tr></thead><tbody><tr><td><code>name</code></td><td><code>str</code></td><td>Yes</td></tr><tr><td><code>role</code></td><td><code>str</code></td><td>Yes</td></tr><tr><td><code>active</code></td><td><code>bool</code></td><td>No</td></tr></tbody></table>
      </section>
      <section class="hedron-explorer-panel" id="explorer-request" role="tabpanel" aria-labelledby="tab-request" data-demo-panel="request" hidden>
        <div class="hedron-request-line"><span class="hedron-method">GET</span><code>/components/user-card</code><span class="hedron-ok">200 OK</span></div>
        <pre><code>HX-Request: true
HX-Target: #team-list
Accept: text/html</code></pre>
        <p>Returns a fragment, applies private caching, and exposes no source path.</p>
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

[Read the reference application contract](../REFERENCE_APPLICATION.md){ .md-button }
[Build your first app](../getting-started/quickstart.md){ .md-button .md-button--primary }
