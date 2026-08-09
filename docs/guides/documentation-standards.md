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

1. **Start** — install, first success, core mental model
2. **Guides** — task-oriented application work
3. **Examples** — runnable, realistic workflows
4. **Packages / Reference** — exact surfaces and signatures
5. **Evaluate** — fit, maturity, security, operations, support
6. **Project** — releases, migration, contributing, maintenance

RFCs, acceptance packets, internal status ledgers, and research notes stay in the GitHub
maintainer corpus and are excluded from MkDocs search. Public pages may link to that
evidence, but must explain the user-facing conclusion without requiring a gate ID, phase
code, or internal decision number.

## Know which file owns the text

| Content | Edit here | Then run |
|---|---|---|
| Root project introduction | `README.md` | docs checks below |
| Package landing page on PyPI | `packages/<package>/README.md` | package build/smoke for that package |
| Adopter maturity | `docs/guides/whats-ready.md` | `check_docs_train_ssot.py` |
| Component reference page | entry in `scripts/generate_component_docs.py` | generator with `--check` |
| Interactive docs simulation | `docs/demos/*.py` and its runnable source | simulation generator and recipe sync |
| Recipe Code tab | marked source under `docs/demos/runnable/` | `check_recipe_code_sync.py` |
| STATUS / ROADMAP | `docs/STATUS.md`, `docs/ROADMAP.md` | `sync_status_roadmap.py`, then `--check` |
| Release procedure | `docs/RELEASE.md` | current release-gate checks |

Generated component pages and generated simulation HTML are outputs. Change their source
and regenerate them; do not hand-edit output that the next generator run will overwrite.

## Editorial rules

- Lead with the outcome or decision. Put prerequisites before commands.
- Use the exact supported Python and package ranges; distinguish **declared** dependency
  ranges from the narrower **CI-supported** ranges.
- Before calling a distribution "published" or documenting an extra, verify the live
  registry version and `Requires-Dist` metadata—not only the local `pyproject.toml`.
- Keep package maturity, capability readiness, and API stability separate. See
  [Understanding maturity labels](../getting-started/how-to-read.md).
- Use **Supported**, **Experimental**, **Alpha**, and **Deferred** only with the meanings
  on [What's ready today](whats-ready.md).
- State ownership explicitly: Hedron does not supply application authorization,
  persistence, tenancy, a hosted service, or a commercial SLA.
- Prefer plain language in adopter docs. Explain a behavior first; place internal gate or
  decision identifiers in maintainer evidence, release history, or a secondary link.
- Keep examples copy-pasteable. Include imports, environment assumptions, expected output,
  and the next command or browser action.
- Document failure behavior. Public API reference should name raised exceptions or HTTP
  status/error codes, not only the happy-path return value.
- Avoid duplicating current-version claims. Link to the canonical page when a second copy
  would create another release-time edit.

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

## Local verification

For a normal docs change:

```bash
uv sync --group docs
uv run python scripts/check_docs_train_ssot.py
uv run python scripts/check_recipe_code_sync.py
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
- [ ] Expected output or browser behavior is stated.
- [ ] Errors, security boundaries, and production caveats are present where relevant.
- [ ] Version, maturity, and support claims match their canonical pages.
- [ ] Published install commands resolve against live registry metadata in a clean environment.
- [ ] New public APIs appear in the coverage map and have reference documentation.
- [ ] New built-ins have generated component pages and composition tests.
- [ ] Relative links resolve and the strict MkDocs build passes.
- [ ] Generated outputs were updated from their owning source.

See also: [Contributing](../CONTRIBUTING.md) ·
[Maintainer handbook](maintainer-handbook.md) ·
[API coverage map](../api/COVERAGE.md)
