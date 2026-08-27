"""Non-magical Edron authoring tools.

Static checks parse source with :mod:`ast` and never import the target module.  Runtime
explanations inspect registered metadata only; they never invoke page methods or dependencies.
"""

from __future__ import annotations

import ast
import importlib
import importlib.util
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from edron.diagnostics import DiagnosticReport, EdronDiagnostic, SourceLocation, finding


def _location(path: Path, node: ast.AST, *, qualname: str | None = None) -> SourceLocation:
    return SourceLocation(
        str(path),
        max(1, int(getattr(node, "lineno", 1))),
        max(1, int(getattr(node, "col_offset", 0)) + 1),
        int(getattr(node, "end_lineno", getattr(node, "lineno", 1))),
        int(getattr(node, "end_col_offset", getattr(node, "col_offset", 0))) + 1,
        qualname,
    )


class _StaticVisitor(ast.NodeVisitor):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.findings: list[EdronDiagnostic] = []
        self._page_class: str | None = None

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == "edron" and alias.asname == "st":
                self.findings.append(
                    finding(
                        "EDR-TOOL-0001",
                        severity="error",
                        title="Unsupported compatibility alias",
                        explanation=(
                            "Edron does not provide an import edron as st compatibility runtime."
                        ),
                        remediation="Use import edron as ed and the explicit Page API.",
                        source=_location(self.path, node),
                    )
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = ""
        if isinstance(node.func, ast.Attribute):
            name = node.func.attr
        elif isinstance(node.func, ast.Name):
            name = node.func.id
        if name in {"write", "session_state", "cache_resource"}:
            self.findings.append(
                finding(
                    "EDR-TOOL-0002",
                    severity="error",
                    title="Unsupported Edron vocabulary",
                    explanation=(
                        f"{name} is not part of the Edron request-local authoring contract."
                    ),
                    remediation=(
                        "Choose an explicit output, dependency, cache_data, session, "
                        "or action owner."
                    ),
                    source=_location(self.path, node),
                    context={"name": name},
                )
            )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        is_page = any(
            isinstance(base, ast.Attribute)
            and base.attr == "Page"
            or isinstance(base, ast.Name)
            and base.id == "Page"
            for base in node.bases
        )
        if is_page:
            previous = self._page_class
            self._page_class = node.name
            methods = {
                item.name
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            if "render" not in methods:
                self.findings.append(
                    finding(
                        "EDR-TOOL-0003",
                        severity="error",
                        title="Page has no render method",
                        explanation=f"Page class {node.name!r} must define render() directly.",
                        remediation="Add def render(self) -> None: ...",
                        source=_location(self.path, node, qualname=node.name),
                    )
                )
            if "__init__" in methods:
                self.findings.append(
                    finding(
                        "EDR-TOOL-0004",
                        severity="error",
                        title="Page constructor is not request-safe",
                        explanation="Edron creates fresh page instances and owns their lifecycle.",
                        remediation=(
                            "Remove __init__; use typed dependencies or local render values."
                        ),
                        source=_location(self.path, node, qualname=node.name),
                    )
                )
            self.generic_visit(node)
            self._page_class = previous
            return
        self.generic_visit(node)


def check_source(source: str | Path) -> DiagnosticReport:
    """Parse an application file without importing or executing it."""
    path = Path(source)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return DiagnosticReport(
            (
                finding(
                    "EDR-TOOL-0005",
                    severity="error",
                    title="Source could not be read",
                    explanation=str(exc),
                    remediation="Pass a readable Python source file.",
                    source=SourceLocation(str(path), 1),
                ),
            )
        )
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        return DiagnosticReport(
            (
                finding(
                    "EDR-TOOL-0006",
                    severity="error",
                    title="Python syntax error",
                    explanation=exc.msg,
                    remediation="Fix the syntax before registering the application.",
                    source=SourceLocation(str(path), exc.lineno or 1, (exc.offset or 1)),
                ),
            )
        )
    visitor = _StaticVisitor(path)
    visitor.visit(tree)
    return DiagnosticReport(tuple(visitor.findings))


def load_application(target: str | Path, *, attribute: str = "app") -> Any:
    """Load a trusted application for ``run``, ``check --register``, or ``explain``."""
    if isinstance(target, Path) or (isinstance(target, str) and Path(target).is_file()):
        path = Path(target).resolve()
        spec = importlib.util.spec_from_file_location("edron_application", path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load application file {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, attribute)
    module_name, separator, attr = str(target).partition(":")
    if not separator:
        raise ValueError("application must be a file or module:attribute")
    module = importlib.import_module(module_name)
    value: Any = module
    for part in attr.split("."):
        value = getattr(value, part)
    return value


def explain_application(app: Any) -> Mapping[str, Any]:
    """Return a bounded, source-mapped explanation of an Edron app."""
    explain = getattr(app, "explain", None)
    if not callable(explain):
        return {
            "schema": "edron.application-explanation/1",
            "kind": type(app).__name__,
            "pages": [],
        }
    return cast(Mapping[str, Any], explain())


def check_application(app: Any) -> DiagnosticReport:
    """Validate already-registered metadata without invoking an application callback."""
    if not hasattr(app, "explain") or not hasattr(app, "source_map"):
        return DiagnosticReport(
            (
                finding(
                    "EDR-TOOL-0008",
                    severity="error",
                    title="Unsupported application target",
                    explanation=(
                        "The target is not an Edron App and has no Edron registration metadata."
                    ),
                    remediation="Pass an edron.App or use a native Hedron inspection command.",
                ),
            )
        )
    payload = app.explain()
    findings: list[EdronDiagnostic] = []
    pages = payload.get("pages", [])
    if not isinstance(pages, list):
        findings.append(
            finding(
                "EDR-TOOL-0009",
                severity="error",
                title="Malformed explanation",
                explanation="The application explanation did not contain a page list.",
            )
        )
    return DiagnosticReport(tuple(findings))


def doctor(*, application: Any = None) -> dict[str, Any]:
    """Report package capabilities without installing or changing anything."""
    import importlib.metadata

    from packaging.specifiers import SpecifierSet

    requirements = {
        "edron": (">=0.6,<0.7", "edron"),
        "hedron": (">=0.66,<0.67", "hedron"),
        "hedron-data": (">=0.66,<0.67", "hedron_data"),
        "hedron-charts": (">=0.2,<0.3", "hedron_charts"),
        "hedron-maps": (">=0.1,<0.2", "hedron_maps"),
    }
    optional = {
        "pandas": (">=2", "pandas"),
        "polars": (">=1", "polars"),
        "pyarrow": (">=15", "pyarrow"),
        "plotly": (">=5.18,<7", "plotly"),
        "altair": (">=6,<7", "altair"),
        "matplotlib": (">=3.8,<4", "matplotlib"),
        "sqlalchemy": (">=2,<3", "sqlalchemy"),
    }

    def inspect_package(
        name: str, spec: str, module_name: str, *, is_required: bool
    ) -> dict[str, Any]:
        if name == "edron":
            from edron import __version__ as version
        else:
            try:
                version = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                return {"name": name, "status": "missing", "required": is_required}
        try:
            compatible = version in SpecifierSet(spec)
        except ValueError:
            compatible = False
        if not compatible:
            return {
                "name": name,
                "version": version,
                "status": "incompatible",
                "required": is_required,
            }
        try:
            importlib.import_module(module_name)
        except (ImportError, OSError, RuntimeError, AttributeError):
            return {"name": name, "version": version, "status": "broken", "required": is_required}
        return {"name": name, "version": version, "status": "available", "required": is_required}

    result: dict[str, Any] = {"schema": "edron.doctor/1", "required": [], "optional": []}
    result["required"] = [
        inspect_package(name, *args, is_required=True) for name, args in requirements.items()
    ]
    result["optional"] = [
        inspect_package(name, *args, is_required=False) for name, args in optional.items()
    ]
    if application is not None:
        result["application"] = explain_application(application)
        operations = getattr(application, "operations", None)
        if callable(operations):
            result["operations"] = operations()
    return result


__all__ = [
    "check_application",
    "check_source",
    "doctor",
    "explain_application",
    "load_application",
]
