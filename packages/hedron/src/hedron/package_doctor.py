"""External package-author validation (DOCTOR-054).

``hedron package doctor`` statically validates a package source tree for authors
who publish Hedron plugins. It is distinct from ``hedron fleet`` (installed
application triage, which reports ``package_doctor: False``) and from Explorer
package health. The doctor never imports the target package, never installs or
enables anything, and reports local paths relative to the package root.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from hedron_core.compat import tomllib

HED_PACKAGE_DOCTOR = "HED-PACKAGE-DOCTOR"
BOUNDARY = "package_doctor"

# Mirrored so the doctor works without the optional hedron-conformance install.
FALLBACK_SCHEMA_VERSION = "hedron-authoring-loop-1"

MAX_SCANNED_FILES = 2_000
MAX_SCANNED_BYTES = 512 * 1024

_ASSET_SUFFIXES = frozenset(
    {".css", ".mjs", ".js", ".hdj", ".json", ".svg", ".png", ".txt", ".woff2"}
)
_NAMESPACE_RE = re.compile(r"^[a-z][a-z0-9_-]*(\.[a-z0-9_-]+)+$")
_NAMESPACE_LITERAL_RE = re.compile(r"(?:namespace|NAMESPACE)\s*=\s*[\"']([^\"']+)[\"']")
_SCHEMA_LITERAL_RE = re.compile(r"[\"'](hedron-authoring-loop-\d+)[\"']")
_MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)")
_ENTRY_POINT_RE = re.compile(r"^[\w.]+:[\w.]+$")
_UPPER_BOUND_OPS = frozenset({"<", "<=", "==", "===", "~="})
_LOWER_BOUND_OPS = frozenset({">", ">=", "==", "===", "~="})

__all__ = [
    "BOUNDARY",
    "FALLBACK_SCHEMA_VERSION",
    "HED_PACKAGE_DOCTOR",
    "authoring_loop_fingerprint",
    "diagnose_package",
]


def _diagnostic(
    message: str,
    *,
    check: str,
    severity: str = "error",
    **details: Any,
) -> dict[str, Any]:
    return {
        "code": HED_PACKAGE_DOCTOR,
        "message": message,
        "boundary": BOUNDARY,
        "severity": severity,
        "details": {"check": check, **details},
    }


def _schema_version() -> tuple[str, bool]:
    try:
        from hedron_conformance.authoring_loop import AUTHORING_LOOP_SCHEMA_VERSION
    except ImportError:
        return FALLBACK_SCHEMA_VERSION, False
    return AUTHORING_LOOP_SCHEMA_VERSION, True


def authoring_loop_fingerprint() -> str:
    """Return a stable fingerprint of the shared authoring-loop contract."""
    version, installed = _schema_version()
    codes = (
        "HED-NOTEBOOK-TOKEN",
        "HED-NOTEBOOK-TOPOLOGY",
        "HED-PACKAGE-DOCTOR",
        "HED-SIM-LIMIT",
        "HED-SIM-UNSUPPORTED",
    )
    payload = "|".join((version, *codes, "installed" if installed else "mirrored"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return path.name


def _hatch_targets(config: dict[str, Any]) -> dict[str, Any]:
    tool = dict(config.get("tool") or {})
    hatch = dict(tool.get("hatch") or {})
    build = dict(hatch.get("build") or {})
    return dict(build.get("targets") or {})


def _package_dirs(root: Path, project: dict[str, Any], config: dict[str, Any]) -> tuple[Path, ...]:
    """Locate importable package directories without importing anything."""
    wheel = (_hatch_targets(config).get("wheel") or {}).get("packages") or []
    found: list[Path] = []
    for entry in wheel:
        candidate = root / str(entry)
        if candidate.is_dir():
            found.append(candidate)
    if found:
        return tuple(found)
    src = root / "src"
    if src.is_dir():
        found = [child for child in sorted(src.iterdir()) if (child / "__init__.py").is_file()]
        if found:
            return tuple(found)
    name = str(project.get("name") or "").replace("-", "_")
    candidate = root / name
    return (candidate,) if (candidate / "__init__.py").is_file() else ()


def _scan_files(package_dirs: tuple[Path, ...]) -> tuple[Path, ...]:
    files: list[Path] = []
    for folder in package_dirs:
        for path in sorted(folder.rglob("*")):
            if "__pycache__" in path.parts or not path.is_file():
                continue
            files.append(path)
            if len(files) >= MAX_SCANNED_FILES:
                return tuple(files)
    return tuple(files)


def _python_sources(files: tuple[Path, ...]) -> dict[Path, str]:
    sources: dict[Path, str] = {}
    for path in files:
        if path.suffix != ".py" or path.stat().st_size > MAX_SCANNED_BYTES:
            continue
        try:
            sources[path] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
    return sources


def _check_metadata(
    root: Path, project: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    found: list[dict[str, Any]] = []
    for key in ("name", "version"):
        if not str(project.get(key) or "").strip():
            found.append(_diagnostic(f"pyproject [project] is missing {key!r}", check="metadata"))
    for key in ("description", "readme", "requires-python", "classifiers"):
        if not project.get(key):
            found.append(
                _diagnostic(
                    f"pyproject [project] is missing {key!r}",
                    check="metadata",
                    severity="warning",
                )
            )
    if not project.get("license") and not project.get("license-files"):
        found.append(
            _diagnostic(
                "pyproject declares neither 'license' nor 'license-files'",
                check="metadata",
                severity="warning",
            )
        )
    readme = str(project.get("readme") or "")
    if readme and not (root / readme).is_file():
        found.append(
            _diagnostic(f"declared readme {readme!r} does not exist", check="metadata"),
        )
    return (
        {
            "name": project.get("name"),
            "version": project.get("version"),
            "requires_python": project.get("requires-python"),
            "readme": readme or None,
        },
        found,
    )


def _check_entry_points(
    root: Path,
    project: dict[str, Any],
    package_dirs: tuple[Path, ...],
    sources: dict[Path, str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    found: list[dict[str, Any]] = []
    groups = dict(project.get("entry-points") or {})
    plugins = dict(groups.get("hedron.plugins") or {})
    resolved: list[dict[str, str]] = []
    for name, target in sorted(plugins.items()):
        value = str(target)
        row = {"name": name, "value": value, "module_file": ""}
        if not _ENTRY_POINT_RE.match(value):
            found.append(
                _diagnostic(
                    f"entry point {name!r} value {value!r} is not 'module:attr'",
                    check="entry_points",
                    entry_point=name,
                )
            )
            resolved.append(row)
            continue
        module, _, attribute = value.partition(":")
        relative = Path(*module.split("."))
        module_file: Path | None = None
        for folder in package_dirs:
            for candidate in (
                folder.parent / relative.with_suffix(".py"),
                folder.parent / relative / "__init__.py",
            ):
                if candidate.is_file():
                    module_file = candidate
                    break
            if module_file is not None:
                break
        if module_file is None:
            found.append(
                _diagnostic(
                    f"entry point {name!r} module {module!r} was not found in the source tree",
                    check="entry_points",
                    entry_point=name,
                )
            )
            resolved.append(row)
            continue
        row["module_file"] = _relative(module_file, root)
        text = sources.get(module_file, "")
        if f"def {attribute}" not in text and f"{attribute} =" not in text:
            found.append(
                _diagnostic(
                    f"entry point {name!r} target {attribute!r} is missing from "
                    f"{row['module_file']}",
                    check="entry_points",
                    entry_point=name,
                )
            )
        if "PLUGIN_META" not in text:
            found.append(
                _diagnostic(
                    f"plugin module {row['module_file']} does not declare PLUGIN_META",
                    check="entry_points",
                    severity="warning",
                    entry_point=name,
                )
            )
        resolved.append(row)
    if not plugins:
        found.append(
            _diagnostic(
                "no 'hedron.plugins' entry point is declared",
                check="entry_points",
                severity="information",
            )
        )
    return {"groups": sorted(groups), "hedron_plugins": resolved}, found


def _check_feature_descriptors(
    root: Path, sources: dict[Path, str]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    found: list[dict[str, Any]] = []
    bundles: list[str] = []
    namespaces: set[str] = set()
    for path, text in sources.items():
        relative = _relative(path, root)
        if "FeatureBundle(" in text:
            bundles.append(relative)
        for namespace in _NAMESPACE_LITERAL_RE.findall(text):
            namespaces.add(str(namespace))
            if not _NAMESPACE_RE.match(str(namespace)):
                found.append(
                    _diagnostic(
                        f"projection namespace {namespace!r} in {relative} is malformed",
                        check="feature_descriptors",
                        source=relative,
                    )
                )
    return (
        {
            "bundle_sources": sorted(bundles),
            "projection_namespaces": sorted(namespaces),
            "present": bool(bundles or namespaces),
        },
        found,
    )


def _check_assets(
    root: Path, files: tuple[Path, ...], config: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    found: list[dict[str, Any]] = []
    assets = [path for path in files if path.suffix in _ASSET_SUFFIXES]
    by_suffix: dict[str, int] = {}
    for path in assets:
        by_suffix[path.suffix] = by_suffix.get(path.suffix, 0) + 1
        if path.stat().st_size == 0:
            found.append(
                _diagnostic(
                    f"asset {_relative(path, root)} is empty",
                    check="assets",
                    asset=_relative(path, root),
                )
            )
    sdist = _hatch_targets(config).get("sdist") or {}
    only_include = [str(item) for item in sdist.get("only-include") or []]
    if only_include:
        for path in assets:
            relative = _relative(path, root)
            shipped = any(
                relative == item or relative.startswith(f"{item}/") for item in only_include
            )
            if not shipped:
                found.append(
                    _diagnostic(
                        f"asset {relative} is excluded from the sdist 'only-include' list",
                        check="assets",
                        severity="warning",
                        asset=relative,
                    )
                )
    return {"count": len(assets), "by_suffix": dict(sorted(by_suffix.items()))}, found


def _check_schema_fingerprints(
    root: Path, sources: dict[Path, str]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    found: list[dict[str, Any]] = []
    expected, installed = _schema_version()
    consumers: list[str] = []
    literals: set[str] = set()
    for path, text in sources.items():
        relative = _relative(path, root)
        if "hedron_conformance.authoring_loop" in text or "AUTHORING_LOOP_SCHEMA_VERSION" in text:
            consumers.append(relative)
        for literal in _SCHEMA_LITERAL_RE.findall(text):
            literals.add(str(literal))
            if str(literal) != expected:
                found.append(
                    _diagnostic(
                        f"authoring-loop schema literal {literal!r} in {relative} "
                        f"does not match {expected!r}",
                        check="schema_fingerprints",
                        source=relative,
                    )
                )
    return (
        {
            "schema_version": expected,
            "conformance_installed": installed,
            "fingerprint": authoring_loop_fingerprint(),
            "consumers": sorted(consumers),
            "literals": sorted(literals),
        },
        found,
    )


def _check_docs_links(
    root: Path, project: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    found: list[dict[str, Any]] = []
    readme = root / str(project.get("readme") or "README.md")
    if not readme.is_file():
        return {"readme": None, "checked": False}, found
    text = readme.read_text(encoding="utf-8")
    name = str(project.get("name") or "")
    if name and name not in text:
        found.append(
            _diagnostic(
                f"README does not mention the distribution name {name!r}",
                check="docs_links",
                severity="warning",
            )
        )
    broken: list[str] = []
    for target in _MARKDOWN_LINK_RE.findall(text):
        link = str(target)
        if link.startswith(("http://", "https://", "#", "mailto:")):
            continue
        if not (readme.parent / link.split("#", 1)[0]).exists():
            broken.append(link)
            found.append(
                _diagnostic(
                    f"README links to missing path {link!r}",
                    check="docs_links",
                    severity="warning",
                    link=link,
                )
            )
    if not (root / "CHANGELOG.md").is_file():
        found.append(
            _diagnostic(
                "no CHANGELOG.md accompanies the package",
                check="docs_links",
                severity="warning",
            )
        )
    return (
        {"readme": _relative(readme, root), "checked": True, "broken_links": broken},
        found,
    )


def _check_version_ranges(project: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from packaging.requirements import InvalidRequirement, Requirement

    found: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    grouped: list[tuple[str, str]] = [
        ("dependencies", str(dep)) for dep in project.get("dependencies") or []
    ]
    for extra, deps in (project.get("optional-dependencies") or {}).items():
        grouped.extend((f"optional-dependencies.{extra}", str(dep)) for dep in deps)
    for group, raw in grouped:
        try:
            requirement = Requirement(str(raw))
        except InvalidRequirement:
            found.append(
                _diagnostic(
                    f"dependency {raw!r} in {group} is not a valid requirement",
                    check="version_ranges",
                    group=group,
                )
            )
            continue
        operators = {spec.operator for spec in requirement.specifier}
        upper = bool(operators & _UPPER_BOUND_OPS)
        lower = bool(operators & _LOWER_BOUND_OPS)
        rows.append(
            {
                "group": group,
                "requirement": str(raw),
                "upper_bound": upper,
                "lower_bound": lower,
            }
        )
        if not upper:
            found.append(
                _diagnostic(
                    f"dependency {raw!r} in {group} has no upper bound",
                    check="version_ranges",
                    severity="warning",
                    group=group,
                )
            )
        if not lower:
            found.append(
                _diagnostic(
                    f"dependency {raw!r} in {group} has no lower bound",
                    check="version_ranges",
                    severity="information",
                    group=group,
                )
            )
    if not str(project.get("requires-python") or "").strip():
        found.append(
            _diagnostic(
                "pyproject does not pin 'requires-python'",
                check="version_ranges",
                severity="warning",
            )
        )
    return {"requirements": rows}, found


def _check_publishable(
    root: Path,
    config: dict[str, Any],
    package_dirs: tuple[Path, ...],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    found: list[dict[str, Any]] = []
    build_system = dict(config.get("build-system") or {})
    backend = str(build_system.get("build-backend") or "")
    if not backend:
        found.append(
            _diagnostic("pyproject declares no [build-system] build-backend", check="publishable")
        )
    if not build_system.get("requires"):
        found.append(
            _diagnostic(
                "pyproject declares no [build-system] requires",
                check="publishable",
                severity="warning",
            )
        )
    if not package_dirs:
        found.append(
            _diagnostic("no importable package directory was found", check="publishable"),
        )
    license_file = any((root / name).is_file() for name in ("LICENSE", "LICENSE.txt", "LICENSE.md"))
    if not license_file:
        found.append(
            _diagnostic(
                "no LICENSE file ships beside pyproject.toml",
                check="publishable",
                severity="warning",
            )
        )
    typed = [folder for folder in package_dirs if (folder / "py.typed").is_file()]
    return (
        {
            "build_backend": backend or None,
            "packages": [_relative(folder, root) for folder in package_dirs],
            "license_file": license_file,
            "py_typed": [_relative(folder, root) for folder in typed],
        },
        found,
    )


def diagnose_package(path: Path | str) -> dict[str, Any]:
    """Return a read-only ``HED-PACKAGE-DOCTOR`` report for a package source tree."""
    root = Path(path).resolve()
    report: dict[str, Any] = {
        "package_doctor": True,
        "read_only": True,
        "automatic_install": False,
        "schema_version": _schema_version()[0],
        "root": str(root),
        "ok": False,
        "checks": {},
        "diagnostics": [],
    }
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        report["diagnostics"] = [
            _diagnostic(f"no pyproject.toml under {root.name}", check="metadata")
        ]
        return report
    try:
        config = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        report["diagnostics"] = [
            _diagnostic(f"pyproject.toml could not be parsed: {exc}", check="metadata")
        ]
        return report

    project = dict(config.get("project") or {})
    package_dirs = _package_dirs(root, project, config)
    files = _scan_files(package_dirs)
    sources = _python_sources(files)

    results: list[tuple[str, tuple[dict[str, Any], list[dict[str, Any]]]]] = [
        ("metadata", _check_metadata(root, project)),
        ("entry_points", _check_entry_points(root, project, package_dirs, sources)),
        ("feature_descriptors", _check_feature_descriptors(root, sources)),
        ("assets", _check_assets(root, files, config)),
        ("schema_fingerprints", _check_schema_fingerprints(root, sources)),
        ("docs_links", _check_docs_links(root, project)),
        ("version_ranges", _check_version_ranges(project)),
        ("publishable", _check_publishable(root, config, package_dirs)),
    ]

    diagnostics: list[dict[str, Any]] = []
    checks: dict[str, Any] = {}
    for name, (detail, found) in results:
        checks[name] = {
            "ok": not any(item["severity"] == "error" for item in found),
            **detail,
        }
        diagnostics.extend(found)

    report["package"] = {
        "name": project.get("name"),
        "version": project.get("version"),
        "scanned_files": len(files),
    }
    report["checks"] = checks
    report["diagnostics"] = diagnostics
    report["ok"] = all(check["ok"] for check in checks.values())
    return report
