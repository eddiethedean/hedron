#!/usr/bin/env python3
"""Validate adopter documentation against ``docs/release.toml``.

The check deliberately derives every release value from structured metadata. It does
not enumerate old versions: a future train changes ``docs/release.toml`` and stale
"current", "living", published-version, and install-pin claims fail automatically.
Historical release pages may describe their own versions, but they must not call them
current or living.
"""

from __future__ import annotations

import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_FILE = ROOT / "docs" / "release.toml"


@dataclass(frozen=True, slots=True)
class ReleaseFacts:
    train: str
    published_version: str
    development_version: str
    pin_floor: str
    pin_ceiling: str
    previous_train: str
    previous_version: str
    previous_security_until: str
    satellite_minimum: str
    satellite_maximum: str

    @property
    def pin(self) -> str:
        return f">={self.pin_floor},<{self.pin_ceiling}"

    @property
    def train_line(self) -> str:
        return f"{self.train}.x"


def load_release_facts(path: Path = RELEASE_FILE) -> ReleaseFacts:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    release = data["release"]
    satellites = data["satellites"]
    return ReleaseFacts(
        train=release["train"],
        published_version=release["published_version"],
        development_version=release["development_version"],
        pin_floor=release["pin_floor"],
        pin_ceiling=release["pin_ceiling"],
        previous_train=release["previous_train"],
        previous_version=release["previous_version"],
        previous_security_until=release["previous_security_until"],
        satellite_minimum=satellites["minimum_version"],
        satellite_maximum=satellites["maximum_version"],
    )


FACTS = load_release_facts()

# Markdown emphasis / code ticks often wrap the version token.
_MD_GAP = r"(?:[\s*`*_])*"
CURRENT_CLAIM_VERSION = re.compile(
    r"(?:"
    # current/living train … then version (or last published … version)
    r"\b(?:"
    r"current(?:ly)?(?:\s+published)?\s+(?:train|line|version|release)|"
    r"living(?:\s+published)?\s+(?:train|line|version|release)|"
    r"last\s+(?:published|PyPI/git)|"
    r"published/latest"
    r")[^\n]{0,100}?v?(0\.\d+(?:\.\d+)?(?:\.x)?)"
    r"|"
    # living/current **0.26** train (version before train|line)
    rf"\b(?:current(?:ly)?|living)(?:\s+published)?{_MD_GAP}"
    rf"v?(0\.\d+(?:\.\d+)?(?:\.x)?){_MD_GAP}(?:train|line)\b"
    r"|"
    # tip-hub "last **v0.26.0**" (bold version; avoids phase "last `v0.25.2`" rows)
    rf"\blast{_MD_GAP}\*\*v?(0\.\d+(?:\.\d+)?(?:\.x)?)\*\*"
    r")",
    re.I,
)
INSTALL_LINE = re.compile(r"\b(?:pip(?:3)?\s+install|uv\s+add|uvx\b)", re.I)
HEDRON_REQUIREMENT = re.compile(
    r"(?<![\w-])(?P<name>hedron-(?:flask|django|core|data|explorer|jinja|conformance|"
    r"extras)(?:\[[^\]]+\])?|hedron(?:\[[^\]]+\])?)"
    r"(?P<constraint>>=[0-9.]+(?:,<[0-9.]+)?)?(?=[\"'\s]|$)",
    re.I,
)
SATELLITE_REQUIREMENT = re.compile(
    r"(?<![\w-])(?P<name>hedron-charts(?:\[[^\]]+\])?|hedron-sample-kit)"
    r"(?P<constraint>>=[0-9.]+(?:,<[0-9.]+)?)?",
    re.I,
)
MATURITY_COLLISION = re.compile(r"Supported beta|Maturity SSOT|beachhead Supported", re.I)

PUBLIC_DOC_EXCLUDES = {
    "archive",
    "rfcs",
    "acceptance",
    "foundations",
    "implementation",
}
INTERNAL_DOC_NAMES = {
    "ACCESSIBILITY_FEATURE_RESEARCH.md",
    "DECISIONS.md",
    "DJANGO_ADAPTER_RESEARCH.md",
    "ENGINEERING_BASELINE.md",
    "FLASK_ADAPTER_RESEARCH.md",
    "GRADIO_FEATURE_CROSSCHECK.md",
    "HTMX_2_AUDIT.md",
    "HTMX_2_EXTENSIONS.md",
    "NICEGUI_FEATURE_CROSSCHECK.md",
    "PERFORMANCE_BUDGETS.md",
    "PLOTLY_DASH_FEATURE_CROSSCHECK.md",
    "READINESS_REPORT.md",
    "ROADMAP.md",
    "STATUS.md",
    "STREAMLIT_EXTRAS_FEATURE_CROSSCHECK.md",
    "STREAMLIT_FEATURE_CROSSCHECK.md",
    "TRACEABILITY.md",
}
HISTORICAL_PREFIXES = ("whats-new-0.", "RELEASE_0_")


def _is_historical(path: Path) -> bool:
    return (
        any(part in PUBLIC_DOC_EXCLUDES for part in path.parts)
        or path.name in INTERNAL_DOC_NAMES
        or path.name.startswith(HISTORICAL_PREFIXES)
    )


def adopter_files() -> list[Path]:
    files = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "SECURITY.md"]
    files.extend(sorted((ROOT / "docs").rglob("*.md")))
    files.extend(sorted((ROOT / "packages").glob("*/README.md")))
    files.extend(sorted((ROOT / "examples").glob("*/README.md")))
    return [path for path in files if path.is_file() and not _is_historical(path)]


def _normalized_version(value: str) -> str:
    return value[:-2] if value.endswith(".x") else value


def _version_matches_current(value: str, facts: ReleaseFacts) -> bool:
    value = _normalized_version(value)
    return value in {facts.train, facts.published_version}


def _line_allows_previous_support(line: str, facts: ReleaseFacts) -> bool:
    lower = line.lower()
    return facts.previous_train in line and any(
        phrase in lower
        for phrase in (
            "previous",
            "prior",
            "best-effort",
            "security triage",
            "upgrade from",
            "upgrading from",
        )
    )


def check_text(path: Path, text: str, facts: ReleaseFacts = FACTS) -> list[str]:
    failures: list[str] = []
    lines = text.splitlines()
    for index, line in enumerate(lines, start=1):
        for claim in CURRENT_CLAIM_VERSION.finditer(line):
            value = next((group for group in claim.groups() if group), None)
            if value is None:
                continue
            if not _version_matches_current(value, facts) and not _line_allows_previous_support(
                line, facts
            ):
                failures.append(
                    f"{path}:{index}: current/living claim uses {value}; "
                    f"expected {facts.train_line} or v{facts.published_version}"
                )

        if MATURITY_COLLISION.search(line):
            failures.append(f"{path}:{index}: ambiguous maturity phrase: {line.strip()}")

        if not INSTALL_LINE.search(line) or re.search(
            r"\b(?:not available|do not|don't|never|failed with)\b", line, re.I
        ):
            continue

        for match in HEDRON_REQUIREMENT.finditer(line):
            constraint = match.group("constraint") or ""
            prefix = line[: match.start()]
            is_requirement_position = bool(
                re.search(r"(?:pip(?:3)?\s+install|uv\s+add|--from)\s+[\"']?$", prefix, re.I)
            )
            if not constraint and not is_requirement_position:
                continue
            if constraint != facts.pin:
                failures.append(
                    f"{path}:{index}: install for {match.group('name')} must use "
                    f"{facts.pin}; found {constraint or 'no version constraint'}"
                )

        for match in SATELLITE_REQUIREMENT.finditer(line):
            expected = f">={facts.satellite_minimum},<{facts.satellite_maximum}"
            constraint = match.group("constraint") or ""
            prefix = line[: match.start()]
            is_requirement_position = bool(
                re.search(r"(?:pip(?:3)?\s+install|uv\s+add|--from)\s+[\"']?$", prefix, re.I)
            )
            if not constraint and not is_requirement_position:
                continue
            if constraint != expected:
                failures.append(
                    f"{path}:{index}: install for {match.group('name')} must use "
                    f"{expected}; found {constraint or 'no version constraint'}"
                )
    return failures


def _has_compatible_satellite_floor(line: str, facts: ReleaseFacts = FACTS) -> bool:
    flagship = f"hedron[charts]{facts.pin}"
    satellite = f">={facts.satellite_minimum},<{facts.satellite_maximum}"
    checks: list[bool] = []
    if "hedron[charts]" in line:
        checks.append(flagship in line)
    if "hedron-charts" in line:
        checks.append(
            f"hedron-charts{satellite}" in line or "hedron-charts[" in line and satellite in line
        )
    if "hedron-sample-kit" in line:
        checks.append(f"hedron-sample-kit{satellite}" in line)
    return bool(checks) and all(checks)


UNBOUNDED_CHARTS_PKG = re.compile(
    rf"hedron-charts(?:\[[^\]]+\])?>={re.escape(FACTS.satellite_minimum)}"
    rf"(?!,<{re.escape(FACTS.satellite_maximum)})"
)


def check_metadata(facts: ReleaseFacts = FACTS) -> list[str]:
    failures: list[str] = []
    workspace = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    if workspace["version"] != facts.development_version:
        failures.append(
            "docs/release.toml development_version does not match workspace pyproject.toml"
        )
    changelog = (ROOT / "packages" / "hedron" / "CHANGELOG.md").read_text(encoding="utf-8")
    for version in (facts.published_version, facts.development_version):
        if f"## [{version}]" not in changelog:
            failures.append(f"packages/hedron/CHANGELOG.md has no [{version}] section")
    if not facts.published_version.startswith(f"{facts.train}."):
        failures.append("published_version is not on the configured release train")
    if facts.pin_floor != facts.published_version:
        failures.append("pin_floor must equal published_version")
    return failures


def main() -> int:
    failures = check_metadata()
    for path in adopter_files():
        relative = path.relative_to(ROOT)
        failures.extend(check_text(relative, path.read_text(encoding="utf-8")))
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(
        f"ok: adopter docs agree with published v{FACTS.published_version}, "
        f"train {FACTS.train_line}, pin {FACTS.pin}, and satellite floor "
        f">={FACTS.satellite_minimum},<{FACTS.satellite_maximum}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
