# Hedron reference application (FastAPI) — production archetype (`ARCHETYPE-025`)

Canonical multi-worker production archetype for the living Hedron train (**0.25** /
Published `v0.25.0`). Also used as the authenticated team-administration demo and
GOVERN-019 accessibility statement dry-run (`accessibility_statement.py` — never
auto-claims WCAG conformance).

Packet SSOT: [PRODUCTION_ARCHETYPE.md](../../docs/api/PRODUCTION_ARCHETYPE.md).

**Human AT (0.21):** engineering prep for the task corpus is on this app; compensated /
screen-reader sessions remain Planned until Verified. Facilitator scripts:
[docs/acceptance/human-at/task-scripts.md](../../docs/acceptance/human-at/task-scripts.md).

## Ingredient checklist (ARCHETYPE-025)

| Ingredient | How this app covers it |
|---|---|
| reverse-proxy subpath | Caddy `handle_path /hedron/*` + `HEDRON_ROOT_PATH=/hedron` |
| Redis job/cache | `HEDRON_REDIS_URL` wires `RedisJobBackend` + `RedisCacheBackend` (requires the `redis` package — see `requirements-prod.txt`) |
| sticky sessions or external session store | Signed cookie sessions/CSRF (default external path); optional Caddy sticky noted in `Caddyfile` |
| `HEDRON_ENV=production` | Set in compose + Dockerfile; refuses placeholder / `change-me` secrets |
| CSP | `security="strict"` + `[tool.hedron.asset_policy] strict_csp = true` |
| Explorer off | `explorer="off"` when `HEDRON_ENV=production` |
| multi-worker | uvicorn `--workers 2` + Redis-backed job/cache |

## Run (local demo)

```bash
uv sync
uv run uvicorn app:app --app-dir examples/reference-app
```

Local/demo mode keeps Explorer in `development` and uses an in-memory demo secret.
Default credentials: `admin` / `secret` (HTTP Basic). **Replace before any shared or
production deploy.**

Open the home page for CRUD + DataEditor + charts/Markdown. Chart interaction endpoints
live under `/charts/*` (for example `/charts/fragment`, `/charts/search`).

## Production compose (canonical archetype)

```bash
export HEDRON_SESSION_SECRET="$(openssl rand -hex 32)"   # required — no weak default
export HEDRON_ALLOW_DEMO_AUTH=1                          # sample Basic auth only
docker compose --profile full up --build
# App via proxy: http://localhost:8080/hedron/
```

Compose requires `HEDRON_SESSION_SECRET` (production gate refuses secrets containing
`change-me`). Demo HTTP Basic is gated behind `HEDRON_ALLOW_DEMO_AUTH=1`. Redis client +
uvicorn are installed in the image; for non-Docker prod installs use
[`requirements-prod.txt`](requirements-prod.txt). Prefer this path when validating
production posture. Generic packaging notes:
[Deployment](https://hedron.readthedocs.io/en/latest/guides/deployment/) ·
[Production readiness](https://hedron.readthedocs.io/en/latest/guides/production-readiness/).

## Demonstrates

- `Hedron()` and plain `FastAPI` + `HedronRouter` modes (both honor production posture)
- Lazy addressable `UserTable` protected by router dependencies
- Typed create/update/delete actions with CSRF validation
- Progressive-enhancement create/edit (no-JS 303) plus HTMX `#user-table` swaps
- DataEditor, Auto, cache helpers, ColorMode, charts (Alpha `hedron[charts]`)
- Optional `hedron[native]` acceleration

## Tests

```bash
uv run pytest examples/reference-app tests/integration/test_reference_crud.py -q
```
