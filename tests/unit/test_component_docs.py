from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "scripts" / "generate_component_docs.py"


def _load_generator():
    spec = importlib.util.spec_from_file_location("generate_component_docs", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_every_builtin_has_a_current_dedicated_demo_page() -> None:
    generator = _load_generator()

    assert generator.check_inventory() == []
    expected = generator.expected_files()
    for path, content in expected.items():
        assert path.read_text() == content, f"regenerate {path.relative_to(ROOT)}"

    assert set((ROOT / "docs" / "components").glob("*.md")) == set(expected)
