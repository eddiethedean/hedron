---
title: Compose built-ins
description: Wire, nest, target, and replace Hedron components as one coherent component system.
---

# Compose built-ins

Hedron’s built-ins share one rendering model: layout components arrange children,
semantic components describe the document, surfaces group a bounded task, and controls
submit to or replace an explicitly addressable region. You can nest any `NodeLike`
component without manually rendering it or converting it to HTML first.

## Integrated example

<section class="hedron-component-demo" data-hedron-component-demo="Composition">
  <div class="hdc-stage">
    <div class="hdc-shell">
      <aside aria-label="Workspace">
        <strong>Acme</strong>
        <a href="#composition-profile">Profile</a>
        <a href="#composition-activity">Activity</a>
      </aside>
      <main class="hdc-stack">
        <div class="hdc-type">
          <span class="hdc-eyebrow">Team settings</span>
          <h2 id="composition-profile">Profile</h2>
          <p>Layouts, surfaces, fields, controls, and status content keep one visual rhythm.</p>
        </div>
        <article class="hdc-card">
          <header><span>Workspace details</span><span class="hdc-badge hdc-success">Saved</span></header>
          <form class="hdc-form" data-hdc-form>
            <label for="composition-name">Team name</label>
            <input id="composition-name" name="team_name" value="Acme">
            <div class="hdc-inline">
              <button class="hdc-button hdc-primary" type="submit">Save changes</button>
              <span class="hdc-muted" role="status" data-hdc-status>Ready to save.</span>
            </div>
          </form>
        </article>
        <div class="hedron-tabs" id="composition-activity">
          <div class="hedron-tablist" role="tablist">
            <button type="button" role="tab" id="composition-tab-0" aria-controls="composition-panel-0" aria-selected="true" tabindex="0">Activity</button>
            <button type="button" role="tab" id="composition-tab-1" aria-controls="composition-panel-1" aria-selected="false" tabindex="-1">Members</button>
          </div>
          <div role="tabpanel" id="composition-panel-0" aria-labelledby="composition-tab-0">
            <div class="hdc-status" role="status"><i></i><span>Deployment completed successfully.</span></div>
          </div>
          <div role="tabpanel" id="composition-panel-1" aria-labelledby="composition-tab-1" hidden>
            <p>12 active members · 2 invitations pending</p>
          </div>
        </div>
      </main>
    </div>
  </div>
</section>

The example is ordinary semantic HTML. The tabs and form response are enhanced by the
same documentation JavaScript used on the individual demos, while a real application
returns the replacement fragment from its route.

## Build from semantic ownership outward

Start with the page landmarks, then choose the smallest component that owns each
relationship:

```python
from hedron import (
    Card,
    Container,
    Form,
    FormField,
    Grid,
    Heading,
    Main,
    Sidebar,
    Stack,
    SubmitButton,
    Tabs,
    Text,
    TextInput,
)

workspace = Container(
    Grid(
        Sidebar(Text("Workspace navigation"), label="Workspace"),
        Main(
            Stack(
                Heading("Team settings", level=1),
                Card(
                    Form(
                        FormField(
                            name="team_name",
                            label="Team name",
                            control=TextInput("team_name"),
                        ),
                        SubmitButton("Save changes"),
                        action="/settings/team",
                    ),
                    title="Workspace details",
                    id="workspace-details",
                ),
                Tabs(
                    ("Activity", Text("Deployment completed successfully.")),
                    ("Members", Text("12 active members")),
                ),
            )
        ),
        columns=2,
    ),
    id="team-workspace",
)
```

`Container`, `Stack`, `Inline`, `Grid`, `Card`, `Form`, `Fragment`, landmarks,
`Dialog`, `Expander`, and `Sidebar` accept positional nodes or a `children=` value.
Use positional children for a small, readable tree and `children=` when a model or
loop already produced a sequence. If both are supplied, positional nodes render first.
Strings are always one text node; they are never split as a sequence.

## Nest components without crossing the renderer boundary

Pass a child component itself, not `child.render()` and not `render(child).html`. Keeping
the component in the tree preserves slot validation, cycle and depth checks, escaping,
diagnostics, and request-local identity tracking. `FormField` follows this rule too: it
copies and binds a compatible control, then lets the normal renderer process that bound
component.

Use ordinary children for the component’s main content. Use named slots only for a
secondary relationship whose placement belongs to the parent, such as a `Card` header
or footer, `Dialog` actions, or `Sidebar` body. Constructor slot arguments are concise;
the fluent `.slot()` form is useful when a builder assembles the same component in
stages.

## Make replacement boundaries explicit

Put a stable `id` on the smallest complete region that a request replaces. Layout and
surface IDs are intentionally ordinary DOM IDs, so an HTMX target, an anchor, a browser
test, and an accessibility relationship all refer to the same node.

```python
from hedron import Card, ComponentRef, RefreshButton, Text

activity_ref = ComponentRef(
    logical_id="activity.latest",
    path="/activity/latest",
    target="#activity",
    swap="outerHTML",
)

activity = Card(
    Text("Deployment completed successfully."),
    title="Latest activity",
    id="activity",
    footer=RefreshButton("Refresh", ref=activity_ref),
)
```

The `/activity/latest` response must return the same outer boundary—including
`id="activity"`—when using `outerHTML`. For `innerHTML`, return only the region’s
children. Loading, empty, validation, success, and recoverable-error responses should
all preserve the target contract. Keep GET requests safe; use POST plus authentication,
authorization, CSRF protection, and server-side validation for mutation.

## IDs and nested relationships

Supply an explicit `id` when external code needs a durable name. When an ID exists only
to connect internal elements, let the component generate it. `Tabs` prefixes every tab
and panel relationship with a request-local component ID, so sibling and nested tab sets
cannot collide. `FormField` does the same for its label, control, help, and error nodes;
pass `id=` only when another component or test must address that exact field.

Application classes augment built-in theme classes. For example,
`Stack(class_="settings-flow")` emits both `hedron-stack` and `settings-flow`, retaining
the default behavior while giving your theme a stable extension point. The validated
`gap` on `Stack`, `Inline`, and `Grid` is applied by the shipped stylesheet without an
inline style, so strict CSP remains intact.

## Composition checklist

- Choose a native landmark or content component before a generic layout wrapper.
- Keep source order equal to reading, focus, and mobile order.
- Replace the smallest complete region and preserve its target ID in every response.
- Pass components through the renderer; never splice rendered HTML strings together.
- Use a parent slot for parent-owned placement and children for the primary flow.
- Give repeated landmarks distinct accessible labels.
- Render representative full trees in tests, then test HTMX methods, targets, swaps,
  validation, focus, and announcements in a browser.

[All component demos](../components/index.md) · [HTMX interactions](htmx-interactions.md) ·
[Test your UI](testing.md)
