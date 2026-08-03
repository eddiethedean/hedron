# HTMX acceptance

## Phase 0.2 (`v0.2.0`) subset

- [x] Ordinary navigation yields PAGE documents; `HX-Request: true` yields FRAGMENT responses without duplicating the document shell.
- [x] History restore (`HX-History-Restore-Request: true`) selects PAGE mode.
- [x] Approved response headers (`HX-Redirect`, `HX-Push-Url`, `HX-Location`, triggers, retarget/reswap) reject unsafe external URLs and unsafe CSS selectors.
- [x] Interaction helpers (`Lazy`, `Poll`, `InfiniteScroll`, `RefreshButton`, `Pagination`, `oob_swap`, `action_attrs`) emit SafeUrl-backed HTMX attrs and validated targets.
- [x] Bundled HTMX is served from `/hedron-static/htmx.min.js` via `Hedron()` or `mount_hedron_static(app)`.
- [x] CSRF for unsafe actions works with HTMX header embedding and form-field tokens.

## Later

- [ ] Browser focus restoration and live-region announcements across swaps. *(accessibility / Explorer phase)*
- [ ] Broader OOB/trigger catalog and history policy knobs beyond the MVP helpers.

## Exit

Phase 0.2 HTMX request/response and helper contracts are covered by FastAPI integration and security suites.
