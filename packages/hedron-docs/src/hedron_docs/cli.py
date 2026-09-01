"""Command line entry points for hedron-docs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .app import create_docs_app
from .config import import_mkdocs, load_config
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
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "[site]",
        f"title = {_toml_string(config.site_title)}",
        f"description = {_toml_string(config.site_description)}",
        f"docs_dir = {_toml_string(str(config.docs_dir))}",
        f"base_url = {_toml_string(config.base_url)}",
        "exclude = [" + ", ".join(_toml_string(item) for item in config.exclude) + "]",
        f"allow_external_links = {str(config.allow_external_links).lower()}",
        "",
        "[build]",
        f"output = {_toml_string(str(config.output))}",
        f"max_source_bytes = {config.max_source_bytes}",
        f"max_nodes = {config.max_nodes}",
        f"max_query_length = {config.max_query_length}",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _toml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


if __name__ == "__main__":
    raise SystemExit(main())
