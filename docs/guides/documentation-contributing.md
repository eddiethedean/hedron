---
description: Maintain public documentation without reintroducing release, API, or example drift.
---

# Contribute documentation

Public documentation is a product surface. A change is complete only when its commands,
links, version claims, and rendered navigation are verified.

## Sources of truth

| Fact | Canonical source |
|---|---|
| Published versions and install bounds | `docs/release.toml` |
| Package versions and Python requirement | Package `pyproject.toml` files |
| Public symbols and signatures | Package source and `__all__` |
| Capability maturity | Stability and readiness inventories |
| Historical release behavior | Versioned What's New and changelog entries |

Do not copy a version into a new page when a link to
[Current release and support](current-release.md) is sufficient. Rendered release callouts and
the layer install matrix are expanded from `docs/release.toml` by `docs/hooks.py`.

## Current, historical, and maintainer material

- **Current:** user-facing 1.0 guidance in the main navigation and current search index.
- **Historical:** earlier release behavior, clearly bannered and excluded from current search
  when it conflicts with 1.0.
- **Maintainer:** RFCs, implementation plans, acceptance evidence, and release gates excluded
  from the public build.

Never present a migration API as the current golden path. New examples use `page`, `view`, and
`action` for Hedron, or the documented Edron page/fragment/action model.

The MkDocs hook excludes `guides/whats-new-0.*.md` from the current search index while keeping
those pages linkable from the historical archive and version selector.

## Required checks

```bash
uv run python scripts/check_docs_train_ssot.py
uv run python scripts/check_public_doc_links.py
uv run python scripts/check_api_docs_coverage.py
uv run python scripts/check_docs_file_tabs.py
uv run --group docs mkdocs build --strict
```

For command or code examples, run the narrow package tests and execute the documented command
in a clean temporary project. Screenshots must identify the example and version that produced
them.

## Review checklist

- The first command works in a clean supported Python environment.
- The page states prerequisites, result, failure recovery, and a next step.
- Public APIs include parameters, returns, errors, and a realistic example.
- Multi-file examples use matching file-path tabs followed by a **Full code on GitHub** link;
  one-file and ordered-edit examples stay linear.
- Links point to current pages unless explicitly labeled historical.
- Release facts come from the manifest or canonical release page.
- Navigation has one obvious location for the page.
