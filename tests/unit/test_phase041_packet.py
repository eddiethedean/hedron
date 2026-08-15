import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_phase041_packet_and_gates() -> None:
    gate = tomllib.loads((ROOT / "docs/acceptance/release-gate-0.41.toml").read_text())
    assert [row["id"] for row in gate["evidence"]] == [
        "COMPOSE-041",
        "STATE-041",
        "NAV-041",
        "TRACE-041",
        "FALLBACK-041",
        "BROWSER-041",
        "REGRESS-041",
        "PKG-041",
    ]
    for path in (
        "docs/acceptance/RELEASE_0_41.md",
        "docs/implementation/HEDRON_COMPOSITION_041.md",
        "docs/acceptance/upgrade-fixtures-041.md",
        "docs/acceptance/security-review-041/BRIEF.md",
    ):
        assert (ROOT / path).is_file()
