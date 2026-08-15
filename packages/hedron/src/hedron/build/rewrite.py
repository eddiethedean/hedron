"""JS/CSS URL rewrite for fingerprinted assets."""

from __future__ import annotations

import re
from pathlib import Path

_URL_RE = re.compile(r"url\(\s*(['\"]?)([^)'\"]+)\1\s*\)", re.IGNORECASE)
# Static/dynamic import and re-export specifiers with relative paths only.
_MODULE_SPEC_RE = re.compile(
    r"""(?P<head>\b(?:import|export)\b[^'"\n]*?\bfrom\s+|import\s*\(\s*)"""
    r"""(?P<quote>['"])(?P<spec>\.\.?/[^'"]+)(?P=quote)"""
)


def _rewrite_css_urls(css: str, url_map: dict[str, str]) -> str:
    """Rewrite relative url(...) values to fingerprinted public paths."""

    def repl(match: re.Match[str]) -> str:
        quote = match.group(1) or '"'
        url = match.group(2).strip()
        if url.startswith(("http://", "https://", "//", "data:", "/")):
            return match.group(0)
        rewritten = url_map.get(url)
        if rewritten is None:
            return match.group(0)
        return f"url({quote}{rewritten}{quote})"

    return _URL_RE.sub(repl, css)


def _rewrite_module_imports(js: str, basename_map: dict[str, str]) -> str:
    """Rewrite relative ES module specifiers to fingerprinted sibling filenames.

    Build flattens modules into one assets directory, so ``./foo.mjs`` becomes
    ``./foo.<digest>.mjs`` when ``foo.mjs`` was fingerprinted in the same pass.
    """

    def repl(match: re.Match[str]) -> str:
        spec = match.group("spec")
        name = Path(spec).name
        hashed = basename_map.get(name)
        if hashed is None or hashed == name:
            return match.group(0)
        return f"{match.group('head')}{match.group('quote')}./{hashed}{match.group('quote')}"

    return _MODULE_SPEC_RE.sub(repl, js)
