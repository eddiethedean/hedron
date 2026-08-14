from scripts.check_api_docs_coverage import (
    cli_commands,
    documented_cli_commands,
    documented_symbols,
    public_exports,
)


def test_public_exports_uses_the_last_all_assignment() -> None:
    source = '__all__ = ["Old"]\n__all__ = ["New", "helper"]\n'
    assert public_exports(source) == {"New", "helper"}


def test_documented_symbols_reads_grouped_code_spans() -> None:
    markdown = "| `Hedron`, `Page`, `render` | API docs |"
    assert documented_symbols(markdown) == {"Hedron", "Page", "render"}


def test_documented_symbols_ignores_import_paths_and_prose() -> None:
    markdown = "Use `hedron.Page` from `hedron`; ordinary words are not symbols."
    assert documented_symbols(markdown) == {"hedron"}


def test_cli_commands_reads_only_top_level_subparser_literals() -> None:
    source = """
sub.add_parser("new")
migrate_sub.add_parser("streamlit")
sub.add_parser(command_name)
"""
    assert cli_commands(source) == {"new"}


def test_documented_cli_commands_reads_grouped_and_nested_headings() -> None:
    markdown = """
### `routes` / `components`
### `migrate streamlit`
## Errors
"""
    assert documented_cli_commands(markdown) == {"routes", "components", "migrate"}
