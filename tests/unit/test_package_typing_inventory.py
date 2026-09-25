"""The strict package typing gate covers the complete uv workspace."""

from scripts.check_package_typing_inventory import (
    _basedpyright_include_roots,
    _workspace_package_source_roots,
)


def test_strict_typing_inventory_matches_workspace() -> None:
    assert _basedpyright_include_roots() == _workspace_package_source_roots()
