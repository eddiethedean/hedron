# NiceGUI → Hedron 0.15 migration glossary

NiceGUI and Hedron both target backend-first Python UIs on FastAPI/Starlette hosts, but
NiceGUI’s Vue/Quasar client, WebSocket outbox, and imperative element mutation are
**deliberate non-parity** for Hedron. Map user-visible outcomes to reusable components and
ordinary HTTP/HTMX instead of translating `ui.*` calls one-for-one. Full audit:
[NiceGUI feature cross-check](https://github.com/eddiethedean/hedron/blob/main/docs/NICEGUI_FEATURE_CROSSCHECK.md).

## Element glossary (0.15)

| NiceGUI | Hedron 0.15 | Notes |
|---|---|---|
| `ui.leaflet` / map layers | `Map`, `GeoJSONLayer`, `MarkerSpec` | Accessible table alternative; tile allowlists (RFC-0033) |
| `ui.download` / file responses | `DownloadButton`, `media_file_response`, `download_all_zip`, Range helpers | RFC-0034 |
| `ui.carousel` | `Carousel` | Surface chrome (RFC-0035) |
| `ui.timeline` | `Timeline` | Surface chrome |
| `ui.chip` / chip inputs | `ChipInput`, `Pills`, `Badge` | Validated submitted values |
| `ui.date` / `ui.time` / `ui.number` | `DateInput`, `TimeInput`, `DateTimeInput`, `NumberInput`, `RangeInput` | Native controls |
| `ui.toggle` / `ui.radio` / selects | `ToggleSwitch`, `SegmentedControl`, `MultiSelect`, `Select` | |
| `ui.color_input` | `ColorInput` | |
| `ui.audio` / `ui.video` / `ui.image` | `Audio`, `Video`, `Image`, `Gallery`, `PdfViewer` | SafeUrl + CSP-conscious delivery |
| `ui.markdown` / LaTeX | `Math`, trusted markdown patterns | Executable content remains a trust boundary |
| `ui.iframe` | `IFrame` | Sandboxed; remote URL policy explicit |
| `ui.dialog` / menus / tooltips | `Dialog`, `Popover`, `MenuButton`, `ContextMenu`, `Tooltip` | Focus/safe-area gates |
| `ui.footer` / sticky bars | `BottomDock`, `ActionDock`, `Spacer` | Virtual keyboard / safe-area aware |
| Storage (`app.storage.user` / `browser` / `general`) | `SessionState`, cookies, `BrowserStorage` tiers | Quotas, expiry, consent; server authority for secrets |
| Auth recipes | OIDC login/logout helpers, session idle/absolute timeouts, login CSRF, rate limits | Host sessions + app authorization remain authoritative |
| Connections / resources | Named connection registry + SQLAlchemy/Snowflake providers | Host DI/lifespan; no global locator |
| Partial page updates | `app.region`, `@app.view`, `swap` / `swap_oob` | Fail-closed region authorization |
| Testing | `AppScenario`, HTMX InteractionResult asserts | HTTP-faithful; no outbox simulation |

## Storage-tier mapping

| NiceGUI storage | Hedron guidance |
|---|---|
| Browser storage | `BrowserStorage` for non-secret preferences (quota/expiry/consent) |
| User/session storage | Host session + `SessionState`; harden with idle/absolute timeouts |
| General/app storage | Application DI / durable store — not a framework global |
| Secrets / tokens | Server-only; never `BrowserStorage` |

## Deliberate non-parity

Do not expect first-party equivalents for:

- Vue/Quasar outbox mutation and client-side element trees as the primary UI model
- `ui.run_javascript` / arbitrary browser script injection
- Implicit two-way `binding` between elements and Python objects
- SPA `sub_pages` as a client router replacing ordinary HTTP navigation
- Single-worker WebSocket UI sync as the Supported multi-worker path (prefer HTMX + polling)

When NiceGUI relies on those mechanisms, redesign around explicit routes, fragments, and
explicit state scopes. See also [Streamlit migration matrix](streamlit-migration-matrix.md)
for overlapping data-app control families.

## Phase 0.17 — bindings and dashboards

| NiceGUI surface | Hedron 0.17 |
|---|---|
| Element binding / `ui.refreshable` | `DashboardBinding` / `InteractionGraph` (RFC-0040); inspectable edges |
| High-frequency timers | Polling + debounce/coalesce on bindings; sub-100ms not Supported |
| Jupyter / interactive hosting | 0.16 browser-Python sandbox + optional `hedron-notebook` preview |

Tools may emit a review plan; they must never claim automatic conversion (`MIGRATE-017`).
