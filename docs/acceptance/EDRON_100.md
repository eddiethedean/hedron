# Edron 1.0 acceptance

**Status:** Implemented and verified in-tree as the untagged `1.0.0` candidate; PyPI publication deferred

**Package target:** `edron==1.0.0` · Hedron `1.0.0` (`>=1.0.0,<2.0`) ·
hedron-data `1.0.0` (`>=1.0.0,<2.0`)

Edron 1.0 adopts Hedron 1.0 as its runtime floor. It no longer treats Hedron 1.0 as a
forward-compatibility target and does not retain a Hedron 0.67 runtime lane. Existing Edron 0.9.1
artifacts remain the immutable bridge release for applications that still need the wider
`>=0.67.0,<2.0` range.

The application facade delegates each canonical role to its native owner:

- `App.page` registers through `Hedron.page`;
- Edron `fragment` descriptors register through `Hedron.view` and retain the exact returned
  `FragmentHandle`;
- Edron `action` descriptors register through `Hedron.action` and retain the exact returned
  `ActionHandle`; and
- features, task flows, and packages register through `Hedron.include`.

This removes Edron's former manual handle construction and private root-router synchronization.
Hedron therefore owns route registration, application identity, binding plans, fragment regions,
lifecycle metadata, result lowering, OpenAPI projection, and the application handle registry once.

| Gate | Implementation evidence | State |
|---|---|---|
| `EDR-100-TRAIN` | Edron, Hedron, and hedron-data metadata and lock resolve the 1.0.0 train | Implemented |
| `EDR-100-ROUTES` | Page, view, action, and include use only canonical Hedron 1.0 APIs | Implemented |
| `EDR-100-IDENTITY` | Edron descriptors expose the exact handles stored by Hedron | Implemented |
| `EDR-100-INTERACTION` | Native interaction/outcome identity and request-effect lowering | Implemented |
| `EDR-100-LIFECYCLE` | Browser-plan closure and HTMX/component lifecycle ownership | Implemented |
| `EDR-100-COMPONENTS` | Native engine dispositions, styling, specialist hosts, and accessible fallbacks | Implemented |
| `EDR-100-DATA-JOBS-CACHE` | Native data, resource, cache, TaskFlow, PollPolicy, and backend contracts | Implemented |
| `EDR-100-TOOLING` | Scaffolds and generated migrations pin 1.x and static migration reports no legacy API | Implemented |
| `EDR-100-PACKAGING` | Version, dependencies, artifacts, typing marker, and clean-install checks | Implemented |
| `EDR-100-REGRESSION` | Unit, HTTP, security, accessibility, migration, and packaging suites | Implemented |

The machine-readable lock is [edron-100.toml](edron-100.toml). Historical 0.9 evidence remains in
[EDRON_009.md](EDRON_009.md) and is not rewritten by this release.
