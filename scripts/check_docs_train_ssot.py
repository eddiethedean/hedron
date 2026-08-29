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
from dataclasses import dataclass
from pathlib import Path

from hedron_core.compat import tomllib

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
    pypi_version: str
    pypi_pin_floor: str
    pypi_pin_ceiling: str
    registry_status: str
    edron_published_version: str
    edron_development_version: str
    edron_pin_floor: str
    edron_pin_ceiling: str
    edron_pypi_version: str
    edron_pypi_pin_floor: str
    edron_pypi_pin_ceiling: str
    edron_registry_status: str
    satellite_minimum: str
    satellite_maximum: str
    charts_minimum: str
    charts_maximum: str

    @property
    def pin(self) -> str:
        return f">={self.pin_floor},<{self.pin_ceiling}"

    @property
    def pypi_pin(self) -> str:
        return f">={self.pypi_pin_floor},<{self.pypi_pin_ceiling}"

    @property
    def train_line(self) -> str:
        return f"{self.train}.x"

    @property
    def pypi_train_line(self) -> str:
        parts = self.pypi_version.split(".")
        return f"{parts[0]}.{parts[1]}.x" if len(parts) >= 2 else f"{self.pypi_version}.x"

    @property
    def registry_deferred(self) -> bool:
        return self.registry_status == "deferred"

    @property
    def sample_kit_pin(self) -> str:
        return f">={self.satellite_minimum},<{self.satellite_maximum}"

    @property
    def charts_pin(self) -> str:
        return f">={self.charts_minimum},<{self.charts_maximum}"

    @property
    def edron_pin(self) -> str:
        return f">={self.edron_pin_floor},<{self.edron_pin_ceiling}"

    @property
    def edron_pypi_pin(self) -> str:
        return f">={self.edron_pypi_pin_floor},<{self.edron_pypi_pin_ceiling}"


def load_release_facts(path: Path = RELEASE_FILE) -> ReleaseFacts:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    release = data["release"]
    edron = data["edron"]
    satellites = data["satellites"]
    published = str(release["published_version"])
    return ReleaseFacts(
        train=release["train"],
        published_version=published,
        development_version=release["development_version"],
        pin_floor=release["pin_floor"],
        pin_ceiling=release["pin_ceiling"],
        previous_train=release["previous_train"],
        previous_version=release["previous_version"],
        previous_security_until=release["previous_security_until"],
        pypi_version=str(release.get("pypi_version") or published),
        pypi_pin_floor=str(release.get("pypi_pin_floor") or release["pin_floor"]),
        pypi_pin_ceiling=str(release.get("pypi_pin_ceiling") or release["pin_ceiling"]),
        registry_status=str(release.get("registry_status") or "uploaded"),
        edron_published_version=str(edron["published_version"]),
        edron_development_version=str(edron["development_version"]),
        edron_pin_floor=str(edron["pin_floor"]),
        edron_pin_ceiling=str(edron["pin_ceiling"]),
        edron_pypi_version=str(edron["pypi_version"]),
        edron_pypi_pin_floor=str(edron.get("pypi_pin_floor") or edron["pin_floor"]),
        edron_pypi_pin_ceiling=str(edron.get("pypi_pin_ceiling") or edron["pin_ceiling"]),
        edron_registry_status=str(edron.get("registry_status") or "uploaded"),
        satellite_minimum=satellites["minimum_version"],
        satellite_maximum=satellites["maximum_version"],
        charts_minimum=str(satellites.get("charts_minimum_version") or "0.2.0"),
        charts_maximum=str(satellites.get("charts_maximum_version") or "0.3"),
    )


FACTS = load_release_facts()

# Markdown emphasis / code ticks often wrap the version token.
_MD_GAP = r"(?:[\s*`*_])*"
CURRENT_CLAIM_VERSION = re.compile(
    r"(?:"
    # current/living train … then version (or last published … version)
    r"\b(?:"
    r"current(?:ly)?(?:\s+published)?\s+(?:train|line|version|release|tip|train\s+tag)|"
    r"living(?:\s+published)?\s+(?:train|line|version|release)|"
    r"last\s+(?:published|PyPI/git)|"
    r"published/latest"
    r")[^\n]{0,100}?v?(\d+\.\d+(?:\.\d+)?(?:\.x)?)"
    r"|"
    # living/current **0.26** train (version before train|line)
    rf"\b(?:current(?:ly)?|living)(?:\s+published)?{_MD_GAP}"
    rf"v?(\d+\.\d+(?:\.\d+)?(?:\.x)?){_MD_GAP}(?:train|line)\b"
    r"|"
    # tip-hub "last **v0.26.0**" (bold version; avoids phase "last `v0.25.2`" rows)
    rf"\blast{_MD_GAP}\*\*v?(\d+\.\d+(?:\.\d+)?(?:\.x)?)\*\*"
    r")",
    re.I,
)
CURRENT_PIN_CLAIM = re.compile(
    r"\b(?:current(?:ly)?|living)[^\n]{0,100}?"
    r"hedron(?:\[[^\]]+\])?(>=\d+(?:\.\d+){1,2},<\d+(?:\.\d+){1,2})",
    re.I,
)
INSTALL_LINE = re.compile(r"\b(?:pip(?:3)?\s+install|uv\s+add|uvx\b)", re.I)
HEDRON_REQUIREMENT = re.compile(
    r"(?<![\w-])(?P<name>hedron-(?:flask|django|core|data|explorer|jinja|conformance|"
    r"extras)(?:\[[^\]]+\])?|hedron(?:\[[^\]]+\])?)"
    r"(?P<constraint>>=[0-9.]+(?:,<[0-9.]+)?)?(?=[\"'\s]|$)",
    re.I,
)
EDRON_REQUIREMENT = re.compile(
    r"(?<![\w-])(?P<name>edron(?:\[[^\]]+\])?)"
    r"(?P<constraint>>=[0-9.]+(?:,<[0-9.]+)?)?(?=[\"'\s]|$)",
    re.I,
)
SATELLITE_REQUIREMENT = re.compile(
    r"(?<![\w-])(?P<name>hedron-charts(?:\[[^\]]+\])?|hedron-sample-kit)"
    r"(?P<constraint>>=[0-9.]+(?:,<[0-9.]+)?)?",
    re.I,
)
MATURITY_COLLISION = re.compile(r"Supported beta|Maturity SSOT|beachhead Supported", re.I)
CURRENT_TRAIN_MENTION = re.compile(
    r"\b(?:current(?:ly)?|living)(?:\s+published)?\s+(?:train|line)\b|"
    rf"\b(?:current(?:ly)?|living){_MD_GAP}\d+\.\d+",
    re.I,
)
PYPI_VERSION_CLAIM = re.compile(
    r"(?:"
    r"(?<!\blast published\s)"
    r"(?:\*\*published\*\*|\bpublished\s+as\b|\bon pypi\b|\bpypi\b)"
    r"[^\n]{0,80}?[`'\"*]*v?(\d+\.\d+\.\d+)"
    r"|"
    r"[`'\"*]*v?(\d+\.\d+\.\d+)[^\n]{0,40}?\bon pypi\b"
    r")",
    re.I,
)
TRAIN_LABEL = re.compile(r"\b(\d+\.\d+(?:\.\d+)?)\s+train\b", re.I)

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

# Implementation claims are independent of registry state: a verified release
# must never be described as unimplemented, and the malformed ``.1.0.x`` token
# is not a valid train label under either state.
IMPLEMENTATION_CONTRADICTION = re.compile(
    r"(?:"
    r"\b1\.0(?:\.0|\.x)?[^\n]{0,120}\b(?:not implemented|implementation pending|"
    r"release evidence pending)\b|"
    r"(?<!\d)\.1\.0\.x\b"
    r")",
    re.IGNORECASE,
)
DEFERRED_REGISTRY_CONTRADICTION = re.compile(
    r"\bv?1\.0\.0\b[^\n]{0,100}\b(?:on PyPI|published on PyPI|in-tree and on PyPI)\b",
    re.IGNORECASE,
)
PUBLISHED_RELEASE_CONTRADICTION = re.compile(
    r"\bv?1\.0\.0\b[^\n]{0,100}\b(?:release candidate|candidate|publication pending|"
    r"tag/PyPI deferred|upload deferred)\b",
    re.IGNORECASE,
)
HISTORICAL_RELEASE_BANNER = "Historical release note"
SECTION_LANDINGS = {
    Path("docs/index.md"): "guides/current-release.md",
    Path("docs/getting-started/index.md"): "installation.md",
    Path("docs/guides/index.md"): "current-release.md",
    Path("docs/examples/index.md"): "../guides/current-release.md",
    Path("docs/api/README.md"): "../guides/current-release.md",
    Path("docs/packages/index.md"): "installation.md",
    Path("docs/components/index.md"): "../guides/current-release.md",
}


def _is_historical(path: Path) -> bool:
    return (
        any(part in PUBLIC_DOC_EXCLUDES for part in path.parts)
        or path.name in INTERNAL_DOC_NAMES
        or path.name.startswith(HISTORICAL_PREFIXES)
    )


def check_release_candidate_status(
    path: Path,
    text: str,
    facts: ReleaseFacts = FACTS,
) -> list[str]:
    """Reject stale implementation and registry claims on maintained pages.

    Implementation status is always checked. Registry language is then
    validated against ``facts.registry_status`` so a deferred candidate cannot
    be called published and an uploaded release cannot still be called pending.
    """
    if _is_historical(path):
        return []
    failures: list[str] = []
    for index, line in enumerate(text.splitlines(), start=1):
        registry_pattern = (
            DEFERRED_REGISTRY_CONTRADICTION
            if facts.registry_deferred
            else PUBLISHED_RELEASE_CONTRADICTION
        )
        deferred_not_published = bool(
            facts.registry_deferred
            and re.search(
                r"\bnot\s+(?:yet\s+)?on\s+pypi\b|\bpublication\s+is\s+deferred\b", line, re.I
            )
        )
        if IMPLEMENTATION_CONTRADICTION.search(line) or (
            registry_pattern.search(line) and not deferred_not_published
        ):
            failures.append(f"{path}:{index}: contradictory 1.0 candidate status: {line.strip()}")
    return failures


def check_historical_release_banner(path: Path, text: str) -> list[str]:
    """Historical What's New pages must point readers back to the living SSOT."""
    required = (HISTORICAL_RELEASE_BANNER, "current-release.md")
    missing = [marker for marker in required if marker not in text]
    if not missing:
        return []
    return [f"{path}: historical release page is missing {', '.join(missing)}"]


def check_section_landing(
    path: Path,
    text: str,
    facts: ReleaseFacts = FACTS,
) -> list[str]:
    """Every reader-facing section landing must expose its 1.0 release context."""
    target = SECTION_LANDINGS.get(path)
    if target is None:
        return []
    required = (facts.train, target)
    missing = [marker for marker in required if marker not in text]
    if not missing:
        return []
    return [f"{path}: section landing is missing {', '.join(missing)}"]


def adopter_files() -> list[Path]:
    files = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "SECURITY.md"]
    files.extend(sorted((ROOT / "docs").rglob("*.md")))
    files.extend(sorted((ROOT / "packages").glob("*/README.md")))
    files.extend(sorted((ROOT / "examples").glob("*/README.md")))
    return [path for path in files if path.is_file() and not _is_historical(path)]


def _normalized_version(value: str) -> str:
    return value[:-2] if value.endswith(".x") else value


def _train_minor(value: str) -> str:
    normalized = _normalized_version(value)
    parts = normalized.split(".")
    return f"{parts[0]}.{parts[1]}" if len(parts) >= 2 else normalized


def _is_inventory_page(path: Path) -> bool:
    return (path.parts[:2] == ("docs", "packages")) or (
        len(path.parts) == 2 and path.parts[0] == "packages" and path.name == "README.md"
    )


CANONICAL_INSTALL_PAGE = Path("docs/getting-started/installation.md")

# The Posit adapter is released on the beta 0.67 train, so its Workbench
# walkthroughs intentionally use the matching Hedron bridge rather than the
# stable public 0.66 pin used by general-purpose beginner pages.
POSIT_WORKBENCH_PATHS = frozenset(
    {
        Path("docs/getting-started/first-app-posit-workbench.md"),
        Path("docs/guides/training-streamlit-to-hedron-posit.md"),
    }
)

# Pages whose pip/uv/uvx lines must be registry-resolvable. While the upload is
# deferred, that is the public-index pin — never the unpublished in-tree pin.
# PyPI-lag honesty lives on REGISTRY_HONESTY_PATHS, not on these pages.
FIRST_RUN_INSTALL_PATHS = frozenset(
    {
        Path("README.md"),
        Path("docs/index.md"),
        Path("docs/getting-started/quickstart.md"),
        Path("docs/guides/faq.md"),
        Path("docs/examples/try-it.md"),
        Path("docs/getting-started/how-to-read.md"),
    }
)

# Deferred-upload honesty lives here — not on every first-run page.
REGISTRY_HONESTY_PATHS = frozenset(
    {
        CANONICAL_INSTALL_PAGE,
        Path("packages/hedron/README.md"),
        Path("packages/hedron-core/README.md"),
    }
)

# Tip / checkout language must match published_version on these living pages.
TIP_HONESTY_PATHS = frozenset(
    {
        *REGISTRY_HONESTY_PATHS,
        Path("README.md"),
        Path("docs/guides/current-release.md"),
        Path("docs/guides/whats-ready.md"),
        Path("docs/guides/whats-ready-evidence.md"),
        Path("docs/guides/evaluate.md"),
        Path("docs/guides/upgrade.md"),
        Path("docs/guides/production-quality.md"),
        Path("docs/STATUS.md"),
        Path("STATUS.md"),
    }
)

BOILERPLATE_ALLOWED_PATHS = frozenset(
    {
        *REGISTRY_HONESTY_PATHS,
        Path("docs/guides/release-notes.md"),
        Path("docs/guides/whats-new-0.49.md"),
        Path("docs/guides/whats-new-0.50.md"),
        Path("docs/guides/whats-new-0.51.md"),
        Path("docs/guides/whats-new-0.52.md"),
        Path("docs/guides/whats-new-0.53.md"),
        Path("docs/RELEASE.md"),
    }
)

# Alias used by tests; honesty is no longer required on every first-run page.
FIRST_RUN_PATHS = REGISTRY_HONESTY_PATHS

IN_TREE_DEFERRED_BOILERPLATE = re.compile(
    r"published in-tree\s+`?v?\d+\.\d+(?:\.\d+)?`?\.?\*?\*?\s*"
    r"git tag and pypi upload are",
    re.IGNORECASE,
)

# Stale deferred-upload / wrong-public-train phrasing that must not appear on
# adopter pages when registry_status is "uploaded".
STALE_DEFERRED_PHRASE = re.compile(
    r"(?:"
    r"\bnot yet uploaded\b|"
    r"\buntil its (?:PyPI|pypi) upload\b|"
    r"\blatest installable public train is\b|"
    r"\brepository(?:'s|’s)?\s+(?:\*\*)?\d+\.\d+\.x(?:\*\*)?\s+train is for contributors\b|"
    r"\brepository contains the published\s+(?:\*\*|`)?\d+\.\d+\.x"
    r")",
    re.IGNORECASE,
)

# Any hedron-sample-kit pin in adopter prose must match release.toml satellites.
SAMPLE_KIT_PIN_ANYWHERE = re.compile(
    r"(?<![\w-])hedron-sample-kit(?P<constraint>>=[0-9.]+(?:,<[0-9.]+)?)",
    re.IGNORECASE,
)


def _version_matches_current(value: str, facts: ReleaseFacts) -> bool:
    value = _normalized_version(value)
    return value in {facts.train, facts.published_version}


def _version_matches_pypi(value: str, facts: ReleaseFacts) -> bool:
    value = _normalized_version(value)
    return value in {facts.pypi_version, facts.pypi_version.rsplit(".", 1)[0]}


def _pypi_claim_versions(line: str) -> list[str]:
    versions: list[str] = []
    for claim in PYPI_VERSION_CLAIM.finditer(line):
        pypi_value = next((group for group in claim.groups() if group), None)
        if pypi_value is None:
            continue
        snippet = line[claim.start() : min(len(line), claim.end() + 20)].lower()
        prefix = line[max(0, claim.start() - 25) : claim.start()].lower()
        if "in-tree" in snippet or "last published" in prefix:
            continue
        versions.append(pypi_value)
    return versions


def _line_describes_pypi_latest(line: str) -> bool:
    lower = line.lower()
    return any(
        phrase in lower
        for phrase in (
            "on pypi today",
            "latest on pypi",
            "pypi today",
            "currently on pypi",
            "from pypi",
            "pypi is",
            "pypi latest",
            "not on pypi",
            "cannot resolve",
            "no matching distribution",
            "tag/pypi deferred",
            "pypi deferred",
        )
    )


def _allowed_install_pins(facts: ReleaseFacts, path: Path | None = None) -> set[str]:
    allowed = {facts.pin}
    if path in POSIT_WORKBENCH_PATHS:
        allowed.add(">=0.67.0,<0.68")
    # Edron 1.0 directly consumes Hedron 1.x and therefore documents its own
    # bounded major range instead of the flagship application's minor pin.
    if path in {
        Path("docs/guides/edron-user-guide.md"),
        Path("packages/edron/README.md"),
    }:
        allowed.add(">=1.0.0,<2.0")
    if facts.registry_deferred and facts.pypi_pin != facts.pin:
        if path is not None and path in FIRST_RUN_INSTALL_PATHS:
            return {facts.pypi_pin}
        allowed.add(facts.pypi_pin)
    return allowed


def check_text(
    path: Path,
    text: str,
    facts: ReleaseFacts = FACTS,
    *,
    check_installs: bool = True,
) -> list[str]:
    failures: list[str] = []
    lines = text.splitlines()
    for index, line in enumerate(lines, start=1):
        # Join a soft-wrapped current/living/last-published claim to its next line.
        claim_windows = [line]
        if index < len(lines):
            lower = line.lower()
            incomplete = bool(
                re.search(r"\b(?:living|current(?:ly)?|last\s+published)\b", lower)
                and not CURRENT_CLAIM_VERSION.search(line)
                and not line.lstrip().startswith("|")
            )
            if incomplete:
                claim_windows.append(f"{line.rstrip()} {lines[index].strip()}")
        for scan in claim_windows:
            for claim in CURRENT_CLAIM_VERSION.finditer(scan):
                value = next((group for group in claim.groups() if group), None)
                if value is None:
                    continue
                if _line_describes_pypi_latest(scan) and _version_matches_pypi(value, facts):
                    continue
                if not _version_matches_current(value, facts):
                    failures.append(
                        f"{path}:{index}: current/living claim uses {value}; "
                        f"expected {facts.train_line} or v{facts.published_version}"
                    )
            for claim in CURRENT_PIN_CLAIM.finditer(scan):
                constraint = claim.group(1)
                if constraint not in _allowed_install_pins(facts, path):
                    expected = " or ".join(sorted(_allowed_install_pins(facts, path)))
                    failures.append(
                        f"{path}:{index}: current/living pin uses {constraint}; expected {expected}"
                    )

        if MATURITY_COLLISION.search(line):
            failures.append(f"{path}:{index}: ambiguous maturity phrase: {line.strip()}")

        if (
            not _is_historical(path)
            and not facts.registry_deferred
            and STALE_DEFERRED_PHRASE.search(line)
        ):
            failures.append(
                f"{path}:{index}: stale deferred-upload / wrong-public-train phrasing "
                f"while registry_status is uploaded: {line.strip()}"
            )

        if not _is_historical(path):
            for match in SAMPLE_KIT_PIN_ANYWHERE.finditer(line):
                constraint = match.group("constraint") or ""
                if constraint != facts.sample_kit_pin:
                    failures.append(
                        f"{path}:{index}: hedron-sample-kit pin must be "
                        f"{facts.sample_kit_pin}; found {constraint}"
                    )

        if not _is_historical(path) and CURRENT_TRAIN_MENTION.search(line):
            for pypi_value in _pypi_claim_versions(line):
                if not _version_matches_pypi(pypi_value, facts):
                    failures.append(
                        f"{path}:{index}: current/living train cites PyPI v{pypi_value}; "
                        f"expected v{facts.pypi_version}"
                    )

        if (
            not _is_historical(path)
            and _is_inventory_page(path)
            and not re.search(r"\b(?:current(?:ly)?|living)\b", line, re.I)
        ):
            for label in TRAIN_LABEL.finditer(line):
                train = _train_minor(label.group(1))
                if train != facts.train:
                    failures.append(
                        f"{path}:{index}: inventory train label {train} train; "
                        f"expected {facts.train_line} or mark current/living"
                    )

        if (
            not check_installs
            or not INSTALL_LINE.search(line)
            or re.search(
                r"\b(?:not available|do not|don't|never|failed with|cannot resolve)\b",
                line,
                re.I,
            )
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
            if constraint not in _allowed_install_pins(facts, path):
                expected = " or ".join(sorted(_allowed_install_pins(facts, path)))
                failures.append(
                    f"{path}:{index}: install for {match.group('name')} must use "
                    f"{expected}; found {constraint or 'no version constraint'}"
                )

        for match in EDRON_REQUIREMENT.finditer(line):
            constraint = match.group("constraint") or ""
            prefix = line[: match.start()]
            is_requirement_position = bool(
                re.search(r"(?:pip(?:3)?\s+install|uv\s+add|--from)\s+[\"']?$", prefix, re.I)
            )
            if not constraint and not is_requirement_position:
                continue
            allowed_edron_pins = {facts.edron_pin}
            if facts.edron_registry_status == "deferred":
                allowed_edron_pins = {facts.edron_pypi_pin}
            if constraint not in allowed_edron_pins:
                failures.append(
                    f"{path}:{index}: install for {match.group('name')} must use "
                    f"{' or '.join(sorted(allowed_edron_pins))}; found "
                    f"{constraint or 'no version constraint'}"
                )

        for match in SATELLITE_REQUIREMENT.finditer(line):
            name = match.group("name") or ""
            if name.startswith("hedron-charts"):
                expected = facts.charts_pin
            else:
                expected = facts.sample_kit_pin
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
    # Soft-wrap joins can duplicate the same claim; keep stable unique messages.
    return list(dict.fromkeys(failures))


def _has_compatible_satellite_floor(line: str, facts: ReleaseFacts = FACTS) -> bool:
    flagship = f"hedron[charts]{facts.pin}"
    charts = facts.charts_pin
    sample = facts.sample_kit_pin
    checks: list[bool] = []
    if "hedron[charts]" in line:
        checks.append(flagship in line)
    if "hedron-charts" in line:
        checks.append(
            f"hedron-charts{charts}" in line or "hedron-charts[" in line and charts in line
        )
    if "hedron-sample-kit" in line:
        checks.append(f"hedron-sample-kit{sample}" in line)
    return bool(checks) and all(checks)


UNBOUNDED_CHARTS_PKG = re.compile(
    rf"hedron-charts(?:\[[^\]]+\])?>={re.escape(FACTS.charts_minimum)}"
    rf"(?!,<{re.escape(FACTS.charts_maximum)})"
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
    edron_project = tomllib.loads(
        (ROOT / "packages" / "edron" / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    if edron_project["version"] != facts.edron_development_version:
        failures.append(
            "docs/release.toml Edron development_version does not match package metadata"
        )
    edron_changelog = (ROOT / "packages" / "edron" / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{facts.edron_published_version}]" not in edron_changelog:
        failures.append(
            f"packages/edron/CHANGELOG.md has no [{facts.edron_published_version}] section"
        )
    if not facts.published_version.startswith(f"{facts.train}."):
        failures.append("published_version is not on the configured release train")
    if facts.pin_floor != facts.published_version:
        failures.append("pin_floor must equal published_version")
    if facts.registry_status not in {"uploaded", "deferred"}:
        failures.append("registry_status must be 'uploaded' or 'deferred'")
    if facts.registry_status == "uploaded" and facts.pypi_version != facts.published_version:
        failures.append("uploaded registry_status requires pypi_version == published_version")
    if facts.registry_status == "deferred" and facts.pypi_version == facts.published_version:
        failures.append(
            "deferred registry_status requires pypi_version to differ from published_version"
        )
    if facts.edron_registry_status not in {"uploaded", "deferred"}:
        failures.append("Edron registry_status must be 'uploaded' or 'deferred'")
    if (
        facts.edron_registry_status == "uploaded"
        and facts.edron_pypi_version != facts.edron_published_version
    ):
        failures.append("Uploaded Edron registry_status requires pypi_version == published_version")
    if (
        facts.edron_registry_status == "deferred"
        and facts.edron_pypi_version == facts.edron_published_version
    ):
        failures.append(
            "Deferred Edron registry_status requires pypi_version to differ from published_version"
        )
    return failures


def check_first_run_registry_honesty(
    files: dict[Path, str],
    facts: ReleaseFacts = FACTS,
) -> list[str]:
    """When the train is not on PyPI, the canonical install page (and PyPI READMEs) must say so."""
    if not facts.registry_deferred:
        return []
    failures: list[str] = []
    required_bits = (facts.pypi_version, "pypi")
    for relative in sorted(REGISTRY_HONESTY_PATHS):
        text = files.get(relative)
        if text is None:
            failures.append(f"{relative}: missing registry-honesty page")
            continue
        lower = text.lower()
        missing = [bit for bit in required_bits if bit.lower() not in lower]
        if missing:
            failures.append(
                f"{relative}: deferred PyPI train must mention {', '.join(missing)} "
                f"(latest on PyPI is {facts.pypi_version})"
            )
        if "deferred" not in lower and "not on pypi" not in lower:
            failures.append(
                f"{relative}: deferred PyPI train must say the Git tag/PyPI upload is deferred"
            )
    return failures


_LIVING_TIP_CLAIM = re.compile(
    r"\b(?:living|checkout|in-tree)\s+tip\b[^\n]{0,40}?v?(\d+\.\d+\.\d+)",
    re.IGNORECASE,
)
_EDITABLE_TIP_CLAIM = re.compile(
    r"\beditable\s+\*?\*?v?(\d+\.\d+\.\d+)\*?\*?",
    re.IGNORECASE,
)
_DEFERRED_UPLOAD_CLAIM = re.compile(
    r"\b(?:for|upload(?:\s+for)?|tag(?:/pypi)?(?:\s+for)?)\s+\*?\*?v?(\d+\.\d+\.\d+)\*?\*?"
    r"[^\n]{0,40}?\bdeferred\b"
    r"|"
    r"\b(\d+\.\d+\.\d+)\b[^\n]{0,20}?\b(?:tag/pypi\s+)?deferred\b",
    re.IGNORECASE,
)


def check_tip_honesty(
    files: dict[Path, str],
    facts: ReleaseFacts = FACTS,
) -> list[str]:
    """Fail stale living/checkout tip and deferred-upload phrasing on honesty pages."""
    failures: list[str] = []
    expected_tip = facts.published_version
    for relative in sorted(TIP_HONESTY_PATHS):
        text = files.get(relative)
        if text is None:
            continue
        for index, line in enumerate(text.splitlines(), start=1):
            for match in _LIVING_TIP_CLAIM.finditer(line):
                value = match.group(1)
                if value != expected_tip:
                    failures.append(
                        f"{relative}:{index}: living/checkout tip claims {value}; "
                        f"expected v{expected_tip}"
                    )
            for match in _EDITABLE_TIP_CLAIM.finditer(line):
                value = match.group(1)
                if value != expected_tip:
                    failures.append(
                        f"{relative}:{index}: editable tip claims {value}; expected {expected_tip}"
                    )
            if facts.registry_deferred:
                for match in _DEFERRED_UPLOAD_CLAIM.finditer(line):
                    value = next((group for group in match.groups() if group), None)
                    if value is None:
                        continue
                    if value in {facts.pypi_version, facts.previous_version}:
                        # Historical "0.56.0 deferred" / prior train notes are fine.
                        continue
                    if value != expected_tip:
                        failures.append(
                            f"{relative}:{index}: deferred-upload claim names {value}; "
                            f"expected deferred tip v{expected_tip}"
                        )
    return failures


def check_in_tree_deferred_boilerplate(
    path: Path,
    text: str,
) -> list[str]:
    """Adopter pages must not paste the in-tree/deferred release sentence."""
    if path in BOILERPLATE_ALLOWED_PATHS or _is_historical(path):
        return []
    if IN_TREE_DEFERRED_BOILERPLATE.search(text):
        return [
            f"{path}: paste the in-tree/deferred upload sentence only on "
            f"{CANONICAL_INSTALL_PAGE} (or a PyPI package README / release notes)"
        ]
    return []


_EVALUATE_VERSION_ROW = re.compile(r"^\|\s*Version\s*\|\s*(.+?)\s*\|", re.IGNORECASE)
_VERSION_TOKEN = re.compile(r"\d+\.\d+(?:\.\d+)?(?:\.x)?")


def check_evaluate_version(
    text: str,
    facts: ReleaseFacts = FACTS,
    path: Path = Path("docs/guides/evaluate.md"),
) -> list[str]:
    """Evaluate's Version row may name the current train or labeled PyPI version only."""
    allowed_trains = {
        facts.train,
        facts.train_line,
        facts.published_version,
        facts.pypi_version,
        facts.pypi_train_line,
    }
    failures: list[str] = []
    for index, line in enumerate(text.splitlines(), start=1):
        match = _EVALUATE_VERSION_ROW.match(line)
        if not match:
            continue
        cell = match.group(1)
        for token in _VERSION_TOKEN.findall(cell):
            train = token[:-2] if token.endswith(".x") else token
            if "." in train and train.count(".") == 2:
                train = ".".join(train.split(".")[:2])
            if token not in allowed_trains and train not in allowed_trains:
                failures.append(
                    f"{path}:{index}: Version row names {token}; expected current "
                    f"{facts.train_line} / v{facts.published_version} or labeled PyPI "
                    f"{facts.pypi_version}"
                )
        if facts.registry_deferred and facts.pypi_version not in cell:
            failures.append(
                f"{path}:{index}: Version row must name PyPI {facts.pypi_version} "
                "while the upload is deferred"
            )
    return failures


def check_security_policy(
    path: Path,
    text: str,
    facts: ReleaseFacts = FACTS,
) -> list[str]:
    """Require the support matrix to follow release metadata exactly."""
    normalized = " ".join(text.split())
    if facts.registry_deferred:
        required = (
            f"current repository train** (`{facts.train_line}`)",
            f"immediately previous minor (`{facts.previous_train}.x`)",
            f"| `{facts.train_line}` | Yes (current repository train — public PyPI pin remains "
            f"`{facts.pypi_pin}`; upload deferred) |",
            f"| `{facts.previous_train}.x` | Best-effort security triage through "
            f"approximately {facts.previous_security_until}; upgrade to `{facts.train_line}` |",
        )
    else:
        required = (
            f"current published train** (`{facts.train_line}`)",
            f"immediately previous minor (`{facts.previous_train}.x`)",
            f"| `{facts.train_line}` | Yes (current published train — pin "
            f"`{facts.pin}`; published `v{facts.published_version}`) |",
            f"| `{facts.previous_train}.x` | Best-effort security triage through "
            f"approximately {facts.previous_security_until}; upgrade to `{facts.train_line}` |",
        )
    return [
        f"{path}: security policy is missing release-derived text: {marker}"
        for marker in required
        if marker not in normalized
    ]


def main() -> int:
    failures = check_metadata()
    honesty_texts: dict[Path, str] = {}
    tip_texts: dict[Path, str] = {}
    evaluate_text: str | None = None
    for path in adopter_files():
        relative = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        if relative in REGISTRY_HONESTY_PATHS:
            honesty_texts[relative] = text
        if relative in TIP_HONESTY_PATHS:
            tip_texts[relative] = text
        if relative == Path("docs/guides/evaluate.md"):
            evaluate_text = text
        failures.extend(check_text(relative, text))
        failures.extend(check_in_tree_deferred_boilerplate(relative, text))
        failures.extend(check_release_candidate_status(relative, text))
        failures.extend(check_section_landing(relative, text))
    # Historical release pages may keep their original install commands, but any
    # explicit current/living pointer on those pages must track release.toml.
    for path in sorted((ROOT / "docs" / "guides").glob("whats-new-0.*.md")):
        relative = path.relative_to(ROOT)
        historical_text = path.read_text(encoding="utf-8")
        failures.extend(check_text(relative, historical_text, check_installs=False))
        failures.extend(check_historical_release_banner(relative, historical_text))
    failures.extend(check_first_run_registry_honesty(honesty_texts))
    failures.extend(check_tip_honesty(tip_texts))
    if evaluate_text is None:
        failures.append("docs/guides/evaluate.md: missing evaluate page")
    else:
        failures.extend(check_evaluate_version(evaluate_text))
    root_security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    docs_security = (ROOT / "docs" / "SECURITY.md").read_text(encoding="utf-8")
    failures.extend(check_security_policy(Path("SECURITY.md"), root_security))
    failures.extend(check_security_policy(Path("docs/SECURITY.md"), docs_security))
    if root_security != docs_security:
        failures.append("SECURITY.md and docs/SECURITY.md must remain byte-for-byte identical")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    registry = (
        f"PyPI {FACTS.pypi_version} ({FACTS.registry_status})"
        if FACTS.registry_deferred
        else f"PyPI {FACTS.pypi_version}"
    )
    print(
        f"ok: adopter docs agree with repository train v{FACTS.published_version}, "
        f"train {FACTS.train_line}, pin {FACTS.pin}, {registry}, "
        f"Edron v{FACTS.edron_published_version} pin {FACTS.edron_pin}, "
        f"charts floor {FACTS.charts_pin}, and sample-kit floor {FACTS.sample_kit_pin}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
