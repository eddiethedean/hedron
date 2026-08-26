import pytest
from scripts.check_edron_docs import (
    EXPECTED_OPTIONAL_REQUIREMENTS,
    api_signature_registries,
    check_all,
    markdown_heading_slugs,
    optional_requirements,
    python_fences,
    table_first_cell_symbols,
)


def test_python_fences_preserve_source_line() -> None:
    markdown = "# Demo\n\nText\n\n```python\nvalue = 1\n```\n"

    assert [(fence.line, fence.source) for fence in python_fences(markdown)] == [(6, "value = 1\n")]


def test_table_first_cell_symbols_expands_grouped_exports() -> None:
    section = """
| Export | Kind |
|---|---|
| `Container` / `FilterScope` | values |
| `fragment` / `Fragment` / `BoundFragment` | descriptors |
"""

    assert table_first_cell_symbols(section) == {
        "Container",
        "FilterScope",
        "fragment",
        "Fragment",
        "BoundFragment",
    }


def test_optional_requirements_reads_shortcut_rows() -> None:
    markdown = """
| Capability | Requirements | Shortcut |
|---|---|---|
| Plotly | `plotly>=5.18,<7` | `edron[plotly]` |
| Altair | `altair>=6,<7` and `vl-convert-python>=1.0` | `edron[altair]` |
"""

    assert optional_requirements(markdown) == {
        "plotly": EXPECTED_OPTIONAL_REQUIREMENTS["plotly"],
        "altair": EXPECTED_OPTIONAL_REQUIREMENTS["altair"],
    }


def test_optional_requirements_rejects_duplicate_shortcut() -> None:
    markdown = """
| Capability | Requirements | Shortcut |
|---|---|---|
| Plotly | `plotly>=5.18,<7` | `edron[plotly]` |
| Plotly again | `plotly>=5.18,<7` | `edron[plotly]` |
"""

    with pytest.raises(ValueError, match=r"duplicate.*edron\[plotly\]"):
        optional_requirements(markdown)


def test_api_signature_registries_include_app_and_class_constructors() -> None:
    markdown = """
```python
from dataclasses import dataclass

class App:
    def __init__(self, *, title: str, debug: bool = False) -> None: ...
    def include(self, value: object) -> None: ...

class JobFlow:
    def __init__(self, *, name: str, job_type: str) -> None: ...

@dataclass(frozen=True)
class Confirm:
    message: str
    confirm_label: str = "Confirm"

def text(self, body: str, *, tone: str = "default") -> None: ...
```
"""

    surface, app, module = api_signature_registries(markdown)

    assert surface["text"].keywords == {"body", "tone"}
    assert app["include"].keywords == {"value"}
    assert module["App"].keywords == {"title", "debug"}
    assert module["JobFlow"].keywords == {"name", "job_type"}
    assert module["Confirm"].keywords == {"message", "confirm_label"}


def test_markdown_heading_slugs_support_contract_anchors() -> None:
    markdown = "## `dependency`\n\n## CLI contract\n\n### Stable Edron diagnostic codes\n"

    assert markdown_heading_slugs(markdown) == {
        "dependency",
        "cli-contract",
        "stable-edron-diagnostic-codes",
    }


def test_repository_edron_packet_is_consistent() -> None:
    findings, stats = check_all()

    assert findings == []
    assert stats["release_gates"] == 46
    assert stats["upstream_requirements"] == 11
    assert stats["upstream_workstreams"] == 5
    assert stats["machine_drafts"] == 7
