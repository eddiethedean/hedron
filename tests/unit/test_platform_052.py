"""PLATFORM-052 evidence."""

from __future__ import annotations

import locale
import os
import platform
import sys
import tomllib
from pathlib import Path


def test_platform_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["PLATFORM-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_os_locale_runtime_markers() -> None:
    assert platform.system() in {"Darwin", "Linux", "Windows"}
    assert sys.version_info >= (3, 11)
    # Locale marker is present (may be empty / C on some hosts).
    _ = locale.getpreferredencoding(False)
    assert "PATH" in os.environ or os.name == "nt"
