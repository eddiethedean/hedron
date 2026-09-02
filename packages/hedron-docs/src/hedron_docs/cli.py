"""Command line entry points for hedron-docs."""

from __future__ import annotations

import argparse
import os
import sys
from contextlib import suppress
from pathlib import Path

from .app import create_docs_app
from .config import CONFIG_SCHEMA_VERSION, NavigationItem, import_mkdocs, load_config
from .errors import DocsError
from .manifest import compile_site


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="hedron-docs", description="Compile Markdown into a Hedron site"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("check", "build", "serve"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("config", nargs="?", default="hedron-docs.toml")
    importer = subparsers.add_parser("import-mkdocs")
    importer.add_argument("mkdocs_config")
    importer.add_argument("-o", "--output", default="hedron-docs.toml")
    args = parser.parse_args(argv)
    try:
        if args.command == "import-mkdocs":
            config = import_mkdocs(args.mkdocs_config)
            _write_native_config(config, Path(args.output))
            print(f"wrote {args.output}")
            return 0
        config = load_config(args.config)
        manifest = compile_site(config)
        if args.command == "check":
            output = config.resolved(
                root=config.config_path.parent if config.config_path else None
            ).output
            if output.exists():
                existing = output.read_text(encoding="utf-8")
                if existing != manifest.dumps():
                    raise ValueError(f"generated manifest is stale: {output}")
            print(f"ok: compiled {len(manifest.pages)} page(s)")
            return 0
        output = manifest.write(
            config.resolved(root=config.config_path.parent if config.config_path else None).output
        )
        if args.command == "build":
            print(f"wrote {output}")
            return 0
        app = create_docs_app(manifest)
        import uvicorn

        uvicorn.run(app, host="127.0.0.1", port=8000)
        return 0
    except DocsError as exc:
        print(exc, file=sys.stderr)
        return 2
    except (OSError, ValueError) as exc:
        print(f"HED-DOCS-0001: {exc}", file=sys.stderr)
        return 2


def _write_native_config(config: object, path: Path) -> None:
    from .config import DocsBuildConfig

    if not isinstance(config, DocsBuildConfig):
        raise TypeError("expected DocsBuildConfig")
    target = path.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    docs_dir = config.docs_dir
    if not docs_dir.is_absolute() and config.config_path is not None:
        docs_dir = (config.config_path.parent / docs_dir).resolve()
    if docs_dir.is_absolute():
        with suppress(ValueError):
            docs_dir = Path(os.path.relpath(docs_dir, target.parent))
    lines = [
        f"schema_version = {CONFIG_SCHEMA_VERSION}",
        "",
        "[site]",
        f"title = {_toml_string(config.site_title)}",
        f"description = {_toml_string(config.site_description)}",
        f"docs_dir = {_toml_string(str(docs_dir))}",
        f"base_url = {_toml_string(config.base_url)}",
        "exclude = [" + ", ".join(_toml_string(item) for item in config.exclude) + "]",
        f"allow_external_links = {str(config.allow_external_links).lower()}",
        "navigation = " + _toml_navigation(config.navigation),
        "",
        "[build]",
        f"output = {_toml_string(str(config.output))}",
        f"max_source_bytes = {config.max_source_bytes}",
        f"max_asset_bytes = {config.max_asset_bytes}",
        f"max_nodes = {config.max_nodes}",
        f"max_depth = {config.max_depth}",
        f"max_table_cells = {config.max_table_cells}",
        f"max_code_blocks = {config.max_code_blocks}",
        f"max_code_block_bytes = {config.max_code_block_bytes}",
        f"max_directives = {config.max_directives}",
        f"max_query_length = {config.max_query_length}",
        "",
    ]
    target.write_text("\n".join(lines), encoding="utf-8")


def _toml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def _toml_navigation(items: tuple[NavigationItem, ...]) -> str:
    def item_text(item: NavigationItem) -> str:
        fields = [f"title = {_toml_string(item.title)}"]
        if item.path:
            fields.append(f"path = {_toml_string(item.path)}")
        else:
            fields.append(f"children = {_toml_navigation(item.children)}")
        return "{ " + ", ".join(fields) + " }"

    return "[" + ", ".join(item_text(item) for item in items) + "]"


if __name__ == "__main__":
    raise SystemExit(main())
