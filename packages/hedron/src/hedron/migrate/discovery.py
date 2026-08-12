"""Static discovery of Streamlit entrypoints and multipage files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DiscoveredSource:
    entrypoint: Path
    project_root: Path
    files: tuple[Path, ...]


def resolve_project_root(source: Path, explicit: Path | None = None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    start = source.resolve()
    if start.is_file():
        start = start.parent
    for parent in (start, *start.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    return source.resolve().parent if source.is_file() else source.resolve()


def discover_sources(
    source: Path,
    *,
    project_root: Path | None = None,
    max_files: int = 200,
) -> DiscoveredSource:
    source = source.resolve()
    if not source.exists():
        raise FileNotFoundError(f"SOURCE not found: {source}")

    root = resolve_project_root(source, project_root)

    if source.is_file():
        if source.suffix != ".py":
            raise ValueError(f"SOURCE must be a Python file or directory: {source}")
        entrypoint = source
        files = [entrypoint]
        pages_dir = entrypoint.parent / "pages"
        if pages_dir.is_dir():
            files.extend(sorted(p for p in pages_dir.rglob("*.py") if p.is_file()))
    else:
        candidates = [
            source / "streamlit_app.py",
            source / "app.py",
            source / "Home.py",
            source / "home.py",
        ]
        entrypoint = next((c for c in candidates if c.is_file()), None)
        if entrypoint is None:
            py_files = sorted(source.glob("*.py"))
            if not py_files:
                raise FileNotFoundError(f"No Python entrypoint under {source}")
            entrypoint = py_files[0]
        files = [entrypoint]
        pages_dir = source / "pages"
        if pages_dir.is_dir():
            files.extend(sorted(p for p in pages_dir.rglob("*.py") if p.is_file()))

    # Containment: keep paths under project root; refuse escaping symlinks.
    contained: list[Path] = []
    for path in files:
        resolved = path.resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError as exc:
            raise ValueError(f"refusing path outside project root: {resolved}") from exc
        if path.is_symlink():
            link_target = path.resolve()
            try:
                link_target.relative_to(root.resolve())
            except ValueError as exc:
                raise ValueError(f"refusing symlink escape: {path}") from exc
        contained.append(resolved)

    # Deduplicate while preserving order
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in contained:
        if path in seen:
            continue
        seen.add(path)
        unique.append(path)

    if len(unique) > max_files:
        raise ValueError(f"file limit exceeded: {len(unique)} > {max_files}")

    return DiscoveredSource(
        entrypoint=entrypoint.resolve(),
        project_root=root.resolve(),
        files=tuple(unique),
    )
