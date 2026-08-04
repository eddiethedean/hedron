## Summary

<!-- What changed and why (1–3 sentences). -->

## Test plan

- [ ] `uv run ruff format --check packages tests examples && uv run ruff check packages tests examples`
- [ ] `uv run pyright` (if packages touched)
- [ ] Relevant `pytest` suite(s)
- [ ] `uv run --group docs mkdocs build --strict` (if docs touched)
- [ ] Browser suite only if HTMX/markup/assets changed (`HEDRON_BROWSER=1`)

## Notes

<!-- Breaking changes, migration, RFC / decision IDs if applicable. -->
