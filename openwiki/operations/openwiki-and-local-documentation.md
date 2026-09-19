---
type: workflow
title: OpenWiki and Local Documentation
description: Local Codex integration, generated wiki artifacts, and the freshness gate that keeps documentation aligned with source.
tags:
  - openwiki
  - documentation
  - operations
sources:
  - id: openwiki-source-6e185c967022a3074c354910
    resource: repo://.agents/skills/openwiki/.openwiki-install.json
  - id: openwiki-source-0f2091252a9c3383cef44ad0
    resource: repo://.agents/skills/openwiki/SKILL.md
  - id: openwiki-source-ab585d88aca3958f2aa6a541
    resource: repo://.codex/config.toml
  - id: openwiki-source-e119253b3c3737247dc63f2a
    resource: repo://.openwikiignore
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
  - id: openwiki-source-76f1c5b345f97c02d0989b38
    resource: repo://scripts/check_openwiki_freshness.py
  - id: openwiki-source-2faef51cd0bcbe4bb5eaae2d
    resource: repo://scripts/ci_checks.sh
  - id: openwiki-source-4c56c4085c56a3ab75df5178
    resource: repo://scripts/README.md
generated: { by: "codex", at: "2026-09-19T19:14:00.347Z" }
verified:
  - by: openwiki/0.5.2
    at: 2026-09-19T19:14:00.347Z
---

# OpenWiki and Local Documentation

Hedron uses OpenWiki as a project-scoped, local documentation index for coding
agents. The Codex MCP configuration in `.codex/config.toml` starts the pinned
OpenWiki integration, while `.agents/skills/openwiki/` supplies the repository
workflow instructions. The generated `openwiki/` tree is complementary to
user-facing README and contributor documentation: it explains architecture,
boundaries, workflows, and source navigation rather than replacing API docs.

## Update lifecycle

An update begins by resolving the Git top-level and calling OpenWiki's durable
`openwiki_begin` lifecycle in `update` mode. The host plans canonical pages,
then repeatedly receives one page job at a time. For each job, Codex researches
the assigned source and tests, writes only that Markdown page, and submits
sparse Claim decisions. OpenWiki retains issue-free Claims, records new or
revised Claims in sidecars, regenerates indexes and provenance, and finalizes
the run only after every page job succeeds.

OpenWiki owns `.claims/`, `.run.json`, `.last-update.json`, manifest metadata,
indexes, logs, provenance, and integration setup blocks. Those files are not
hand-edited. If source changes make the generated wiki stale, update it through
the Codex OpenWiki integration, then run the local check again. The
`.openwikiignore` file keeps Git metadata, environments, caches, build output,
dependencies, databases, and other local artifacts outside the source boundary
used for documentation freshness. This repository also ignores the
host-managed `AGENTS.md` and `CLAUDE.md` setup files; they are integration
metadata rather than source documentation inputs.

## Freshness contract

`scripts/check_openwiki_freshness.py` is deterministic and read-only. Its
source fingerprint mirrors OpenWiki's `openwiki-source-fingerprint-v1`: it
includes the Git HEAD, visible Git status, and visible tracked/untracked paths
and bytes, while excluding the generated `openwiki/` tree and paths matched by
`.openwikiignore`, including the host-managed agent instruction files. This
means an uncommitted source or documentation edit outside that ignore boundary
is intentionally visible to the gate.

The checker then verifies that the last OpenWiki run completed at the current
Git HEAD; the page manifest covers exactly the factual Markdown pages on disk;
each manifest entry has the current fingerprint and HEAD; each Markdown
`pageVersion` matches its bytes; and every Claims sidecar has the expected
schema, matching page version, verification metadata, and at least one grounded
Claim. When a completed run observed a dirty worktree and the update is then
recorded in a clean descendant commit, the checker replays that committed
source snapshot so the commit itself does not make an otherwise unchanged wiki
stale. New source edits or a later commit still require another OpenWiki update.
It does not call a model, mutate the wiki, or contact a service.

Run the focused gate with:

```bash
bash scripts/ci_checks.sh openwiki --python 3.12
```

The `all` suite invokes the same gate before the expensive local test,
quality, browser, evidence, and packaging suites. A failure is a documentation
freshness failure, not a request to bypass the check: refresh OpenWiki in Codex
and rerun the command. This integration is deliberately local-only; the
repository has no GitHub Actions workflow for OpenWiki and the local gate is not
called by GitHub Actions.

See [Quality and Release Workflow](quality-and-release.md) for the surrounding
checks and [Quickstart](../quickstart.md) for the agent-oriented entry points.
