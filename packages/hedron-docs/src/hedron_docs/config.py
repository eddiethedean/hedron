"""Configuration and bounded MkDocs migration import."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

from hedron_core.compat import tomllib

from .errors import source_error


@dataclass(frozen=True, slots=True)
class DocsBuildConfig:
    docs_dir: Path = Path("docs")
    output: Path = Path("build/hedron-docs/site.json")
    site_title: str = "Documentation"
    site_description: str = ""
    base_url: str = ""
    exclude: tuple[str, ...] = ()
    allow_external_links: bool = True
    max_source_bytes: int = 2_000_000
    max_asset_bytes: int = 10_000_000
    max_nodes: int = 10_000
    max_query_length: int = 200
    config_path: Path | None = field(default=None, compare=False)

    def __post_init__(self) -> None:
        if not self.site_title.strip():
            raise ValueError("site_title must not be empty")
        limits = (
            self.max_source_bytes,
            self.max_asset_bytes,
            self.max_nodes,
            self.max_query_length,
        )
        if any(type(value) is not int for value in limits):
            raise ValueError("compiler limits must be integers")
        if any(value < 1 for value in limits):
            raise ValueError("compiler limits must be positive")
        if self.base_url:
            parts = urlsplit(self.base_url)
            if (
                parts.scheme not in {"http", "https"}
                or not parts.netloc
                or parts.query
                or parts.fragment
                or parts.username is not None
                or parts.password is not None
                or "\\" in self.base_url
                or any(ord(char) < 0x20 for char in self.base_url)
            ):
                raise ValueError("base_url must be an absolute http(s) URL without query/fragment")

    def resolved(self, *, root: Path | None = None) -> DocsBuildConfig:
        base = (root or Path.cwd()).resolve()
        docs = self.docs_dir if self.docs_dir.is_absolute() else base / self.docs_dir
        output = self.output if self.output.is_absolute() else base / self.output
        return DocsBuildConfig(
            docs_dir=docs,
            output=output,
            site_title=self.site_title,
            site_description=self.site_description,
            base_url=self.base_url,
            exclude=self.exclude,
            allow_external_links=self.allow_external_links,
            max_source_bytes=self.max_source_bytes,
            max_asset_bytes=self.max_asset_bytes,
            max_nodes=self.max_nodes,
            max_query_length=self.max_query_length,
            config_path=self.config_path,
        )


def load_config(path: str | Path = "hedron-docs.toml") -> DocsBuildConfig:
    config_path = Path(path).resolve()
    try:
        raw_value: object = cast(object, tomllib.loads(config_path.read_text(encoding="utf-8")))
    except FileNotFoundError as exc:
        raise source_error("HED-DOCS-0002", f"configuration file not found: {config_path}") from exc
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise source_error("HED-DOCS-0003", f"invalid configuration: {exc}", config_path) from exc
    if not isinstance(raw_value, dict):
        raise source_error("HED-DOCS-0003", "configuration must be a TOML table", config_path)
    raw = cast(dict[str, object], raw_value)
    allowed = {"site", "build"}
    unknown = set(raw) - allowed
    if unknown:
        raise source_error(
            "HED-DOCS-0004", f"unknown configuration sections: {sorted(unknown)}", config_path
        )
    site = _mapping(raw.get("site", {}), config_path)
    build = _mapping(raw.get("build", {}), config_path)
    allowed_site = {
        "title",
        "description",
        "base_url",
        "docs_dir",
        "exclude",
        "allow_external_links",
    }
    allowed_build = {
        "output",
        "max_source_bytes",
        "max_asset_bytes",
        "max_nodes",
        "max_query_length",
    }
    unknown_site = set(site) - allowed_site
    unknown_build = set(build) - allowed_build
    if unknown_site or unknown_build:
        raise source_error(
            "HED-DOCS-0005",
            f"unknown configuration keys: {sorted(unknown_site | unknown_build)}",
            config_path,
        )
    exclude_value = site.get("exclude", [])
    if not isinstance(exclude_value, list):
        raise source_error("HED-DOCS-0006", "site.exclude must be an array of strings", config_path)
    exclude = cast(list[object], exclude_value)
    if not all(isinstance(item, str) for item in exclude):
        raise source_error("HED-DOCS-0006", "site.exclude must be an array of strings", config_path)
    exclude_strings = [item for item in exclude if isinstance(item, str)]
    try:
        return DocsBuildConfig(
            docs_dir=Path(_as_str(site.get("docs_dir", "docs"), "docs_dir")),
            output=Path(_as_str(build.get("output", "build/hedron-docs/site.json"), "output")),
            site_title=_as_str(site.get("title", "Documentation"), "title"),
            site_description=_as_str(site.get("description", ""), "description"),
            base_url=_as_str(site.get("base_url", ""), "base_url"),
            exclude=tuple(exclude_strings),
            allow_external_links=_as_bool(site.get("allow_external_links", True)),
            max_source_bytes=_as_int(build.get("max_source_bytes", 2_000_000)),
            max_asset_bytes=_as_int(build.get("max_asset_bytes", 10_000_000)),
            max_nodes=_as_int(build.get("max_nodes", 10_000)),
            max_query_length=_as_int(build.get("max_query_length", 200)),
            config_path=config_path,
        )
    except ValueError as exc:
        raise source_error(
            "HED-DOCS-0005", f"invalid configuration value: {exc}", config_path
        ) from exc


def import_mkdocs(path: str | Path) -> DocsBuildConfig:
    """Import safe site metadata and exclusion facts from a MkDocs YAML file.

    Plugin objects, hooks, theme configuration, and arbitrary YAML constructors are ignored.
    """

    config_path = Path(path).resolve()
    try:
        import yaml

        class _SafeMigrationLoader(yaml.SafeLoader):
            pass

        def _ignore_unknown(loader: Any, tag_suffix: str, node: Any) -> Any:
            if isinstance(node, yaml.ScalarNode):
                return loader.construct_scalar(node)
            if isinstance(node, yaml.SequenceNode):
                return loader.construct_sequence(node)
            return loader.construct_mapping(node)

        _SafeMigrationLoader.add_multi_constructor(  # pyright: ignore[reportUnknownMemberType]
            "!", _ignore_unknown
        )
        _SafeMigrationLoader.add_multi_constructor(  # pyright: ignore[reportUnknownMemberType]
            "tag:yaml.org,2002:python/", _ignore_unknown
        )
        raw_value: object = cast(
            object,
            yaml.load(config_path.read_text(encoding="utf-8"), Loader=_SafeMigrationLoader) or {},
        )
    except FileNotFoundError as exc:
        raise source_error(
            "HED-DOCS-0010", f"MkDocs configuration not found: {config_path}"
        ) from exc
    except Exception as exc:
        raise source_error(
            "HED-DOCS-0011", f"invalid MkDocs configuration: {exc}", config_path
        ) from exc
    if not isinstance(raw_value, dict):
        raise source_error("HED-DOCS-0012", "MkDocs configuration must be a mapping", config_path)
    data = cast(dict[str, object], raw_value)
    docs_dir_value = data.get("docs_dir", "docs")
    if not isinstance(docs_dir_value, str):
        raise source_error("HED-DOCS-0012", "MkDocs docs_dir must be a string", config_path)
    docs_dir = Path(docs_dir_value)
    exclude_value = data.get("exclude_docs")
    if exclude_value is None:
        excludes = ()
    elif isinstance(exclude_value, str):
        excludes = tuple(item for item in exclude_value.splitlines() if item.strip())
    elif isinstance(exclude_value, list):
        exclude_items = cast(list[object], exclude_value)
        if not all(isinstance(item, str) for item in exclude_items):
            raise source_error(
                "HED-DOCS-0012",
                "MkDocs exclude_docs must be a string or array of strings",
                config_path,
            )
        string_items = cast(list[str], exclude_items)
        excludes = tuple(item for item in string_items if item.strip())
    else:
        raise source_error(
            "HED-DOCS-0012", "MkDocs exclude_docs must be a string or array of strings", config_path
        )
    try:
        return DocsBuildConfig(
            docs_dir=docs_dir,
            site_title=str(data.get("site_name", "Documentation")),
            site_description=str(data.get("site_description", "")),
            base_url=str(data.get("site_url", "")) if isinstance(data.get("site_url"), str) else "",
            exclude=excludes,
            config_path=config_path,
        )
    except ValueError as exc:
        raise source_error(
            "HED-DOCS-0012", f"invalid MkDocs site metadata: {exc}", config_path
        ) from exc


def _mapping(value: object, source: Path) -> dict[str, object]:
    if not isinstance(value, dict):
        raise source_error("HED-DOCS-0007", "configuration section must be a table", source)
    return cast(dict[str, object], value)


def _as_int(value: object) -> int:
    if isinstance(value, bool):
        raise ValueError("configuration integer value is invalid")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and re.fullmatch(r"[+-]?\d+", value.strip()):
        return int(value)
    raise ValueError("configuration integer value is invalid")


def _as_bool(value: object) -> bool:
    if not isinstance(value, bool):
        raise ValueError("configuration boolean value is invalid")
    return value


def _as_str(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"configuration {name} value must be a string")
    return value
