# What’s new in Hedron 0.23

**Published** as `v0.23.0`. Pin `hedron>=0.23.0,<0.24`.

Phase **0.23** expands the compatibility-protected **`stable`** API tier for a narrow
Supported CRUD/admin happy path (D-053 / RFC-0056). No new product features — catalog and
packaging only.

- **Expanded stable tier** — beginner facade chrome, HTMX regions/`swap` helpers, Poll +
  durable job status helpers (polling), SecurityPolicy profiles / `CsrfField`+`Form`+`Hx`,
  and selected `AppScenario` asserts become API `stable`.
- **Beginner inventory** — machine-checked import list in
  [STABLE_FACADE.md](../api/STABLE_FACADE.md) (`FACADE-023`).
- **Still not stable** — `hedron.experimental` live helpers, Alpha packages, `hedron[data]`,
  dashboards/inference, Dialog/Tabs/Pagination/Lazy, and other Supported chrome remain
  `beta` / `experimental`.

Contract: [STABILITY.md](../api/STABILITY.md#expanded-stable-tier-023) ·
[STABLE_FACADE.md](../api/STABLE_FACADE.md). Acceptance:
[RELEASE_0_23](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_23.md).

Gates: `STABLE-023`, `FACADE-023`, `INVENTORY-023`, `REGRESS-023`, `PKG-023` (all Verified).

Human AT sessions (`SR-021` / …) remain Planned / not Supported. Next: live-transport
disposition (**0.24**).
