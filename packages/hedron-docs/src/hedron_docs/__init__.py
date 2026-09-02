"""Experimental Markdown compiler and Hedron docs application toolkit."""

__version__ = "0.2.0"

from .app import create_docs_app
from .ast import DocNode, SourceSpan
from .config import DocsBuildConfig, NavigationItem, import_mkdocs, load_config
from .errors import Diagnostic, DocsError
from .manifest import AssetRecord, PageRecord, SiteManifest, compile_site, load_manifest
from .markdown import ParserLimits, parse_markdown, slugify
from .search import SearchResult, search

__all__ = [
    "Diagnostic",
    "DocNode",
    "DocsBuildConfig",
    "DocsError",
    "NavigationItem",
    "ParserLimits",
    "SourceSpan",
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
