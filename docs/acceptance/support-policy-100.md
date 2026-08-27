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
  `stable-inventory-100.toml`. Beta and Experimental interfaces retain their weaker labels.
- Fixes after publication move forward in `1.0.x`; removed aliases are not silently restored and
  a published tag is never retagged.

## Supported release matrix

| Boundary | Supported 1.0 range |
|---|---|
| Python | CPython `>=3.11,<3.15` |
| Hedron coordinated packages | `>=1.0.0,<2.0` on one coordinated train |
| FastAPI | `>=0.141.1,<0.150` |
| Pydantic | `>=2.13.4,<2.15` |
| Flask adapter | Flask `>=3,<4` |
| Django adapter | Django `>=5.2,<6` |
| Browser automation evidence | Playwright `1.62.0`, Chromium, Firefox, and WebKit |
| Type checking | Pyright `>=1.1.400` against the locked release environment |
| Packaging | wheel and sdist artifacts built with `SOURCE_DATE_EPOCH=0`; Python packages use PyPI attestations from the release workflow |

Independent satellites keep their own versions and declare Hedron compatibility explicitly.
The 1.0 release does not promise support for undocumented imports, unpinned future dependency
majors, third-party plugins, experimental live transports, human-AT conformance, a commercial SLA,
or multi-year LTS.
