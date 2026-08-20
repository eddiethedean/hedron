"""Third-party runtime author kit helpers and intentional-failure diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from hedron_conformance.compat import (
    CompatibilityDecision,
    check_contract_version,
    check_fixture_version,
    compatibility_policy_dict,
)
from hedron_conformance.schema import (
    CONTRACT_VERSION,
    FIXTURE_VERSION,
    Capability,
    load_bundled_fixtures,
)

AUTHOR_KIT_VERSION = "0.52.0"


@dataclass(frozen=True, slots=True)
class AuthorKitDiagnostic:
    code: str
    message: str
    ok: bool = False


def author_kit_dir() -> Path:
    root = resources.files("hedron_conformance").joinpath("author_kit")
    return Path(str(root))


def author_kit_readme() -> str:
    path = author_kit_dir() / "README.md"
    return path.read_text(encoding="utf-8")


def validate_author_manifest(
    contract_version: str, fixture_version: str
) -> list[AuthorKitDiagnostic]:
    """Validate versions a third-party runtime claims to implement."""
    out: list[AuthorKitDiagnostic] = []
    for decision in (
        check_contract_version(contract_version),
        check_fixture_version(fixture_version),
    ):
        out.append(
            AuthorKitDiagnostic(code=decision.code, message=decision.message, ok=decision.ok)
        )
    return out


def intentional_failure_examples() -> list[AuthorKitDiagnostic]:
    """Stable diagnostics authors should emit for common misconfigurations."""
    bad_contract = check_contract_version("hedron-portable-99")
    bad_fixture = check_fixture_version("9.0.0")
    empty = load_bundled_fixtures()
    return [
        AuthorKitDiagnostic(code=bad_contract.code, message=bad_contract.message, ok=False),
        AuthorKitDiagnostic(code=bad_fixture.code, message=bad_fixture.message, ok=False),
        AuthorKitDiagnostic(
            code="CONF-AUTHOR-EMPTY-CORPUS",
            message="runtime produced zero fixture results; ensure portable fixtures are loaded",
            ok=False,
        ),
        AuthorKitDiagnostic(
            code="CONF-AUTHOR-CORPUS-HINT",
            message=(
                f"bundled corpus has {len(empty)} fixtures; "
                f"pin contract={CONTRACT_VERSION} fixture={FIXTURE_VERSION}"
            ),
            ok=True,
        ),
    ]


def declared_capabilities() -> list[str]:
    """Capability labels third parties may declare without a monorepo import."""
    return [cap.value for cap in Capability]


def author_kit_summary() -> dict[str, object]:
    readme = author_kit_readme()
    return {
        "author_kit_version": AUTHOR_KIT_VERSION,
        "policy": compatibility_policy_dict(),
        "readme_present": (author_kit_dir() / "README.md").is_file(),
        "template_present": (author_kit_dir() / "runtime_template.md").is_file(),
        "declares_capability_without_monorepo": "Capability" in readme
        and "monorepo" in readme.lower(),
        "declared_capabilities": declared_capabilities(),
        "intentional_failures": [
            {"code": item.code, "message": item.message, "ok": item.ok}
            for item in intentional_failure_examples()
        ],
    }


# Re-export for author convenience.
__all__ = [
    "AUTHOR_KIT_VERSION",
    "AuthorKitDiagnostic",
    "CompatibilityDecision",
    "author_kit_dir",
    "author_kit_readme",
    "author_kit_summary",
    "compatibility_policy_dict",
    "declared_capabilities",
    "intentional_failure_examples",
    "validate_author_manifest",
]
