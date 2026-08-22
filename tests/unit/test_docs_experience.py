from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"


def _front_matter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    assert match is not None, f"{path.relative_to(ROOT)} needs YAML front matter"
    parsed = yaml.safe_load(match.group(1))
    assert isinstance(parsed, dict)
    return parsed


def test_reader_entry_pages_have_descriptions_and_search_priority() -> None:
    priorities = {
        "index.md": 2.0,
        "getting-started/index.md": 1.7,
        "getting-started/installation.md": 1.7,
        "getting-started/quickstart.md": 2.0,
        "guides/index.md": 1.4,
        "guides/cookbook.md": 1.6,
        "guides/troubleshooting.md": 1.8,
        "guides/error-codes.md": 1.4,
        "guides/security.md": 1.6,
        "api/AUTODOC.md": 0.2,
    }

    for relative, priority in priorities.items():
        metadata = _front_matter(DOCS / relative)
        assert isinstance(metadata.get("description"), str)
        search = metadata.get("search")
        assert isinstance(search, dict)
        assert search.get("boost") == priority


def test_docs_enable_reader_experience_features() -> None:
    config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    for feature in (
        "navigation.path",
        "content.code.copy",
        "content.code.select",
        "content.tabs.link",
    ):
        assert f"- {feature}" in config

    assert "line_spans: __span" in config
    assert "pygments_lang_class: true" in config


def test_current_release_banner_and_not_found_page_are_helpful() -> None:
    main = (DOCS / "overrides" / "main.html").read_text(encoding="utf-8")
    not_found = (DOCS / "overrides" / "404.html").read_text(encoding="utf-8")

    assert "development_version != config.extra.hedron_docs.published_version" in main
    assert "stable v" in main
    assert "guides/current-release/" in main
    for destination in ("quickstart", "cookbook", "troubleshooting", "support"):
        assert destination in not_found
