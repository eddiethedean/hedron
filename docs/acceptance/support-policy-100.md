# Hedron 1.0 support policy

This policy takes effect when `v1.0.0` is published. It defines the exact community-support and
compatibility window used by the 1.0 release gate; it is not a commercial SLA or warranty.

## Version and security window

- `1.0.x` is the current stable train. Security and correctness fixes target the newest `1.0.x`
  patch. The project makes no fixed response-time promise.
- `0.67.x` is the documented migration and rollback source through **2027-02-27**. During that
  window it receives best-effort migration-blocker and critical-security triage; applications
  should move to `1.0.x`. After that date, upgrade is required.
- The stable 1.x SemVer promise applies only to symbols enumerated in
  `stable-inventory-100.toml` and packages marked `maturity = "stable"` in
  `release/support-matrix.toml`. Beta and Experimental interfaces retain their weaker labels.
- Fixes after publication move forward in `1.0.x`; removed aliases are not silently restored and
  a published tag is never retagged.

## Supported release matrix

| Boundary | Supported 1.0 range |
|---|---|
| Python | CPython `>=3.10,<3.15` |
| Stable coordinated packages (`hedron-core`, `hedron`, `hedron-data`, `hedron-charts`, `hedron-maps`) | `>=1.0.0,<2.0` on one coordinated train |
| Stable Edron facade (`edron`) | `>=1.0.0,<2.0`; independently tagged after the coordinated train |
| FastAPI | `>=0.121.0,<0.150` |
| Starlette | `>=0.40.0,<1.0` |
| Pydantic | `>=2.12.0,<2.15` |
| Uvicorn | `>=0.32,<1.0` |
| Flask adapter | Flask `>=3,<4` |
| Django adapter | Django `>=5.2,<6` |
| Browser automation evidence | Playwright `1.62.0`, Chromium, Firefox, and WebKit |
| Stable-package typing | Pyright `>=1.1.400`, warning-fatal with 0 warnings across the six Stable packages; Beta satellite warnings are outside the Stable claim |
| Packaging | wheel and sdist artifacts built with `SOURCE_DATE_EPOCH=315619200`; approved hashes are verified before Python packages use PyPI attestations |

All other packages are independent Beta satellites and must declare their Hedron compatibility
explicitly. A Beta capability may be useful or individually “Supported” without entering the
stable platform promise.
The 1.0 release does not promise support for undocumented imports, unpinned future dependency
majors, third-party plugins, experimental live transports, human-AT conformance, a commercial SLA,
or multi-year LTS.
