"""#275: Explorer HDJ inventory must not follow escaping symlinks."""

from __future__ import annotations

from pathlib import Path

from hedron_explorer.router import _hdj_text_under_root


def test_inventory_skips_symlink_escape(tmp_path: Path) -> None:
    root = tmp_path / "allowed"
    root.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("password-hash", encoding="utf-8")
    leak = root / "leak.hdj"
    leak.symlink_to(secret)
    assert _hdj_text_under_root(leak, root.resolve()) is None

    local = root / "ok.hdj"
    local.write_text("{% hedron %}", encoding="utf-8")
    assert _hdj_text_under_root(local, root.resolve()) == "{% hedron %}"
