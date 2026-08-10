from scripts.check_api_docs_coverage import documented_symbols, public_exports


def test_public_exports_uses_the_last_all_assignment() -> None:
    source = '__all__ = ["Old"]\n__all__ = ["New", "helper"]\n'
    assert public_exports(source) == {"New", "helper"}


def test_documented_symbols_reads_grouped_code_spans() -> None:
    markdown = "| `Hedron`, `Page`, `render` | API docs |"
    assert documented_symbols(markdown) == {"Hedron", "Page", "render"}


def test_documented_symbols_ignores_import_paths_and_prose() -> None:
    markdown = "Use `hedron.Page` from `hedron`; ordinary words are not symbols."
    assert documented_symbols(markdown) == {"hedron"}
