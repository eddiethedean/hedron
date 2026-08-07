# Mutations: `@action` vs `@component` POST

Hedron has two common ways to handle unsafe HTTP methods (POST/PUT/PATCH/DELETE).
Pick one deliberately — do not mix them on the same form without understanding the
difference.

## Decision table

| You need… | Use | Why |
|---|---|---|
| Classic form POST that returns a **full page** (redirect or confirmation `Page`) | `@app.action("/…")` | Simplest CSRF-safe mutation; no fragment allowlist |
| HTMX POST that swaps a **declared region** / returns `InteractionResult` | `@app.component("/…", methods=["POST"], fragment_regions=(…,))` | Region allowlists live on `page`/`component`, not `action` |
| DELETE/PUT with CSRF and a fragment body | `@app.action(..., method="DELETE")` **or** `@component(..., methods=["DELETE"])` | Prefer `component` when you need `fragment_regions` |

`@action` does **not** accept `fragment_regions`. If HTMX sends `HX-Target` and you need
an allowlist, use `@component`.

### Try it (simulated)

Same submit — toggle HTMX on (region swap) vs off (full confirmation page).

<section class="hedron-component-demo" data-hedron-component-demo="MutationsPeGuide" data-hdc-pe-mode="htmx">
  <div class="hdc-stage">
    <div class="hdc-inline" role="group" aria-label="Progressive enhancement">
      <button class="hdc-button hdc-primary" type="button" data-hdc-pe-toggle="htmx" aria-pressed="true">HTMX on</button>
      <button class="hdc-button" type="button" data-hdc-pe-toggle="full" aria-pressed="false">HTMX off</button>
    </div>
    <div data-hdc-pe-app>
      <form class="hdc-form" data-hdc-form="pe-submit" data-hdc-path="/save">
        <label for="pe-note">Note<input id="pe-note" name="note" type="text" value="Ship the docs demo"></label>
        <button class="hdc-button hdc-primary" type="submit">Save</button>
      </form>
      <div class="hdc-result" data-hdc-form-result hidden aria-live="polite"></div>
    </div>
    <div class="hdc-result" data-hdc-pe-page hidden aria-live="polite"></div>
    <p class="hdc-muted" role="status" data-hdc-status>HTMX on — submit swaps the result region.</p>
  </div>
  <div class="hdc-request" data-hdc-request hidden><span>Simulated HTMX</span><code>POST /save → 200</code></div>
</section>

## Classic form → `@action`

See the full pasteable sample in [Minimal form POST](minimal-form.md).

```python
@app.action("/save")
def save(request: Request, note: Annotated[str, Form()]) -> Page:
    return Page(Text(f"Saved: {note}"), title="Saved")
```

## HTMX fragment → `@component` POST

See [Forms and actions](forms-and-actions.md) for validation fragments.

```python
from hedron import FragmentRegion, InteractionResult

FORM = FragmentRegion(id="note-form", selector="#note-form")


@app.component("/save", methods=["POST"], fragment_regions=(FORM,))
def save_fragment(...) -> InteractionResult:
    return InteractionResult(content=..., region_id=FORM.id, explanation="...")
```

## CSRF

Both paths require CSRF when security profiles enable it for unsafe methods. Seed the
cookie on a safe GET and send `csrf_token` (form field) or `X-CSRF-Token` (header).

## See also

[Action API](../api/ACTION.md) · [Interaction](../api/INTERACTION.md) ·
[Hedron methods](../api/HEDRON.md)
