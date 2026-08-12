"""Unit tests for Streamlit migrator discovery and project-root defaults."""

from __future__ import annotations

from pathlib import Path

from hedron.migrate.discovery import discover_sources, resolve_project_root


def test_resolve_project_root_walks_up(tmp_path: Path) -> None:
    root = tmp_path / "proj"
    nested = root / "apps" / "dash"
    nested.mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    entry = nested / "streamlit_app.py"
    entry.write_text("import streamlit as st\nst.title('x')\n", encoding="utf-8")
    assert resolve_project_root(entry) == root.resolve()


def test_resolve_project_root_falls_back_to_parent(tmp_path: Path) -> None:
    entry = tmp_path / "solo.py"
    entry.write_text("import streamlit as st\n", encoding="utf-8")
    assert resolve_project_root(entry) == tmp_path.resolve()


def test_discover_single_file(tmp_path: Path) -> None:
    entry = tmp_path / "streamlit_app.py"
    entry.write_text("import streamlit as st\nst.title('Hi')\n", encoding="utf-8")
    discovered = discover_sources(entry)
    assert discovered.entrypoint == entry.resolve()
    assert discovered.files == (entry.resolve(),)


def test_discover_includes_pages(tmp_path: Path) -> None:
    entry = tmp_path / "streamlit_app.py"
    entry.write_text("import streamlit as st\n", encoding="utf-8")
    pages = tmp_path / "pages"
    pages.mkdir()
    page = pages / "2_About.py"
    page.write_text("import streamlit as st\nst.header('About')\n", encoding="utf-8")
    discovered = discover_sources(tmp_path)
    assert entry.resolve() in discovered.files
    assert page.resolve() in discovered.files
