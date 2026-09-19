# Hedron OpenWiki instructions

Document Hedron as a Python monorepo for agents who need to understand its
architecture, public APIs, package boundaries, and development workflows.

Prioritize meaningful systems and end-to-end flows over file inventories. Cover
the core component and rendering model, request and interaction lifecycles,
package and adapter boundaries, data and background-work surfaces, security
contracts, and the tests and release checks that protect them. Treat the
published support matrix, package READMEs, and existing documentation as useful
context, but ground factual claims in current source and focused tests.

Keep the generated wiki complementary to the existing user-facing documentation:
the wiki should help coding agents navigate and change the repository, while
linking to canonical docs for detailed API reference and release guidance.

The local check contract is part of this repository's documentation workflow:
`bash scripts/ci_checks.sh openwiki --python 3.12` verifies the OpenWiki source
fingerprint, page manifest, Markdown bytes, and verified Claims. The `all` suite
runs that check first. It is deliberately local-only; do not add a GitHub Actions
workflow for OpenWiki. When source changes make the check fail, update the wiki
through the OpenWiki Codex integration and rerun the check.
