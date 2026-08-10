---
status: shipped
---

# Beginner / stable facade inventory

!!! note "Facade inventory from 0.23; living train is 0.26"

    This inventory is the **FACADE-023** artifact. Symbols listed under
    [Expanded stable tier (0.23)](STABILITY.md#expanded-stable-tier-023) remain
    compatibility-protected **`stable`** on the living **0.26** train. Pin
    `hedron>=0.26.0,<0.27`.

**Owning gates:** `FACADE-023` (`python scripts/check_stable_facade.py`),
`STABLE-023`, `INVENTORY-023`. Decision: **D-053** /
[RFC-0056](https://github.com/eddiethedean/hedron/blob/main/docs/rfcs/RFC-0056-PRODUCTION-QUALITY.md).

## Rules

1. Beginner apps import the golden-path surface from `hedron` (and the module paths
   below for jobs / testing).
2. **Alpha** packages and `hedron.experimental` names must **not** appear in this inventory.
3. Optional extras (`hedron[data]`, `hedron[charts]`, `hedron[jinja]`, `hedron[auth]`, …)
   stay package-local — not root-stable via this facade.
4. Machine-checked block: fenced `text` inventory under
   [Inventory (machine-checked)](#inventory-machine-checked). Format:
   `module:Name` or `module:Class.method`.

## Beginner imports (human table)

| Import | Role |
|---|---|
| `from hedron import Hedron, HedronRouter, Page, Text, html` | App + document (already minimal-stable) |
| `from hedron import Stack, TextInput, TextArea, SubmitButton, RefreshButton` | CRUD chrome |
| `from hedron import Form, CsrfField, Hx, FormField, FormErrors, Label` | Forms / CSRF |
| `from hedron import SecurityPolicy, SecurityHeadersPolicy` | Profiles / headers |
| `from hedron import DoubleSubmitCookieCsrf, SessionTokenCsrf, CsrfStrategy` | CSRF strategies |
| `from hedron import swap, swap_oob, retarget, redirect_htmx, Poll` | Fragments / polling UI |
| `from hedron.jobs import enqueue_durable, job_status_response` | Durable job HTTP helpers |
| `from hedron_core.jobs import JobBackend, JobStatus, JobHandle, JobState, set_job_backend, get_job_backend` | Job protocol |
| `from hedron.testing import AppScenario, assert_page_document, assert_fragment_body, assert_htmx_trigger, assert_hx_retarget, assert_oob_present, assert_hx_push_url, assert_hx_redirect, assert_hx_reswap` | App tests |

Instance methods on `Hedron`: `app.region(...)`, `app.fragment(...)`.
On `HedronRouter`, declare `FragmentRegion` values and pass `fragment_regions=` to
`@page` / `@component` / `@action` (no `.region` / `.fragment` helpers).

## Deny list (must not appear in inventory)

- Any `hedron.experimental` export (`job_status_sse_response`, `SseResponse`, stream/WS/preload helpers, …)
- Alpha root names from charts / notebook / MCP / Gradio / native
- `DataTable`, `DataEditor`, dashboard/inference facades

## Inventory (machine-checked)

```text
hedron:Hedron
hedron:HedronRouter
hedron:Hedron.region
hedron:Hedron.fragment
hedron:FragmentRegion
hedron:Page
hedron:Text
hedron:html
hedron:Stack
hedron:TextInput
hedron:TextArea
hedron:SubmitButton
hedron:RefreshButton
hedron:Form
hedron:CsrfField
hedron:Hx
hedron:FormField
hedron:FormErrors
hedron:Label
hedron:SecurityPolicy
hedron:SecurityHeadersPolicy
hedron:DoubleSubmitCookieCsrf
hedron:SessionTokenCsrf
hedron:CsrfStrategy
hedron:swap
hedron:swap_oob
hedron:retarget
hedron:redirect_htmx
hedron:Poll
hedron.jobs:enqueue_durable
hedron.jobs:job_status_response
hedron_core.jobs:JobBackend
hedron_core.jobs:JobStatus
hedron_core.jobs:JobHandle
hedron_core.jobs:JobState
hedron_core.jobs:set_job_backend
hedron_core.jobs:get_job_backend
hedron.testing:AppScenario
hedron.testing:assert_page_document
hedron.testing:assert_fragment_body
hedron.testing:assert_htmx_trigger
hedron.testing:assert_hx_retarget
hedron.testing:assert_oob_present
hedron.testing:assert_hx_push_url
hedron.testing:assert_hx_redirect
hedron.testing:assert_hx_reswap
```

## See also

- [STABILITY.md](STABILITY.md) — levels and expanded tier
- [What’s ready](../guides/whats-ready.md) — capability maturity (Supported ≠ whole matrix is stable)
- [What’s new in 0.23](../guides/whats-new-0.23.md)
- [Minimal form](../guides/minimal-form.md) · [HTMX interactions](../guides/htmx-interactions.md)
