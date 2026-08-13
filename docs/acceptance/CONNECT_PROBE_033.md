# Stage 0 licensed Connect contract probe (0.33)

**Owner:** phase 0.33 / [#167](https://github.com/eddiethedean/hedron/issues/167)  
**Gates:** `CONTRACT-033`, `CONNECT-033`, `BRIDGE-033`  
**Implements:** [HEDRON_POSIT_033](../implementation/HEDRON_POSIT_033.md) Stage 0

## Purpose

Replace assumptions with sanitized live evidence before Accepting RFC-0066:

1. Confirm Connect runtime product marker, singular base header, and `root_path` agreement.
2. Exercise GUID mount HTTP/HTMX/CSRF/session/assets/OpenAPI/redirect/WebSocket paths.
3. Prove whether application-owned **request** cookies round-trip natively (bridge keep/drop).
4. Record the exact Supported cut matrix cells (no `TBD` for Supported lanes).
5. Emit sanitized fixtures under `tests/fixtures/posit-connect/` (never real secrets/cookies).

## Prerequisites

- Docker reachable; `uv`, `curl`, `jq`, `openssl`, `rsync` on `PATH`
- Product-license-shaped `CONNECT_LICENSE`:
  - **Local:** repo-root `.env` (or export; parsed as data; never sourced)
  - **CI:** GitHub Actions secret `CONNECT_LICENSE` (same name as the env var)
- Legacy alias `CONNECT_API_KEY` is accepted locally only
- Prefer the pinned image used by `scripts/realconnect_029.sh` unless intentionally re-pinning

## Commands

```bash
# Full Stage 0 probe (writes docs/acceptance/realconnect-033/RESULT.log + fixtures)
bash scripts/realconnect_033_probe.sh

# Shape-only refine gate (does not require Verified rows)
python scripts/verify_pkg_33.py --allow-planned
```

Prior Published evidence in `docs/acceptance/realconnect-029/RESULT.log` is complementary
Workbench/Connect smoke history; Stage 0 for 0.33 must still produce `realconnect-033` artifacts.

## Redaction rules

Never commit or print:

- `CONNECT_LICENSE` / `CONNECT_API_KEY` / `PCT_LICENSE` / bootstrap or publishing keys
- Raw `Cookie` / `Set-Cookie` values, CSRF tokens, session identifiers
- Content GUIDs or vanity names that identify a private deployment
- `RStudio-Connect-Credentials` / user-session headers

Sanitized fixtures may record boolean presence, cookie **names**, path shapes with a placeholder
mount (`/content/00000000-0000-4000-8000-000000000000`), and header **counts**.

## License teardown

Each probe run deactivates the Connect product license before stopping the container
(`/opt/rstudio-connect/bin/license-manager deactivate`) with a 120s stop grace period.
This mirrors REALWB-030 and avoids consuming activation slots on repeated CI runs.
Set `HEDRON_CONNECT_LICENSE_STOP_TIMEOUT` to override the stop timeout (seconds).

## Stop conditions (from RFC-0066)

- Missing base header or `root_path` mismatch → native mode blocked; do **not** invent a bridge.
- Native request-cookie loss **not** reproduced → drop Supported bridge from 0.33; keep extension-point prose only.
- Bridge headers would appear in ordinary Connect logs → redesign or drop; do not waive redaction.
- Off-host Kubernetes Connect unavailable → mark off-host **Experimental** in the cut matrix.

## Bridge decision encoding

`docs/acceptance/realconnect-033/RESULT.log` must include exactly one of:

- `BRIDGE_DECISION=drop_supported` — native cookies round-trip; Supported bridge out of scope
- `BRIDGE_DECISION=keep_supported` — loss reproduced on a named topology; wire contract stays in RFC
