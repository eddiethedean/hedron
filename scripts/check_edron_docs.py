#!/usr/bin/env python3
"""Validate the Edron design packet's cross-document contracts.

The documentation and machine locks remain the source of truth for the accepted design contract;
the implemented runtime and release evidence are checked by their phase-specific suites.
"""

from __future__ import annotations

import ast
import builtins
import importlib
import re
import sys
import urllib.parse
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

ROADMAP = DOCS / "EDRON_ROADMAP.md"
RFC = DOCS / "rfcs/RFC-0094-EDRON-AUTHORING-FACADE.md"
PUBLIC_API = DOCS / "api/EDRON.md"
STATE = DOCS / "api/EDRON_STATE_INTERACTION.md"
PACKAGING = DOCS / "api/EDRON_PACKAGING.md"
INVENTORY = DOCS / "implementation/EDRON_CAPABILITY_INVENTORIES.md"
IMPLEMENTATION = DOCS / "implementation/EDRON_001.md"
GOLDENS = DOCS / "implementation/EDRON_GOLDEN_APPS.md"
ACCEPTANCE = DOCS / "acceptance/EDRON_001.md"
RELEASE_GATE = DOCS / "acceptance/edron-release-gate-001.toml"
UPSTREAM_LOCK = DOCS / "acceptance/edron-upstream-lock-001.toml"
CAPABILITY_MANIFEST = DOCS / "acceptance/edron-capability-manifest-001.toml"
PACKAGE_LOCK = DOCS / "acceptance/edron-package-lock-001.toml"
PUBLIC_API_LOCK = DOCS / "acceptance/edron-public-api-lock-001.toml"
LOWERING_MATRIX = DOCS / "acceptance/edron-lowering-matrix-001.toml"
STATE_INTERACTION_MATRIX = DOCS / "acceptance/edron-state-interaction-matrix-001.toml"
FIXTURE_LOCK = DOCS / "acceptance/edron-fixture-lock-001.toml"
PERFORMANCE_LOCK = DOCS / "acceptance/edron-performance-lock-001.toml"

MACHINE_DRAFTS = {
    "CAPABILITY_MANIFEST": CAPABILITY_MANIFEST,
    "PACKAGE_LOCK": PACKAGE_LOCK,
    "PUBLIC_API_LOCK": PUBLIC_API_LOCK,
    "LOWERING_MATRIX": LOWERING_MATRIX,
    "STATE_INTERACTION_MATRIX": STATE_INTERACTION_MATRIX,
    "FIXTURE_LOCK": FIXTURE_LOCK,
    "PERFORMANCE_LOCK": PERFORMANCE_LOCK,
}

EDRON_DOCUMENTS = (
    ROADMAP,
    RFC,
    PUBLIC_API,
    STATE,
    PACKAGING,
    INVENTORY,
    IMPLEMENTATION,
    GOLDENS,
    ACCEPTANCE,
)
CONTRACT_DOCUMENTS = (
    RFC,
    PUBLIC_API,
    STATE,
    PACKAGING,
    INVENTORY,
    IMPLEMENTATION,
    GOLDENS,
    ACCEPTANCE,
)

TARGET_TEXT = "Edron `0.1.0`; compatible Hedron train and release phase unassigned"
BASELINE_TEXT = "Hedron workspace `0.66.2`; not an accepted compatibility floor"
EXPECTED_UPSTREAM_IDS = tuple(f"UP-{number:03d}" for number in range(1, 12))
EXPECTED_UPSTREAM_WORKSTREAMS = {
    "HEDRON-WS-CLASS": ("UP-001", "UP-003"),
    "HEDRON-WS-INTERACTIONS": ("UP-002", "UP-004", "UP-005", "UP-006"),
    "HEDRON-WS-PROVENANCE": ("UP-007", "UP-011"),
    "HEDRON-WS-JOBS": ("UP-008",),
    "HEDRON-WS-STYLING": ("UP-009", "UP-010"),
}
EXPECTED_GATE_PHASE_COUNTS = {"design": 16, "implementation-entry": 10, "release": 20}
EXPECTED_REQUIREMENT_COUNTS = {
    RFC: 23,
    STATE: 14,
    PACKAGING: 13,
    INVENTORY: 9,
    IMPLEMENTATION: 87,
}
EXPECTED_OPTIONAL_REQUIREMENTS = {
    "pandas": ("pandas>=2.0", "narwhals>=1.1"),
    "polars": ("polars>=1.0", "narwhals>=1.1"),
    "pyarrow": ("pyarrow>=15.0", "narwhals>=1.1"),
    "plotly": ("plotly>=5.18,<7",),
    "altair": ("altair>=6,<7", "vl-convert-python>=1.0"),
    "matplotlib": ("matplotlib>=3.8,<4",),
    "sqlalchemy": ("sqlalchemy>=2,<3",),
}
EXPECTED_REQUIRED_DISTRIBUTION_IDS = (
    "runtime.hedron",
    "runtime.data",
    "runtime.charts",
    "runtime.maps",
    "runtime.markdown",
    "runtime.sanitizer",
    "runtime.server",
)
EXPECTED_LOWERING_IDS = (
    "LOWER-APP",
    "LOWER-PAGE",
    "LOWER-LAYOUT",
    "LOWER-INCLUDE",
    "LOWER-TEXT",
    "LOWER-DATA",
    "LOWER-CHART",
    "LOWER-MAP",
    "LOWER-OPTIONAL-DISPLAY",
    "LOWER-INPUT",
    "LOWER-FILTER",
    "LOWER-FRAGMENT",
    "LOWER-ACTION",
    "LOWER-FORM",
    "LOWER-OUTCOME",
    "LOWER-DEPENDENCY",
    "LOWER-CACHE-SESSION",
    "LOWER-STYLE",
    "LOWER-JOB",
    "LOWER-DOWNLOAD",
    "LOWER-NATIVE",
    "LOWER-TOOLING",
)
EXPECTED_STATE_IDS = (
    "STATE-PAGE-INSTANCE",
    "STATE-OUTPUT-FRAME",
    "STATE-SAFE-INPUT",
    "STATE-FORM-INPUT",
    "STATE-DEPENDENCY",
    "STATE-SESSION",
    "STATE-CACHE",
    "STATE-DURABLE",
    "STATE-IDEMPOTENCY",
    "STATE-JOB",
    "STATE-BROWSER",
    "STATE-STYLE",
)
EXPECTED_INTERACTION_IDS = (
    "INTERACTION-PAGE",
    "INTERACTION-FRAGMENT",
    "INTERACTION-FILTER",
    "INTERACTION-ACTION",
    "INTERACTION-FORM",
    "INTERACTION-JOB-SUBMIT",
    "INTERACTION-JOB-STATUS",
    "INTERACTION-JOB-CANCEL",
    "INTERACTION-DOWNLOAD",
    "INTERACTION-EXPLAIN",
)
EXPECTED_GOLDEN_IDS = (
    "GOLDEN-HELLO",
    "GOLDEN-SALES",
    "GOLDEN-CRUD",
    "GOLDEN-JOB",
    "GOLDEN-PLOTLY",
    "GOLDEN-STYLING",
)
EXPECTED_FOCUSED_IDS = (
    "FOCUSED-MAP",
    "FOCUSED-NATIVE-EDITOR",
    "FOCUSED-OPTIONAL-MATRIX",
    "FOCUSED-NATIVE-COMPOSITION",
    "FOCUSED-DEPENDENCY-LIFECYCLE",
    "FOCUSED-STATE-JOBS-DOWNLOADS",
    "FOCUSED-CLI-TRUST",
    "FOCUSED-ARTIFACT-UPGRADE",
    "FOCUSED-DEFERRED-NEGATIVE",
    "FOCUSED-CROSS-CUTTING",
)
EXPECTED_PERFORMANCE_BUDGET_COUNT = 43
MACHINE_TARGET = "edron 0.1.0"
MACHINE_BASELINE = "hedron workspace 0.66.2"

PYTHON_FENCE = re.compile(r"^```python[^\n]*\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
REQUIREMENT_DEFINITION = re.compile(r"^- \*\*(EDR-[A-Z0-9-]+-\d{3}):", re.MULTILINE)
CAPABILITY_ROW = re.compile(r"^\| `([A-Z]+(?:-[A-Z]+)*-\d{3})` \|", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class PythonFence:
    line: int
    source: str


@dataclass(slots=True)
class SignatureShape:
    keywords: set[str]
    accepts_var_keyword: bool = False

    def merge(self, other: SignatureShape) -> None:
        self.keywords.update(other.keywords)
        self.accepts_var_keyword = self.accepts_var_keyword or other.accepts_var_keyword


def display(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def python_fences(markdown: str) -> list[PythonFence]:
    return [
        PythonFence(line=markdown.count("\n", 0, match.start(1)) + 1, source=match.group(1))
        for match in PYTHON_FENCE.finditer(markdown)
    ]


def markdown_section(markdown: str, start: str, end: str) -> str:
    try:
        body = markdown.split(start, 1)[1]
        return body.split(end, 1)[0]
    except IndexError as exc:
        raise ValueError(f"missing section boundary {start!r} or {end!r}") from exc


def table_first_cell_symbols(section: str) -> set[str]:
    symbols: set[str] = set()
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        first_cell = line.strip().strip("|").split("|", 1)[0]
        symbols.update(re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", first_cell))
    return symbols


def optional_requirements(markdown: str) -> dict[str, tuple[str, ...]]:
    """Return ``extra -> direct requirement strings`` from a capability table."""
    result: dict[str, tuple[str, ...]] = {}
    for line in markdown.splitlines():
        if not line.startswith("|") or "edron[" not in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        shortcut_index = next(
            (
                index
                for index, cell in enumerate(cells)
                if re.fullmatch(r"`edron\[[a-z0-9-]+\]`", cell)
            ),
            None,
        )
        if shortcut_index is None:
            continue
        shortcut = re.fullmatch(r"`edron\[([a-z0-9-]+)\]`", cells[shortcut_index])
        assert shortcut is not None
        requirements: list[str] = []
        for cell in cells[:shortcut_index]:
            requirements.extend(
                span
                for span in re.findall(r"`([^`]+)`", cell)
                if re.search(r"(?:~=|==|!=|<=|>=|<|>)", span)
            )
        extra = shortcut.group(1)
        if extra in result:
            raise ValueError(f"duplicate optional shortcut row: edron[{extra}]")
        result[extra] = tuple(requirements)
    return result


def markdown_heading_slugs(markdown: str) -> set[str]:
    slugs: set[str] = set()
    counts: Counter[str] = Counter()
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*$", markdown, re.MULTILINE):
        plain = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", heading)
        plain = plain.replace("`", "").lower()
        slug = re.sub(r"[^\w\- ]", "", plain)
        slug = re.sub(r"\s+", "-", slug.strip())
        suffix = counts[slug]
        counts[slug] += 1
        slugs.add(f"{slug}-{suffix}" if suffix else slug)
    return slugs


def _signature_shape(node: ast.FunctionDef | ast.AsyncFunctionDef) -> SignatureShape:
    arguments = node.args
    names = {
        argument.arg
        for argument in (*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs)
        if argument.arg not in {"self", "cls"}
    }
    return SignatureShape(names, accepts_var_keyword=arguments.kwarg is not None)


def _merge_signature(
    registry: dict[str, SignatureShape],
    name: str,
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> None:
    shape = _signature_shape(node)
    if name in registry:
        registry[name].merge(shape)
    else:
        registry[name] = shape


def api_signature_registries(
    markdown: str,
) -> tuple[dict[str, SignatureShape], dict[str, SignatureShape], dict[str, SignatureShape]]:
    """Return common-surface, App, and module-level signature registries."""
    surface: dict[str, SignatureShape] = {}
    app: dict[str, SignatureShape] = {}
    module: dict[str, SignatureShape] = {}
    for fence in python_fences(markdown):
        tree = ast.parse(fence.source)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                positional = (*node.args.posonlyargs, *node.args.args)
                registry = surface if positional and positional[0].arg == "self" else module
                _merge_signature(registry, node.name, node)
            elif isinstance(node, ast.ClassDef):
                registry = app if node.name == "App" else surface
                for member in node.body:
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if member.name == "__init__":
                            _merge_signature(module, node.name, member)
                        elif node.name in {"App", "Page"}:
                            _merge_signature(registry, member.name, member)
                if any(
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Name)
                    and decorator.func.id == "dataclass"
                    for decorator in node.decorator_list
                ):
                    fields = {
                        member.target.id
                        for member in node.body
                        if isinstance(member, ast.AnnAssign) and isinstance(member.target, ast.Name)
                    }
                    module[node.name] = SignatureShape(fields)
    return surface, app, module


def _call_keywords(call: ast.Call) -> set[str]:
    return {keyword.arg for keyword in call.keywords if keyword.arg is not None}


def _check_known_call(
    *,
    path: Path,
    line: int,
    name: str,
    call: ast.Call,
    registry: Mapping[str, SignatureShape],
    findings: list[str],
) -> bool:
    shape = registry.get(name)
    if shape is None:
        return False
    if not shape.accepts_var_keyword:
        unexpected = sorted(_call_keywords(call) - shape.keywords)
        if unexpected:
            findings.append(
                f"{display(path)}:{line}: {name}() uses undocumented keyword(s): "
                + ", ".join(unexpected)
            )
    return True


def check_python_examples(texts: Mapping[Path, str], findings: list[str]) -> int:
    try:
        surface, app, module = api_signature_registries(texts[PUBLIC_API])
    except SyntaxError as exc:
        findings.append(f"{display(PUBLIC_API)}: cannot build API signature registry: {exc}")
        return 0

    root_exports = table_first_cell_symbols(
        markdown_section(texts[PUBLIC_API], "## Root export inventory", "## Common types")
    )
    application_methods: set[str] = set()
    for path in CONTRACT_DOCUMENTS:
        for fence in python_fences(texts[path]):
            try:
                tree = ast.parse(fence.source)
            except SyntaxError:
                continue
            application_methods.update(
                member.name
                for node in tree.body
                if isinstance(node, ast.ClassDef)
                for member in node.body
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
            )

    parsed = 0
    for path in CONTRACT_DOCUMENTS:
        for fence in python_fences(texts[path]):
            try:
                tree = ast.parse(fence.source, filename=display(path))
            except SyntaxError as exc:
                offset = (exc.lineno or 1) - 1
                findings.append(
                    f"{display(path)}:{fence.line + offset}: invalid Python example: {exc.msg}"
                )
                continue
            parsed += 1
            local_methods = {
                member.name
                for node in tree.body
                if isinstance(node, ast.ClassDef)
                for member in node.body
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
                call_line = fence.line + call.lineno - 1
                function = call.func
                if not (
                    isinstance(function, ast.Attribute) and isinstance(function.value, ast.Name)
                ):
                    continue
                receiver = function.value.id
                name = function.attr
                if receiver in {"self", "page"}:
                    known = _check_known_call(
                        path=path,
                        line=call_line,
                        name=name,
                        call=call,
                        registry=surface,
                        findings=findings,
                    )
                    if not known and name not in local_methods and name not in application_methods:
                        findings.append(
                            f"{display(path)}:{call_line}: undocumented {receiver}.{name}() call"
                        )
                    if name == "dataframe" and "name" not in _call_keywords(call):
                        findings.append(
                            f"{display(path)}:{call_line}: dataframe() example requires name="
                        )
                elif receiver == "app":
                    if not _check_known_call(
                        path=path,
                        line=call_line,
                        name=name,
                        call=call,
                        registry=app,
                        findings=findings,
                    ):
                        findings.append(
                            f"{display(path)}:{call_line}: undocumented app.{name}() call"
                        )
                elif receiver == "ed":
                    if name not in root_exports:
                        findings.append(
                            f"{display(path)}:{call_line}: ed.{name}() is absent from root exports"
                        )
                    _check_known_call(
                        path=path,
                        line=call_line,
                        name=name,
                        call=call,
                        registry=module,
                        findings=findings,
                    )
    return parsed


def _is_example_tree(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.Import) and any(alias.name == "edron" for alias in node.names):
            return True
        if isinstance(node, ast.ClassDef) and any(
            isinstance(base, ast.Attribute)
            and isinstance(base.value, ast.Name)
            and base.value.id == "ed"
            for base in node.bases
        ):
            return True
    return False


def _annotation_expressions(tree: ast.Module) -> Iterable[ast.expr]:
    for node in ast.walk(tree):
        if isinstance(node, ast.arg) and node.annotation is not None:
            yield node.annotation
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is not None:
                yield node.returns
        elif isinstance(node, ast.AnnAssign):
            yield node.annotation
            if (
                isinstance(node.annotation, ast.Name)
                and node.annotation.id == "TypeAlias"
                and node.value is not None
            ):
                yield node.value
        elif isinstance(node, ast.ClassDef):
            yield from node.bases


def check_api_annotations_and_native_imports(markdown: str, findings: list[str]) -> int:
    trees: list[ast.Module] = []
    known = set(dir(builtins))
    imported_objects: dict[str, object] = {}
    native_import_count = 0

    for fence in python_fences(markdown):
        try:
            tree = ast.parse(fence.source)
        except SyntaxError:
            continue
        if _is_example_tree(tree):
            continue
        trees.append(tree)
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                known.add(node.name)
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                known.update(target.id for target in targets if isinstance(target, ast.Name))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    known.add(alias.asname or alias.name.split(".", 1)[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    known.add(alias.asname or alias.name)
                if node.module and node.module.startswith("hedron"):
                    try:
                        owner = importlib.import_module(node.module)
                    except ImportError as exc:  # pragma: no cover - exercised by repository state
                        findings.append(
                            f"{display(PUBLIC_API)}: cannot import native module "
                            f"{node.module}: {exc}"
                        )
                        continue
                    for alias in node.names:
                        if alias.name == "*":
                            continue
                        native_import_count += 1
                        if not hasattr(owner, alias.name):
                            findings.append(
                                f"{display(PUBLIC_API)}: native symbol missing: "
                                f"{node.module}.{alias.name}"
                            )
                            continue
                        imported_objects[alias.asname or alias.name] = getattr(owner, alias.name)

    unresolved: set[str] = set()
    for tree in trees:
        for expression in _annotation_expressions(tree):
            unresolved.update(
                node.id
                for node in ast.walk(expression)
                if isinstance(node, ast.Name) and node.id not in known
            )
    if unresolved:
        findings.append(
            f"{display(PUBLIC_API)}: unresolved API annotation name(s): "
            + ", ".join(sorted(unresolved))
        )

    for left, dotted in re.findall(
        r"^ed\.([A-Za-z_]\w*) is ([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+)\s*$",
        markdown,
        re.MULTILINE,
    ):
        module_name, attribute = dotted.rsplit(".", 1)
        try:
            expected = getattr(importlib.import_module(module_name), attribute)
        except (ImportError, AttributeError) as exc:
            findings.append(
                f"{display(PUBLIC_API)}: invalid native identity authority {dotted}: {exc}"
            )
            continue
        imported = imported_objects.get(left)
        if imported is None:
            findings.append(
                f"{display(PUBLIC_API)}: identity re-export {left} lacks its documented import"
            )
        elif imported is not expected:
            findings.append(
                f"{display(PUBLIC_API)}: identity re-export {left} disagrees with {dotted}"
            )
    return native_import_count


def check_metadata(texts: Mapping[Path, str], findings: list[str]) -> None:
    for path in CONTRACT_DOCUMENTS:
        if TARGET_TEXT not in texts[path]:
            findings.append(f"{display(path)}: missing canonical Edron 0.1 target metadata")
        if "EDRON_ROADMAP.md" not in texts[path]:
            findings.append(f"{display(path)}: missing Edron roadmap link")
    for path in (GOLDENS, IMPLEMENTATION, ACCEPTANCE):
        if BASELINE_TEXT not in texts[path]:
            findings.append(f"{display(path)}: missing canonical planning baseline")


def check_root_exports(texts: Mapping[Path, str], findings: list[str]) -> int:
    try:
        api = table_first_cell_symbols(
            markdown_section(texts[PUBLIC_API], "## Root export inventory", "## Common types")
        )
        inventory = table_first_cell_symbols(
            markdown_section(
                texts[INVENTORY],
                "## Inventory 0: beginner root exports",
                "## Inventory A: application and composition",
            )
        )
    except ValueError as exc:
        findings.append(str(exc))
        return 0
    if api != inventory:
        findings.append(
            "Edron root export inventory drift: "
            f"API-only={sorted(api - inventory)}, inventory-only={sorted(inventory - api)}"
        )
    return len(api)


def _requirement_prefix(path: Path, requirement_id: str) -> bool:
    if path == STATE:
        return requirement_id.startswith("EDR-SI-")
    if path == PACKAGING:
        return requirement_id.startswith("EDR-PKG-")
    if path == INVENTORY:
        return requirement_id.startswith("EDR-INV-")
    if path == IMPLEMENTATION:
        return requirement_id.startswith("EDR-IMPL-")
    if path == RFC:
        return not requirement_id.startswith(("EDR-SI-", "EDR-PKG-", "EDR-INV-", "EDR-IMPL-"))
    return False


def check_requirement_ids(texts: Mapping[Path, str], findings: list[str]) -> int:
    total = 0
    for path, expected in EXPECTED_REQUIREMENT_COUNTS.items():
        ids = [
            requirement_id
            for requirement_id in REQUIREMENT_DEFINITION.findall(texts[path])
            if _requirement_prefix(path, requirement_id)
        ]
        duplicates = sorted(name for name, count in Counter(ids).items() if count > 1)
        if duplicates:
            findings.append(f"{display(path)}: duplicate acceptance IDs: {', '.join(duplicates)}")
        if len(ids) != expected:
            findings.append(
                f"{display(path)}: expected {expected} acceptance IDs, found {len(ids)}"
            )
        total += len(ids)

    capability_ids = CAPABILITY_ROW.findall(texts[INVENTORY])
    duplicates = sorted(name for name, count in Counter(capability_ids).items() if count > 1)
    if duplicates:
        findings.append(f"{display(INVENTORY)}: duplicate capability rows: {', '.join(duplicates)}")
    public_capabilities = [name for name in capability_ids if not name.startswith("PKG-BASE-")]
    if len(capability_ids) != 134 or len(public_capabilities) != 128:
        findings.append(
            f"{display(INVENTORY)}: expected 134 total/128 non-base capability rows, found "
            f"{len(capability_ids)} total/{len(public_capabilities)} non-base"
        )
    return total


def _human_gate_states(markdown: str) -> dict[str, str]:
    states: dict[str, str] = {}
    for line in markdown.splitlines():
        match = re.match(
            r"^\| `(EDR-(?:DESIGN|ENTRY|RELEASE)-[A-Z0-9-]+-\d{3})` \|",
            line,
        )
        if not match:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        gate_id = match.group(1)
        if gate_id in states:
            raise ValueError(f"duplicate human gate row: {gate_id}")
        states[gate_id] = cells[-1]
    return states


def check_release_gate(texts: Mapping[Path, str], findings: list[str]) -> int:
    try:
        gate = tomllib.loads(RELEASE_GATE.read_text(encoding="utf-8"))
        human = _human_gate_states(texts[ACCEPTANCE])
    except (OSError, tomllib.TOMLDecodeError, ValueError) as exc:
        findings.append(f"Edron release gate cannot be parsed: {exc}")
        return 0

    rows = gate.get("gate", [])
    if gate.get("target") != MACHINE_TARGET:
        findings.append(f"release gate target must be {MACHINE_TARGET!r}")
    if gate.get("planning_baseline") != MACHINE_BASELINE:
        findings.append(f"release gate planning_baseline must be {MACHINE_BASELINE!r}")
    if gate.get("acceptance_packet") != ACCEPTANCE.name:
        findings.append("release gate acceptance_packet does not name EDRON_001.md")
    if gate.get("upstream_lock") != UPSTREAM_LOCK.name:
        findings.append("release gate upstream_lock does not name the canonical upstream lock")
    ids = [row.get("id") for row in rows]
    duplicates = sorted(name for name, count in Counter(ids).items() if count > 1)
    if duplicates:
        findings.append(f"duplicate machine release gates: {', '.join(duplicates)}")
    machine = {row.get("id"): row for row in rows}
    if set(human) != set(machine):
        findings.append(
            "human/TOML release gate drift: "
            f"human-only={sorted(set(human) - set(machine))}, "
            f"TOML-only={sorted(set(machine) - set(human))}"
        )
    for gate_id in sorted(set(human) & set(machine)):
        if human[gate_id] != machine[gate_id].get("state"):
            findings.append(
                f"{gate_id}: human state {human[gate_id]!r} != "
                f"TOML state {machine[gate_id].get('state')!r}"
            )

    phase_counts = Counter(row.get("phase") for row in rows)
    if dict(phase_counts) != EXPECTED_GATE_PHASE_COUNTS:
        findings.append(
            f"release gate phase counts drift: expected {EXPECTED_GATE_PHASE_COUNTS}, "
            f"found {dict(phase_counts)}"
        )
    allowed_states = {"Planned", "Blocked", "Verified"}
    for row in rows:
        gate_id = row.get("id", "<missing>")
        state = row.get("state")
        if state not in allowed_states:
            findings.append(f"{gate_id}: invalid required-gate state {state!r}")
        if state == "Blocked" and not row.get("blocker"):
            findings.append(f"{gate_id}: Blocked gate lacks blocker")
        if state == "Verified" and row.get("blocker"):
            findings.append(f"{gate_id}: Verified gate retains blocker")
        if row.get("required") is not True:
            findings.append(f"{gate_id}: Edron 0.1 gate is not marked required")

    decisions = {row.get("id"): row for row in gate.get("decision", [])}
    decision_fields = {
        "A": "design_accepted",
        "B": "implementation_authorized",
        "C": "release_ready",
    }
    for decision_id, field in decision_fields.items():
        decision = decisions.get(decision_id)
        if decision is None:
            findings.append(f"release gate is missing Decision {decision_id}")
            continue
        if bool(decision.get("authorized")) != bool(gate.get(field)):
            findings.append(f"Decision {decision_id} disagrees with top-level {field}")
        if decision.get("authorized"):
            prefix = decision.get("required_gate_prefix", "")
            required = [row for row in rows if str(row.get("id", "")).startswith(prefix)]
            if decision.get("state") != "Verified" or any(
                row.get("state") != "Verified" for row in required
            ):
                findings.append(
                    f"Decision {decision_id} is authorized without all required gates Verified"
                )
    if decisions.get("B", {}).get("authorized") and not decisions.get("A", {}).get("authorized"):
        findings.append("Decision B is authorized before Decision A")
    if decisions.get("C", {}).get("authorized") and not decisions.get("B", {}).get("authorized"):
        findings.append("Decision C is authorized before Decision B")

    for artifact in gate.get("artifact", []):
        if "path" in artifact:
            target = (RELEASE_GATE.parent / artifact["path"]).resolve()
            if not target.exists():
                findings.append(
                    f"release artifact {artifact.get('id')} points to missing {artifact['path']}"
                )
        elif "planned_path" in artifact:
            target = (RELEASE_GATE.parent / artifact["planned_path"]).resolve()
            if target.exists():
                findings.append(
                    f"release artifact {artifact.get('id')} exists but remains planned_path"
                )
        else:
            findings.append(f"release artifact {artifact.get('id')} has no path/planned_path")
    return len(rows)


def check_upstream(texts: Mapping[Path, str], findings: list[str]) -> int:
    expected = set(EXPECTED_UPSTREAM_IDS)
    for path in (RFC, PUBLIC_API, INVENTORY, ACCEPTANCE):
        found = set(re.findall(r"\bUP-\d{3}\b", texts[path]))
        if found != expected:
            findings.append(
                f"{display(path)}: upstream ID drift: "
                f"missing={sorted(expected - found)}, extra={sorted(found - expected)}"
            )
    expected_workstream_ids = set(EXPECTED_UPSTREAM_WORKSTREAMS)
    for path in (ROADMAP, RFC, INVENTORY, IMPLEMENTATION, ACCEPTANCE):
        found = set(re.findall(r"\bHEDRON-WS-[A-Z]+\b", texts[path]))
        if found != expected_workstream_ids:
            findings.append(
                f"{display(path)}: upstream workstream drift: "
                f"missing={sorted(expected_workstream_ids - found)}, "
                f"extra={sorted(found - expected_workstream_ids)}"
            )

    try:
        lock = tomllib.loads(UPSTREAM_LOCK.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        findings.append(f"Edron upstream lock cannot be parsed: {exc}")
        return 0
    rows = lock.get("requirement", [])
    workstreams = lock.get("workstream", [])
    if lock.get("target") != MACHINE_TARGET:
        findings.append(f"upstream lock target must be {MACHINE_TARGET!r}")
    if lock.get("planning_baseline") != MACHINE_BASELINE:
        findings.append(f"upstream lock planning_baseline must be {MACHINE_BASELINE!r}")
    if lock.get("workstream_count") != len(EXPECTED_UPSTREAM_WORKSTREAMS):
        findings.append("upstream lock workstream_count is stale")
    workstream_ids = [row.get("id") for row in workstreams]
    if workstream_ids != list(EXPECTED_UPSTREAM_WORKSTREAMS):
        findings.append(
            "upstream lock workstream order or IDs drift: "
            f"expected {list(EXPECTED_UPSTREAM_WORKSTREAMS)}, found {workstream_ids}"
        )
    assigned: list[str] = []
    for workstream in workstreams:
        workstream_id = workstream.get("id")
        requirements = workstream.get("requirements", [])
        expected_requirements = EXPECTED_UPSTREAM_WORKSTREAMS.get(workstream_id)
        if requirements != list(expected_requirements or ()):
            findings.append(f"{workstream_id}: requirement membership drift: found {requirements}")
        assigned.extend(requirements)
        for field in (
            "owner",
            "objective",
            "native_packages",
            "deliverables",
            "acceptance_focus",
        ):
            if not workstream.get(field):
                findings.append(f"{workstream_id}: workstream lacks {field}")
        if workstream.get("state") != "Blocked" or not workstream.get("blocker"):
            findings.append(f"{workstream_id}: unresolved workstream must be Blocked")
    duplicate_assignments = sorted(
        requirement_id for requirement_id, count in Counter(assigned).items() if count > 1
    )
    if duplicate_assignments or set(assigned) != expected:
        findings.append(
            "upstream workstreams must partition UP-001..UP-011 exactly once: "
            f"duplicates={duplicate_assignments}, missing={sorted(expected - set(assigned))}, "
            f"extra={sorted(set(assigned) - expected)}"
        )
    expected_workstream_by_requirement = {
        requirement_id: workstream_id
        for workstream_id, requirement_ids in EXPECTED_UPSTREAM_WORKSTREAMS.items()
        for requirement_id in requirement_ids
    }
    ids = [row.get("id") for row in rows]
    if ids != list(EXPECTED_UPSTREAM_IDS):
        findings.append(f"upstream lock must contain ordered UP-001..UP-011, found {ids}")
    resolved_states = set(lock.get("resolution_states", []))
    if resolved_states != {"Existing", "Shipped"}:
        findings.append("upstream lock resolution_states must be exactly Existing and Shipped")
    resolved: list[bool] = []
    for row in rows:
        requirement_id = row.get("id")
        if row.get("workstream") != expected_workstream_by_requirement.get(requirement_id):
            findings.append(f"{requirement_id}: upstream workstream assignment drift")
        row_resolved = row.get("resolution") in resolved_states
        resolved.append(row_resolved)
        if row_resolved and row.get("state") != "Verified":
            findings.append(f"{row.get('id')}: resolved upstream row is not Verified")
        if not row_resolved:
            if row.get("state") != "Blocked":
                findings.append(f"{row.get('id')}: unresolved upstream row is not Blocked")
            if not row.get("blocker"):
                findings.append(f"{row.get('id')}: unresolved upstream row lacks blocker")
    all_resolved = bool(resolved) and all(resolved)
    if bool(lock.get("all_resolved")) != all_resolved:
        findings.append("upstream lock all_resolved disagrees with requirement rows")
    if lock.get("implementation_entry_satisfied") and not all_resolved:
        findings.append("upstream implementation entry is satisfied with unresolved rows")
    return len(rows)


def check_optional_dependencies(texts: Mapping[Path, str], findings: list[str]) -> int:
    try:
        api = optional_requirements(texts[PUBLIC_API])
        package = optional_requirements(texts[PACKAGING])
    except ValueError as exc:
        findings.append(f"optional dependency tables cannot be parsed: {exc}")
        return 0
    if api != EXPECTED_OPTIONAL_REQUIREMENTS:
        findings.append(f"{display(PUBLIC_API)}: optional requirement table drift: {api}")
    if package != EXPECTED_OPTIONAL_REQUIREMENTS:
        findings.append(f"{display(PACKAGING)}: optional requirement table drift: {package}")
    for path in (RFC, PACKAGING, GOLDENS):
        for command in (
            'pip install "plotly>=5.18,<7"',
            'pip install "edron[plotly]>=1.0.1,<1.1"',
        ):
            if command not in texts[path]:
                findings.append(f"{display(path)}: missing exact remediation {command!r}")
    return len(package)


def _machine_table(
    document: Mapping[str, Any], key: str, path: Path, findings: list[str]
) -> dict[str, Any]:
    value = document.get(key)
    if isinstance(value, dict):
        return cast(dict[str, Any], value)
    findings.append(f"{display(path)}: {key} must be a TOML table")
    return {}


def _machine_rows(
    document: Mapping[str, Any], key: str, path: Path, findings: list[str]
) -> list[dict[str, Any]]:
    value = document.get(key)
    if not isinstance(value, list):
        findings.append(f"{display(path)}: {key} must be an array of TOML tables")
        return []
    rows = cast(list[object], value)
    if not all(isinstance(row, dict) for row in rows):
        findings.append(f"{display(path)}: {key} must be an array of TOML tables")
        return []
    return [cast(dict[str, Any], row) for row in rows]


def _string_list(value: object) -> list[str] | None:
    if not isinstance(value, list):
        return None
    values = cast(list[object], value)
    if not all(isinstance(item, str) for item in values):
        return None
    return cast(list[str], values)


def _row_ids(rows: Iterable[Mapping[str, Any]]) -> list[Any]:
    return [row.get("id") for row in rows]


def check_machine_drafts(texts: Mapping[Path, str], findings: list[str]) -> int:
    drafts: dict[Path, dict[str, Any]] = {}
    for path in MACHINE_DRAFTS.values():
        try:
            drafts[path] = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            findings.append(f"{display(path)}: machine draft cannot be parsed: {exc}")

    if len(drafts) != len(MACHINE_DRAFTS):
        return len(drafts)

    for path, draft in drafts.items():
        if draft.get("schema_version") != 1:
            findings.append(f"{display(path)}: schema_version must be 1")
        if draft.get("target") != MACHINE_TARGET:
            findings.append(f"{display(path)}: target must be {MACHINE_TARGET!r}")
        if draft.get("planning_baseline") != MACHINE_BASELINE:
            findings.append(f"{display(path)}: planning_baseline must be {MACHINE_BASELINE!r}")
        if draft.get("status") != "Draft and blocked":
            findings.append(f"{display(path)}: status must be 'Draft and blocked'")
        for flag in ("accepted", "complete", "locked"):
            if draft.get(flag) is not False:
                findings.append(f"{display(path)}: {flag} must remain false in this draft")
        blockers = _string_list(draft.get("blockers"))
        if not blockers or not all(blockers):
            findings.append(f"{display(path)}: blockers must be a non-empty string array")

    try:
        expected_exports: set[str] = table_first_cell_symbols(
            markdown_section(texts[PUBLIC_API], "## Root export inventory", "## Common types")
        )
    except ValueError as exc:
        findings.append(str(exc))
        expected_exports = set()

    capability = drafts[CAPABILITY_MANIFEST]
    capability_root = _machine_table(capability, "root", CAPABILITY_MANIFEST, findings)
    manifest_exports = _string_list(capability_root.get("exports"))
    if manifest_exports is None or set(manifest_exports) != expected_exports:
        findings.append(f"{display(CAPABILITY_MANIFEST)}: root exports drift from public API")
    inventory = _machine_table(capability, "inventory", CAPABILITY_MANIFEST, findings)
    manifest_ids = inventory.get("ids")
    expected_capability_ids = CAPABILITY_ROW.findall(texts[INVENTORY])
    if manifest_ids != expected_capability_ids:
        findings.append(
            f"{display(CAPABILITY_MANIFEST)}: ordered capability IDs drift from inventory"
        )
    if capability.get("inventory_row_count") != len(expected_capability_ids):
        findings.append(f"{display(CAPABILITY_MANIFEST)}: inventory_row_count is stale")
    non_base = [
        capability_id
        for capability_id in expected_capability_ids
        if not capability_id.startswith("PKG-BASE-")
    ]
    if capability.get("non_base_capability_count") != len(non_base):
        findings.append(f"{display(CAPABILITY_MANIFEST)}: non_base_capability_count is stale")
    capability_partitions = {
        "base_package_ids": [
            capability_id
            for capability_id in expected_capability_ids
            if capability_id.startswith("PKG-BASE-")
        ],
        "upstream_ids": list(EXPECTED_UPSTREAM_IDS),
        "deferred_ids": [
            capability_id
            for capability_id in expected_capability_ids
            if capability_id.startswith("DEF-")
        ],
    }
    for field, expected_ids in capability_partitions.items():
        if inventory.get(field) != expected_ids:
            findings.append(f"{display(CAPABILITY_MANIFEST)}: {field} drift from inventory")
    count_fields = {
        "root_export_count": len(expected_exports),
        "optional_capability_count": len(EXPECTED_OPTIONAL_REQUIREMENTS),
        "upstream_requirement_count": len(EXPECTED_UPSTREAM_IDS),
        "native_capability_count": len(
            [name for name in expected_capability_ids if name.startswith("NATIVE-")]
        ),
        "deferred_capability_count": len(capability_partitions["deferred_ids"]),
    }
    for field, expected_count in count_fields.items():
        if capability.get(field) != expected_count:
            findings.append(f"{display(CAPABILITY_MANIFEST)}: {field} is stale")

    manifest_optional_rows = _machine_rows(capability, "optional", CAPABILITY_MANIFEST, findings)
    manifest_optional: dict[str, tuple[str, ...]] = {}
    for row in manifest_optional_rows:
        shortcut = row.get("shortcut")
        match = (
            re.fullmatch(r"edron\[([a-z0-9-]+)\]", shortcut) if isinstance(shortcut, str) else None
        )
        requirements = _string_list(row.get("requirements"))
        if match is None or requirements is None:
            findings.append(f"{display(CAPABILITY_MANIFEST)}: malformed optional row")
            continue
        manifest_optional[match.group(1)] = tuple(requirements)
    if manifest_optional != EXPECTED_OPTIONAL_REQUIREMENTS:
        findings.append(
            f"{display(CAPABILITY_MANIFEST)}: optional requirements drift: {manifest_optional}"
        )

    package = drafts[PACKAGE_LOCK]
    distributions = _machine_rows(package, "required_distribution", PACKAGE_LOCK, findings)
    if _row_ids(distributions) != list(EXPECTED_REQUIRED_DISTRIBUTION_IDS):
        findings.append(f"{display(PACKAGE_LOCK)}: required distribution rows drift")
    package_optional_rows = _machine_rows(package, "optional", PACKAGE_LOCK, findings)
    package_optional: dict[str, tuple[str, ...]] = {}
    for row in package_optional_rows:
        extra = row.get("extra")
        requirements = _string_list(row.get("requirements"))
        if not isinstance(extra, str) or requirements is None:
            findings.append(f"{display(PACKAGE_LOCK)}: malformed optional row")
            continue
        package_optional[extra] = tuple(requirements)
    if package_optional != EXPECTED_OPTIONAL_REQUIREMENTS:
        findings.append(f"{display(PACKAGE_LOCK)}: optional requirements drift: {package_optional}")

    api_lock = drafts[PUBLIC_API_LOCK]
    api_root = _machine_table(api_lock, "root", PUBLIC_API_LOCK, findings)
    locked_exports = _string_list(api_root.get("exports"))
    if locked_exports is None or set(locked_exports) != expected_exports:
        findings.append(f"{display(PUBLIC_API_LOCK)}: root exports drift from public API")
    if api_root.get("count") != len(expected_exports):
        findings.append(f"{display(PUBLIC_API_LOCK)}: root export count is stale")
    try:
        diagnostic_section = markdown_section(
            texts[PUBLIC_API], "### Stable Edron diagnostic codes", "### HTTP behavior"
        )
        expected_codes = re.findall(
            r"^\| `(EDR-[A-Z]+-\d{4})` \|", diagnostic_section, re.MULTILINE
        )
    except ValueError as exc:
        findings.append(str(exc))
        expected_codes = []
    diagnostics = _machine_table(api_lock, "diagnostics", PUBLIC_API_LOCK, findings)
    if diagnostics.get("codes") != expected_codes:
        findings.append(f"{display(PUBLIC_API_LOCK)}: diagnostic code snapshot drift")
    if api_lock.get("signature_snapshot_state") != "Unfrozen":
        findings.append(f"{display(PUBLIC_API_LOCK)}: signature snapshot must remain Unfrozen")
    if api_lock.get("signature_snapshot_sha256") != "unassigned":
        findings.append(f"{display(PUBLIC_API_LOCK)}: draft signature digest must be unassigned")

    lowering_rows = _machine_rows(drafts[LOWERING_MATRIX], "lowering", LOWERING_MATRIX, findings)
    if _row_ids(lowering_rows) != list(EXPECTED_LOWERING_IDS):
        findings.append(f"{display(LOWERING_MATRIX)}: lowering row order or IDs drift")
    for row in lowering_rows:
        row_id = row.get("id", "<missing>")
        for field in ("edron_surface", "native_authority"):
            if not isinstance(row.get(field), list) or not row[field]:
                findings.append(f"{display(LOWERING_MATRIX)}: {row_id} lacks {field}")
        if not isinstance(row.get("fallback"), str) or not row["fallback"]:
            findings.append(f"{display(LOWERING_MATRIX)}: {row_id} lacks fallback")
        upstream = _string_list(row.get("upstream", []))
        if upstream is None or not set(upstream) <= set(EXPECTED_UPSTREAM_IDS):
            findings.append(f"{display(LOWERING_MATRIX)}: {row_id} has invalid upstream IDs")
        if row.get("state") == "Verified":
            findings.append(f"{display(LOWERING_MATRIX)}: draft {row_id} cannot be Verified")

    state_lock = drafts[STATE_INTERACTION_MATRIX]
    state_rows = _machine_rows(state_lock, "state", STATE_INTERACTION_MATRIX, findings)
    interaction_rows = _machine_rows(state_lock, "interaction", STATE_INTERACTION_MATRIX, findings)
    if _row_ids(state_rows) != list(EXPECTED_STATE_IDS):
        findings.append(f"{display(STATE_INTERACTION_MATRIX)}: state row order or IDs drift")
    if _row_ids(interaction_rows) != list(EXPECTED_INTERACTION_IDS):
        findings.append(f"{display(STATE_INTERACTION_MATRIX)}: interaction row order or IDs drift")
    for row in state_rows:
        row_id = row.get("id", "<missing>")
        for field in ("value", "owner", "writer", "lifetime", "persistence", "concurrency"):
            if not isinstance(row.get(field), str) or not row[field]:
                findings.append(f"{display(STATE_INTERACTION_MATRIX)}: {row_id} lacks {field}")
        if row.get("state") == "Verified":
            findings.append(
                f"{display(STATE_INTERACTION_MATRIX)}: draft {row_id} cannot be Verified"
            )
    for row in interaction_rows:
        row_id = row.get("id", "<missing>")
        for field in ("surface", "method", "htmx", "ordinary_http", "no_javascript"):
            if not isinstance(row.get(field), str) or not row[field]:
                findings.append(f"{display(STATE_INTERACTION_MATRIX)}: {row_id} lacks {field}")
        if not isinstance(row.get("csrf"), bool) or not isinstance(row.get("mutation"), bool):
            findings.append(
                f"{display(STATE_INTERACTION_MATRIX)}: {row_id} lacks boolean CSRF/mutation facts"
            )
        upstream = _string_list(row.get("upstream", []))
        if upstream is None or not set(upstream) <= set(EXPECTED_UPSTREAM_IDS):
            findings.append(
                f"{display(STATE_INTERACTION_MATRIX)}: {row_id} has invalid upstream IDs"
            )
        if row.get("state") == "Verified":
            findings.append(
                f"{display(STATE_INTERACTION_MATRIX)}: draft {row_id} cannot be Verified"
            )

    fixture = drafts[FIXTURE_LOCK]
    golden_rows = _machine_rows(fixture, "golden", FIXTURE_LOCK, findings)
    focused_rows = _machine_rows(fixture, "focused", FIXTURE_LOCK, findings)
    if _row_ids(golden_rows) != list(EXPECTED_GOLDEN_IDS):
        findings.append(f"{display(FIXTURE_LOCK)}: golden row order or IDs drift")
    if _row_ids(focused_rows) != list(EXPECTED_FOCUSED_IDS):
        findings.append(f"{display(FIXTURE_LOCK)}: focused row order or IDs drift")
    for row in (*golden_rows, *focused_rows):
        row_id = row.get("id", "<missing>")
        if row.get("materialized_source") != "unassigned":
            findings.append(f"{display(FIXTURE_LOCK)}: {row_id} source is not draft-safe")
        if row.get("source_sha256") != "unassigned":
            findings.append(f"{display(FIXTURE_LOCK)}: {row_id} digest is not draft-safe")
        if row.get("state") != "Blocked":
            findings.append(f"{display(FIXTURE_LOCK)}: {row_id} must remain Blocked")
    known_capabilities = set(expected_capability_ids)
    for row in golden_rows:
        capabilities = _string_list(row.get("capabilities"))
        if capabilities is None or not set(capabilities) <= known_capabilities:
            findings.append(
                f"{display(FIXTURE_LOCK)}: {row.get('id', '<missing>')} has unknown capabilities"
            )
    for flag in ("all_sources_materialized", "all_hashes_frozen"):
        if fixture.get(flag) is not False:
            findings.append(f"{display(FIXTURE_LOCK)}: {flag} must remain false")

    performance = drafts[PERFORMANCE_LOCK]
    budget_rows = _machine_rows(performance, "budget", PERFORMANCE_LOCK, findings)
    budget_ids = _row_ids(budget_rows)
    if len(budget_ids) != EXPECTED_PERFORMANCE_BUDGET_COUNT:
        findings.append(
            f"{display(PERFORMANCE_LOCK)}: expected {EXPECTED_PERFORMANCE_BUDGET_COUNT} "
            f"budget rows, found {len(budget_ids)}"
        )
    duplicate_budgets = sorted(
        str(name) for name, count in Counter(budget_ids).items() if count > 1
    )
    if duplicate_budgets:
        findings.append(
            f"{display(PERFORMANCE_LOCK)}: duplicate budgets: {', '.join(duplicate_budgets)}"
        )
    for row in budget_rows:
        row_id = row.get("id", "<missing>")
        for field in ("metric", "unit", "direction", "mode", "comparator", "failure"):
            if not isinstance(row.get(field), str) or not row[field]:
                findings.append(f"{display(PERFORMANCE_LOCK)}: {row_id} lacks {field}")
        if row.get("limit_state") != "Unfrozen":
            findings.append(f"{display(PERFORMANCE_LOCK)}: {row_id} limit must be Unfrozen")
        if "limit" in row:
            findings.append(f"{display(PERFORMANCE_LOCK)}: {row_id} invents a draft limit")
    if performance.get("all_limits_frozen") is not False:
        findings.append(f"{display(PERFORMANCE_LOCK)}: all_limits_frozen must remain false")

    try:
        release = tomllib.loads(RELEASE_GATE.read_text(encoding="utf-8"))
        artifact_rows = _machine_rows(release, "artifact", RELEASE_GATE, findings)
        artifacts: dict[str, dict[str, Any]] = {}
        for row in artifact_rows:
            artifact_id = row.get("id")
            if isinstance(artifact_id, str):
                artifacts[artifact_id] = row
    except (OSError, tomllib.TOMLDecodeError):
        artifacts = {}
    for artifact_id, path in MACHINE_DRAFTS.items():
        artifact = artifacts.get(artifact_id, {})
        if artifact.get("path") != path.name or "planned_path" in artifact:
            findings.append(
                f"{display(RELEASE_GATE)}: {artifact_id} must point to existing {path.name}"
            )
        if artifact.get("state") != "Blocked" or not artifact.get("blocker"):
            findings.append(
                f"{display(RELEASE_GATE)}: {artifact_id} must remain Blocked with a blocker"
            )

    return len(drafts)


def check_links(texts: Mapping[Path, str], findings: list[str]) -> int:
    checked = 0
    for path, markdown in texts.items():
        without_code = re.sub(r"```.*?```", "", markdown, flags=re.DOTALL)
        for line_number, line in enumerate(without_code.splitlines(), start=1):
            for raw_target in MARKDOWN_LINK.findall(line):
                target = raw_target.strip("<>")
                if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith(("#", "//")):
                    continue
                path_text, separator, fragment = target.partition("#")
                relative = urllib.parse.unquote(path_text)
                if not relative:
                    continue
                checked += 1
                resolved = (path.parent / relative).resolve()
                if not resolved.exists():
                    findings.append(
                        f"{display(path)}:{line_number}: missing link target {target!r}"
                    )
                    continue
                if separator and fragment and resolved.suffix.lower() == ".md":
                    slugs = markdown_heading_slugs(resolved.read_text(encoding="utf-8"))
                    if fragment not in slugs:
                        findings.append(
                            f"{display(path)}:{line_number}: missing anchor "
                            f"#{fragment} in {display(resolved)}"
                        )
    return checked


def check_roadmap_and_stages(texts: Mapping[Path, str], findings: list[str]) -> None:
    roadmap = texts[ROADMAP]
    headings = re.findall(r"^## Phase (\d+\.\d+)\b", roadmap, re.MULTILINE)
    expected = [f"0.{number}" for number in range(10)]
    if headings != expected:
        findings.append(f"Edron roadmap phase headings must be 0.0..0.9, found {headings}")
    summary = re.findall(r"^\| \*\*(\d+\.\d+)\*\* \|", roadmap, re.MULTILINE)
    expected_summary = [*expected, "1.0"]
    if summary != expected_summary:
        findings.append(f"Edron roadmap summary must be 0.0..1.0, found {summary}")
    if re.search(r"^## Phase 1\.", roadmap, re.MULTILINE):
        findings.append("Edron roadmap must not define a 1.x phase")
    canonical_boundary = (
        "Edron `1.0` is the first release that directly adopts Hedron's canonical 1.0 interface"
    )
    if canonical_boundary not in roadmap:
        findings.append("Edron roadmap must declare the canonical 1.0 adoption boundary")

    stages = re.findall(r"^### Stage (\d+)\b", texts[IMPLEMENTATION], re.MULTILINE)
    if stages != [str(number) for number in range(8)]:
        findings.append(f"Edron implementation stages must be 0..7, found {stages}")
    normalized = " ".join(texts[IMPLEMENTATION].split())
    for required in (
        "Exit requires Decision A in the acceptance packet.",
        "Exit requires Decision B;",
        "no `packages/edron` runtime slice begins until the acceptance packet records "
        "Decision B as Verified",
    ):
        if required not in normalized:
            findings.append(
                f"{display(IMPLEMENTATION)}: missing authorization invariant {required!r}"
            )


def check_forbidden_drift(texts: Mapping[Path, str], findings: list[str]) -> None:
    combined = "\n".join(texts[path] for path in EDRON_DOCUMENTS)
    forbidden = {
        "EdronOptionalDependencyError": "use the stable capability exception hierarchy",
        "ed.JobBackend is hedron.JobBackend": "JobBackend is owned by hedron_core.jobs",
        "all 77": "do not freeze a fragile declaration count in prose",
        "77 declaration": "do not freeze a fragile declaration count in prose",
        "## Stage 0 exit gate": "golden readiness is not an authorization decision",
    }
    for phrase, reason in forbidden.items():
        if phrase in combined:
            findings.append(f"forbidden Edron drift phrase {phrase!r}: {reason}")
    if "Plain `edron check` projects conservative static source facts only" not in texts[STATE]:
        findings.append(f"{display(STATE)}: static check trust boundary is missing")
    if "`dashboard_panel` recipe" not in texts[RFC] or "`dashboard_panel`" not in texts[PUBLIC_API]:
        findings.append("raised variant must map consistently to dashboard_panel")


def check_all(root: Path = ROOT) -> tuple[list[str], dict[str, int]]:
    if root != ROOT:
        raise ValueError("alternate roots are not supported; patch module constants in tests")
    findings: list[str] = []
    required_paths = (*EDRON_DOCUMENTS, RELEASE_GATE, UPSTREAM_LOCK, *MACHINE_DRAFTS.values())
    missing = [path for path in required_paths if not path.exists()]
    if missing:
        return ([f"missing required Edron document: {display(path)}" for path in missing], {})
    texts = {path: path.read_text(encoding="utf-8") for path in EDRON_DOCUMENTS}

    check_metadata(texts, findings)
    root_exports = check_root_exports(texts, findings)
    requirements = check_requirement_ids(texts, findings)
    gates = check_release_gate(texts, findings)
    upstream = check_upstream(texts, findings)
    optional = check_optional_dependencies(texts, findings)
    machine_drafts = check_machine_drafts(texts, findings)
    examples = check_python_examples(texts, findings)
    native_imports = check_api_annotations_and_native_imports(texts[PUBLIC_API], findings)
    links = check_links(texts, findings)
    check_roadmap_and_stages(texts, findings)
    check_forbidden_drift(texts, findings)

    stats = {
        "documents": len(EDRON_DOCUMENTS),
        "python_examples": examples,
        "acceptance_ids": requirements,
        "root_exports": root_exports,
        "release_gates": gates,
        "upstream_requirements": upstream,
        "upstream_workstreams": len(EXPECTED_UPSTREAM_WORKSTREAMS),
        "optional_capabilities": optional,
        "machine_drafts": machine_drafts,
        "native_imports": native_imports,
        "local_links": links,
    }
    return findings, stats


def main() -> int:
    findings, stats = check_all()
    if findings:
        print("Edron documentation consistency check failed:", file=sys.stderr)
        print("\n".join(f"- {finding}" for finding in findings), file=sys.stderr)
        return 1
    print(
        "ok: Edron packet is consistent "
        f"({stats['documents']} docs, {stats['python_examples']} Python examples, "
        f"{stats['acceptance_ids']} acceptance IDs, {stats['root_exports']} root exports, "
        f"{stats['release_gates']} gates, {stats['upstream_requirements']} upstream rows, "
        f"{stats['upstream_workstreams']} upstream workstreams, "
        f"{stats['optional_capabilities']} optional capabilities, "
        f"{stats['machine_drafts']} machine drafts, "
        f"{stats['native_imports']} native imports, {stats['local_links']} local links)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
