"""Experimental Markdown compiler and Hedron docs application toolkit."""

__version__ = "0.1.0"

from .app import create_docs_app
from .ast import DocNode
from .config import DocsBuildConfig, import_mkdocs, load_config
from .errors import Diagnostic, DocsError
from .manifest import AssetRecord, PageRecord, SiteManifest, compile_site, load_manifest
from .markdown import parse_markdown, slugify
from .search import SearchResult, search

__all__ = [
    "Diagnostic",
    "DocNode",
    "DocsBuildConfig",
    "DocsError",
    "AssetRecord",
    "PageRecord",
    "SearchResult",
    "SiteManifest",
    "compile_site",
    "create_docs_app",
    "import_mkdocs",
    "load_config",
    "load_manifest",
    "parse_markdown",
    "search",
    "slugify",
    "__version__",
]
