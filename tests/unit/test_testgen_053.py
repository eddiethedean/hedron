"""TESTGEN-053 evidence."""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path
from types import SimpleNamespace

from hedron_core import GENERATOR_VERSION, generate_interaction_tests
from hedron_core.catalog import CatalogEntry, InteractionCatalog
from hedron_core.testgen import PATHS


def test_testgen_053_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.53.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["TESTGEN-053"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md").is_file()


def test_generate_interaction_tests_placeholders_are_deterministic() -> None:
    catalog = InteractionCatalog(app_id="demo", sealed=True)
    first = generate_interaction_tests(catalog, profile="default")
    second = generate_interaction_tests(catalog, profile="default")
    assert first == second
    assert GENERATOR_VERSION == "1.0.0"
    assert catalog.fingerprint in first
    for path in PATHS:
        assert f"test_placeholder_{path}" in first
    tree = ast.parse(first)
    assert any(
        isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        for node in tree.body
    )


def test_generate_interaction_tests_covers_kinds_without_exec() -> None:
    entries = {
        "views.home": CatalogEntry(
            logical_id="views.home",
            kind="view",
            descriptor_version=1,
            descriptor_fingerprint="a" * 32,
        ),
        "commands.save": CatalogEntry(
            logical_id="commands.save",
            kind="command",
            descriptor_version=1,
            descriptor_fingerprint="b" * 32,
        ),
    }
    # Hostile field that must remain a string literal, never executed.
    hostile = CatalogEntry(
        logical_id="views.__import__('os').system('echo pwned')",
        kind="view",
        descriptor_version=1,
        descriptor_fingerprint="c" * 32,
    )
    entries[hostile.logical_id] = hostile
    catalog = InteractionCatalog(app_id="demo", entries=entries, sealed=True)
    source = generate_interaction_tests(catalog, profile="ci", generator_version="1.0.0")
    again = generate_interaction_tests(catalog, profile="ci", generator_version="1.0.0")
    assert source == again
    for path in PATHS:
        assert f"path = {path!r}" in source or f'path = "{path}"' in source
    assert "views.home" in source
    assert "commands.save" in source
    # Redacted literal only — no exec/eval of catalog fields.
    assert "eval(" not in source
    assert "exec(" not in source
    assert "__import__" in source  # embedded as a string literal inside quotes
    compiled = compile(source, "<testgen>", "exec")
    namespace: dict[str, object] = {}
    exec(compiled, namespace)
    assert namespace["CATALOG_FINGERPRINT"] == catalog.fingerprint
    assert "test_catalog_fingerprint_matches_sealed" in namespace
    namespace["test_catalog_fingerprint_matches_sealed"]()
    # Duck-typed catalog also works.
    duck = SimpleNamespace(entries=entries, fingerprint=catalog.fingerprint)
    assert generate_interaction_tests(duck, profile="ci") == source


def test_profile_and_version_change_output() -> None:
    catalog = InteractionCatalog(app_id="demo", sealed=True)
    a = generate_interaction_tests(catalog, profile="a", generator_version="1.0.0")
    b = generate_interaction_tests(catalog, profile="b", generator_version="1.0.0")
    c = generate_interaction_tests(catalog, profile="a", generator_version="1.0.1")
    assert a != b
    assert a != c
