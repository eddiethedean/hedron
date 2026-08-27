#!/usr/bin/env python3
"""Generate deterministic Hedron 1.0 W0 inventory artifacts.

The generator intentionally reads an immutable baseline (a git tag or an
already materialized directory).  It does not import package code, execute
decorators, or infer maturity from a moving checkout.  The resulting files are
inventory inputs for human reconciliation; they do not mark a release gate
Verified by themselves.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TAG = "v0.67.0"

COORDINATED = {
    "hedron-core",
    "hedron",
    "hedron-explorer",
    "hedron-data",
    "hedron-flask",
    "hedron-django",
    "hedron-jinja",
    "hedron-conformance",
    "hedron-extras",
    "hedron-workbench",
    "hedron-posit",
    "hedron-elements",
}

PACKAGE_IMPORTS = {
    "hedron-core": "hedron_core",
    "hedron": "hedron",
    "hedron-explorer": "hedron_explorer",
    "hedron-data": "hedron_data",
    "hedron-flask": "hedron_flask",
    "hedron-django": "hedron_django",
    "hedron-jinja": "hedron_jinja",
    "hedron-conformance": "hedron_conformance",
    "hedron-extras": "hedron_extras",
    "hedron-workbench": "hedron_workbench",
    "hedron-posit": "hedron_posit",
    "hedron-elements": "hedron_elements",
    "hedron-charts": "hedron_charts",
    "hedron-maps": "hedron_maps",
    "hedron-native": "hedron_native",
    "hedron-mcp": "hedron_mcp",
    "hedron-gradio": "hedron_gradio",
    "hedron-sample-kit": "hedron_sample_kit",
    "hedron-notebook": "hedron_notebook",
    "hedron-sim": "hedron_sim",
    "fastapi-workbench": "fastapi_workbench",
    "edron": "edron",
}

SKIP_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "build",
        "site",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    }
)
ARTIFACT_SUFFIXES = frozenset(
    {
        ".md",
        ".rst",
        ".toml",
        ".yaml",
        ".yml",
        ".json",
        ".hdj",
        ".html",
        ".htm",
        ".jinja",
        ".jinja2",
        ".py",
        ".mjs",
        ".js",
        ".css",
    }
)


def _read_all(path: Path) -> tuple[str, ...]:
    """Read a literal ``__all__`` without importing the module."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return ()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets
        ):
            continue
        if not isinstance(node.value, (ast.List, ast.Tuple)):
            return ()
        names = [
            item.value
            for item in node.value.elts
            if isinstance(item, ast.Constant) and isinstance(item.value, str)
        ]
        return tuple(names)
    return ()


def _version(path: Path) -> str:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return "unknown"
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "__version__"
                for target in node.targets
            )
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            return node.value.value
    return "unknown"


def _package_init(root: Path, distribution: str) -> Path | None:
    import_name = PACKAGE_IMPORTS.get(distribution)
    if import_name is None:
        return None
    path = root / "packages" / distribution / "src" / import_name / "__init__.py"
    return path if path.is_file() else None


def _tracked_artifacts(root: Path) -> tuple[Path, ...]:
    paths: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.suffix.lower() in ARTIFACT_SUFFIXES:
            paths.append(path.relative_to(root))
    return tuple(paths)


def _git_baseline(tag: str) -> tuple[Path, str, tempfile.TemporaryDirectory[str]]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-list", "-1", tag], cwd=ROOT, text=True, stderr=subprocess.STDOUT
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(f"immutable baseline tag is unavailable: {tag}") from exc
    temp = tempfile.TemporaryDirectory(prefix="hedron-100-baseline-")
    target = Path(temp.name)
    try:
        archive = subprocess.Popen(
            ["git", "archive", tag], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        assert archive.stdout is not None
        extract = subprocess.run(
            ["tar", "-x", "-f", "-", "-C", str(target)], stdin=archive.stdout, check=False
        )
        archive.stdout.close()
        stderr = archive.stderr.read().decode("utf-8", errors="replace") if archive.stderr else ""
        returncode = archive.wait()
        if returncode or extract.returncode:
            temp.cleanup()
            raise RuntimeError(f"could not materialize baseline {tag}: {stderr.strip()}")
    except Exception:
        temp.cleanup()
        raise
    return target, commit, temp


def _toml_string(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def _package_disposition(distribution: str) -> str:
    return "coordinated-cut" if distribution in COORDINATED else "independent-satellite"


def _write_public_inventory(
    path: Path, *, baseline: str, commit: str, root: Path
) -> dict[str, int]:
    packages: list[tuple[str, str, str, tuple[str, ...]]] = []
    for distribution in sorted(PACKAGE_IMPORTS):
        init = _package_init(root, distribution)
        if init is None:
            continue
        packages.append(
            (distribution, PACKAGE_IMPORTS[distribution], _version(init), _read_all(init))
        )
    artifacts = _tracked_artifacts(root)
    lines = [
        "schema_version = 1",
        'phase = "1.0"',
        'status = "Generated; W0 reconciliation pending"',
        f"baseline = {_toml_string(baseline)}",
        f"baseline_commit = {_toml_string(commit)}",
        'source_rule = "Generated from an immutable baseline; dispositions require review."',
        "",
    ]
    for distribution, import_name, version, exports in packages:
        lines.extend(
            [
                "[[package]]",
                f"name = {_toml_string(distribution)}",
                f"import = {_toml_string(import_name)}",
                f"version = {_toml_string(version)}",
                f"disposition = {_toml_string(_package_disposition(distribution))}",
                "",
            ]
        )
        for name in exports:
            lines.extend(
                [
                    "[[surface]]",
                    f"task = {_toml_string('export:' + import_name + '.' + name)}",
                    f"canonical = {_toml_string(import_name + '.' + name)}",
                    f"owner = {_toml_string(distribution)}",
                    'disposition = "unclassified"',
                    'maturity = "unclassified"',
                    "",
                ]
            )
    for artifact in artifacts:
        lines.extend(
            [
                "[[artifact]]",
                f"path = {_toml_string(artifact.as_posix())}",
                f"kind = {_toml_string(artifact.suffix.lower().lstrip('.') or 'extensionless')}",
                'disposition = "unclassified"',
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "packages": len(packages),
        "symbols": sum(len(item[3]) for item in packages),
        "artifacts": len(artifacts),
    }


def _write_stable_inventory(
    path: Path, *, baseline: str, commit: str, root: Path
) -> dict[str, int]:
    packages: list[tuple[str, str, str, tuple[str, ...]]] = []
    for distribution in sorted(PACKAGE_IMPORTS):
        init = _package_init(root, distribution)
        if init is None:
            continue
        packages.append(
            (distribution, PACKAGE_IMPORTS[distribution], _version(init), _read_all(init))
        )
    lines = [
        "schema_version = 1",
        'phase = "1.0"',
        'status = "Generated; stability and task reconciliation pending W0"',
        f"baseline = {_toml_string(baseline)}",
        f"baseline_commit = {_toml_string(commit)}",
        'stable_rule = "Every export is enumerated; reviewed rows enter the '
        'SemVer stable promise."',
        "",
    ]
    for distribution, import_name, version, exports in packages:
        lines.extend(
            [
                "[[package]]",
                f"name = {_toml_string(distribution)}",
                f"import = {_toml_string(import_name)}",
                f"version = {_toml_string(version)}",
                f"disposition = {_toml_string(_package_disposition(distribution))}",
                "",
            ]
        )
        for name in exports:
            lines.extend(
                [
                    "[[symbol]]",
                    f"qualified = {_toml_string(import_name + '.' + name)}",
                    'maturity = "unclassified"',
                    'disposition = "needs-review"',
                    "",
                ]
            )
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"packages": len(packages), "symbols": sum(len(item[3]) for item in packages)}


def _write_baseline(
    path: Path, *, baseline: str, commit: str, root: Path, counts: dict[str, int]
) -> None:
    files = _tracked_artifacts(root)
    digest = hashlib.sha256()
    for relative in files:
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update((root / relative).read_bytes())
    payload = {
        "schema": "hedron.phase-1.0-baseline/1",
        "phase": "1.0",
        "status": "Generated; reconciliation and release evidence pending",
        "baseline": baseline,
        "baseline_commit": commit,
        "source_digest": digest.hexdigest(),
        "inventory_counts": counts,
        "generation": {
            "command": "python scripts/generate_100_inventory.py --baseline v0.67.0",
            "non_executing": True,
            "tracked_artifact_digest": "sha256(path + bytes, sorted)",
        },
        "target": "v1.0.0",
        "release_cut_satisfied": False,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def generate(
    *, baseline: str = DEFAULT_TAG, output_dir: Path = ROOT / "docs" / "acceptance"
) -> dict[str, object]:
    baseline_root, commit, temporary = _git_baseline(baseline)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        public_counts = _write_public_inventory(
            output_dir / "public-inventory-100.toml",
            baseline=baseline,
            commit=commit,
            root=baseline_root,
        )
        stable_counts = _write_stable_inventory(
            output_dir / "stable-inventory-100.toml",
            baseline=baseline,
            commit=commit,
            root=baseline_root,
        )
        counts = {"public": public_counts, "stable": stable_counts}
        _write_baseline(
            output_dir / "baseline-100.json",
            baseline=baseline,
            commit=commit,
            root=baseline_root,
            counts=counts,
        )
        return {"baseline": baseline, "commit": commit, "counts": counts}
    finally:
        temporary.cleanup()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline", default=DEFAULT_TAG, help="immutable git tag (default: v0.67.0)"
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs" / "acceptance")
    args = parser.parse_args()
    try:
        result = generate(baseline=args.baseline, output_dir=args.output_dir)
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
