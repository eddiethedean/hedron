#!/usr/bin/env python3
"""Protect the public adoption path from high-impact documentation drift."""

from __future__ import annotations

from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(relative: str, needle: str) -> None:
    if needle not in read(relative):
        raise SystemExit(f"{relative} must contain: {needle!r}")


def forbid(relative: str, needle: str) -> None:
    if needle in read(relative):
        raise SystemExit(f"{relative} contains stale or unsafe text: {needle!r}")


def main() -> int:
    release_data = tomllib.loads(read("docs/release.toml"))["release"]
    current = str(release_data["published_version"])
    bounded = f'>={release_data["pin_floor"]},<{release_data["pin_ceiling"]}'
    exact = f"=={current}"

    # The docs must describe what the default FastAPI scaffold actually writes.
    require(
        "packages/hedron/src/hedron/cli/scaffold/fastapi.py",
        '"files": ["pyproject.toml", "app.py", "components/"]',
    )
    require(
        "packages/hedron/src/hedron/cli/commands/new.py",
        '(dest / "components").mkdir(exist_ok=True)',
    )
    require("docs/getting-started/quickstart.md", "└── components/")
    forbid("docs/getting-started/quickstart.md", "Created later when")
    require("docs/guides/deployment.md", "COPY pyproject.toml app.py ./")
    require("docs/guides/deployment.md", "COPY components ./components")
    forbid("docs/guides/deployment.md", "COPY pyproject.toml README.md app.py ./")

    # Proxy examples must not teach blanket trust or globally apply SSE tuning.
    forbid("docs/guides/deployment.md", "--forwarded-allow-ips='*'")
    forbid("docs/guides/deployment.md", '--forwarded-allow-ips="*"')
    require("docs/guides/deployment.md", "actual proxy IP or CIDR")
    require("docs/guides/deployment.md", "location /events/ {")
    require("docs/guides/deployment.md", "@events path /events/*")

    # Current release language distinguishes compatibility, recommendation, and lock.
    for relative in (
        "README.md",
        "docs/getting-started/installation.md",
        "docs/guides/current-release.md",
    ):
        require(relative, ">=1.0.0")
        require(relative, bounded)
        require(relative, exact)
    forbid("docs/guides/release-summary.md", f"editable {current} workspace")
    forbid("docs/guides/versions.md", "pre-1.0")

    # Primary navigation must expose the product choice and governance/version context.
    require("mkdocs.yml", "edit_uri: edit/main/docs/")
    require("mkdocs.yml", "Choose Hedron or Edron: getting-started/choose-layer.md")
    require("mkdocs.yml", "Governance: guides/governance.md")
    require("mkdocs.yml", "Versioned documentation: guides/versions.md")

    # Known maturity and diligence contradictions must not return.
    forbid("docs/CONTRIBUTING.md", "`hedron[charts]`, Beta")
    forbid("docs/ARCHITECTURE.md", "stable Flask adapter")
    forbid("docs/ARCHITECTURE.md", "stable Django >=5.2,<6 adapter")
    forbid("docs/guides/why-hedron.md", "`0.x` Beta pinning")
    forbid("docs/guides/enterprise-diligence.md", "\nwhen they are attached")
    require("docs/guides/faq.md", bounded)
    require("docs/guides/faq.md", exact)
    forbid("docs/guides/faq.md", "Packages are Beta")
    require("mkdocs.yml", "FAQ: guides/faq.md")
    forbid("docs/api/SYMBOL_TIERS.md", "foundation for an honest 1.0 freeze")
    forbid("docs/api/INTERACTION.md", "Phase 0.61 in-tree preview")
    forbid("docs/api/BUILT_INS.md", "Phase 0.61 in-tree preview")

    print("ok: public adoption documentation matches scaffold, release, nav, and proxy contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
