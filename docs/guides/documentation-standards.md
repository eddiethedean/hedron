# Documentation standards

How to keep Hedron's README, guides, reference pages, examples, and release material
accurate as the project changes. Start with [Contributor day-one](contributor-day-one.md)
for a small docs-only pull request; use this page when a change touches public behavior,
generated content, examples, or release claims.

## Write for a specific reader and task

Every public page should primarily serve one of these purposes:

| Page type | Reader question | Required content |
|---|---|---|
| Tutorial | "Can you teach me by building something?" | Prerequisites, ordered steps, observable results, next step |
| How-to guide | "How do I complete this task?" | Goal, pasteable commands/code, failure cases, related reference |
| Reference | "What exactly does this API accept and return?" | Signature, parameters, return value, errors, stability, example |
| Explanation | "Why does Hedron work this way?" | Context, tradeoffs, boundaries, links to the operational guide/reference |

Do not make one page serve every audience. Link to deeper material instead of placing
architecture, release evidence, and beginner setup in the same flow.

## Public path and maintainer corpus

The public MkDocs path is organized around adopters:

1. **Start** — install, first success, HTMX mental model, next steps
2. **Guides** — task-oriented application work
3. **Examples** — runnable, realistic workflows
4. **Reference** — exact surfaces, components, packages, and signatures
5. **Project** — fit, maturity, architecture, security, upgrades, and contributor day-one

RFCs, acceptance packets, internal status ledgers, and research notes stay in the GitHub
maintainer corpus and are excluded from MkDocs search. Public pages may link to that
evidence, but must explain the user-facing conclusion without requiring a gate ID, phase
code, or internal decision number.

## Know which file owns the text

| Content | Edit here | Then run |
|---|---|---|
| Root project introduction | `README.md` | docs checks below |
| Package landing page on PyPI | `packages/<package>/README.md` | package build/smoke for that package |
| Install pins / PyPI vs in-tree | `docs/getting-started/installation.md` | `check_docs_train_ssot.py` |
| Adopter maturity | `docs/guides/whats-ready.md` | `check_docs_train_ssot.py` |
| Component reference page | entry in `scripts/generate_component_docs.py` | generator with `--check` |
| Interactive docs simulation | `docs/demos/*.py` and its runnable source | simulation generator and recipe sync |
| Recipe Code tab | marked source under `docs/demos/runnable/` | `check_recipe_code_sync.py` |
| STATUS / ROADMAP | `docs/STATUS.md`, `docs/ROADMAP.md` (only roadmap file) | STATUS sync: `sync_status_roadmap.py`, then `--check` |
| Release procedure | `docs/RELEASE.md` | current release-gate checks |
| Documentation owner/review cadence | `docs/documentation.toml` | `check_documentation_ownership.py` |

Generated component pages and generated simulation HTML are outputs. Change their source
and regenerate them; do not hand-edit output that the next generator run will overwrite.

## Editorial rules

- Lead with the outcome or decision. Put prerequisites before commands.
- Use the exact supported Python and package ranges; distinguish **declared** dependency
  ranges from the narrower **CI-supported** ranges.
- Before calling a distribution "published" or documenting an extra, verify the live
  registry version and `Requires-Dist` metadata—not only the local `pyproject.toml`.
- Keep package maturity, capability readiness, and API stability separate. See
  [Maturity labels (evaluators)](../getting-started/how-to-read.md).
- Use **Supported**, **Experimental**, **Alpha**, and **Deferred** only with the meanings
  on [What's ready today](whats-ready.md).
- State ownership explicitly: Hedron does not supply application authorization,
  persistence, tenancy, a hosted service, or a commercial SLA.
- Prefer plain language in adopter docs. Explain a behavior first; place internal gate or
  decision identifiers in maintainer evidence, release history, or a secondary link.
- Keep examples copy-pasteable. Include imports, environment assumptions, expected output,
  and the next command or browser action.
- When two or more files form one example, show them as MkDocs content tabs. Use the exact
  project-relative path for both the tab label and code-fence `title`; keep a genuinely
  single-file example linear.
- Document failure behavior. Public API reference should name raised exceptions or HTTP
  status/error codes, not only the happy-path return value.
- Avoid duplicating current-version claims. Link to the canonical page when a second copy
  would create another release-time edit. Canonical pin facts live in
  [`docs/release.toml`](https://github.com/eddiethedean/hedron/blob/main/docs/release.toml)
  and are explained on [Installation](../getting-started/installation.md).
  **First-run copy-paste must always be registry-resolvable.** While
  `registry_status` is `uploaded`, Home, README, Quickstart, FAQ, and Installation use
  the same pin (`pin_floor` / `pin_ceiling`). While `registry_status` is `deferred`,
  first-run commands use the public-index pin (`pypi_pin_floor` / `pypi_pin_ceiling`);
  Installation and the `hedron` / `hedron-core` READMEs must say the in-tree train is
  not on PyPI yet. Never place an unpublished in-tree pin in a `pip` / `uv` / `uvx`
  command a visitor can copy.

## README quality bar

The root and package READMEs are distribution landing pages, not indexes of every feature.
Within the first screen, a reader should learn:

1. what the package does and which problem it solves;
2. maturity and a safe version pin;
3. Python/runtime prerequisites;
4. one minimal success path;
5. the most important limitation or ownership boundary;
6. where to continue for guides, API reference, support, and security.

Package READMEs must stand alone on PyPI. Do not rely on repository-relative links for
essential install or safety information.

## Examples and screenshots

- Prefer a small, realistic workflow over a component inventory.
- Verify commands from a clean environment when dependencies or scaffold behavior change.
- Keep the first app focused on one observable interaction; move variants to guides.
- Use meaningful test data and safe placeholder secrets. State that placeholder secrets
  must be replaced before deployment.
- Give screenshots descriptive alt text. Update or remove a screenshot when it no longer
  matches the command that precedes it.
- Label simulations as simulations. Never imply that static documentation is a hosted
  application or live backend.

### File-oriented examples

Use file tabs when a reader must create or compare multiple files to reproduce one result:

````markdown
=== "app.py"

    ```python title="app.py"
    # complete app file
    ```

=== "styles.css"

    ```css title="styles.css"
    /* complete stylesheet */
    ```
````

- Put a small project tree before the tabs when the example has more than three files.
- Keep tab labels and fence titles identical, including directories and capitalization.
- Make each tab complete enough to save as the named file; do not hide required imports in
  prose or another tab.
- Follow every file-tab group with a **Full code on GitHub** link. Link exact runnable source
  when it exists; for a shortened teaching example, link the maintained full reference and
  state that relationship honestly.
- Keep ordered edits, command sequences, migration stages, and independent alternatives
  linear. Tabs should describe files that coexist, not conceal steps that happen over time.
- For runnable repository examples, add source-sync coverage so documentation cannot drift
  from the actual files.

## Reader-experience quality bar

- Keep **Start**, **Guides**, **Examples**, **Reference**, and **Project** task-oriented.
  The golden path, Cookbook, troubleshooting, and error codes must remain in navigation.
- Give primary landing, tutorial, and support pages a concise `description` and a gentle
  search boost. Narrative answers should rank ahead of generated signatures; Autodoc is
  for exact lookup after a reader knows the symbol they need.
- Use the same labels for equivalent content tabs (`uv`, `pip`, operating systems) so a
  reader's selection follows them across pages.
- Preserve visible keyboard focus, meaningful link text, heading order, table headers,
  screenshot alternatives, and a useful not-found page.
- After navigation, template, or CSS changes, inspect the homepage, first-app tutorial,
  search results, and 404 page at desktop and narrow-mobile widths in both color schemes.
  Check for horizontal overflow and verify that the primary action appears before setup
  detail on mobile.

## Local verification

For a normal docs change:

```bash
uv sync --group docs
uv run python scripts/check_docs_train_ssot.py
uv run python scripts/check_package_docs_inventory.py
uv run python scripts/check_documentation_ownership.py
uv run python scripts/check_api_docs_coverage.py
uv run python scripts/check_package_readme_links.py
uv run python scripts/check_public_doc_links.py
uv run python scripts/check_changelog_structure.py
uv run python scripts/check_recipe_code_sync.py
uv run python scripts/check_docs_file_tabs.py
uv run --group docs mkdocs build --strict
```

When changing generated component docs or simulations:

```bash
uv run python scripts/generate_component_docs.py
uv run python scripts/generate_component_docs.py --check
uv run python scripts/generate_sim_demos.py
uv run python scripts/generate_sim_demos.py --check
```

Use the narrowest runnable example or test that proves edited code. The full CI quality
suite also checks formatting, types, wheel smoke tests, documentation links, generated
artifacts, and release-train consistency:

```bash
bash scripts/ci_checks.sh quality --python 3.12
```

## Pull-request review checklist

- [ ] The intended reader and task are obvious from the opening paragraph.
- [ ] Commands work from the directory and environment the page states.
- [ ] Code uses public imports and current signatures.
- [ ] Multi-file examples use matching project-relative file tabs; sequential edits remain linear.
- [ ] Expected output or browser behavior is stated.
- [ ] Errors, security boundaries, and production caveats are present where relevant.
- [ ] Version, maturity, and support claims match their canonical pages.
- [ ] Published install commands resolve against live registry metadata in a clean environment.
- [ ] New public APIs appear in the coverage map and have reference documentation.
- [ ] New built-ins have generated component pages and composition tests.
- [ ] Relative links resolve and the strict MkDocs build passes.
- [ ] Public pages do not link relatively to maintainer files excluded from MkDocs.
- [ ] Package changelog releases are non-empty and remain under one top-level title.
- [ ] Generated outputs were updated from their owning source.

See also: [Contributing](../CONTRIBUTING.md) ·
[Contributor day-one](contributor-day-one.md) ·
[API coverage map](../api/COVERAGE.md)
