# REALWB-030 Workbench evidence

**Owner:** phase 0.30 / 0.33 Workbench packages  
**Gates:** `REALWB-030`, `WORKBENCH-033`  
**Packages:** `hedron-workbench`, `hedron-posit`, `fastapi-workbench`

## Purpose

Record licensed on-host Posit Workbench smoke for the three Workbench packages
before claiming a Supported version floor.

## Commands

```bash
# Current verified lane (Workbench 2026.07.0)
bash scripts/realwb_smoke.sh

# Supported minimum floor (Workbench 2025.05.1, linux/amd64)
bash scripts/realwb_202505_probe.sh
```

Workbench **2025.05.1** is amd64-only. On arm64 hosts the floor probe uses
`HEDRON_WORKBENCH_DOCKER_PLATFORM=linux/amd64`. `rserver-url` exit 139 under
qemu is labeled `PROXY_E2E=emulation_limited`; remaining launcher/HTTP/WS
markers still have to pass.

Requires product-license-shaped `PWB_LICENSE` in repo-root `.env` (parsed as
data, never sourced). The smoke deactivates the license before teardown.

## Evidence

| Lane | Image | Result |
|---|---|---|
| Current | `posit/workbench:2026.07.0` | [`realwb-030/RESULT.log`](realwb-030/RESULT.log) |
| Floor | `posit/workbench:2025.05.1` | [`realwb-030-202505/RESULT.log`](realwb-030-202505/RESULT.log) |

Required package markers: `HEDRON_PACKAGE=pass`, `POSIT_PACKAGE=pass`,
`FASTAPI_PACKAGE=pass`, `RESULT=pass`.
