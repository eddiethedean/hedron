"""Fingerprinted asset pipeline."""

from __future__ import annotations

import mimetypes
import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from hedron_core.codes import (
    HED_ASSET_COLLISION,
    HED_ASSET_MISSING,
    HED_ASSET_REMOTE,
    HED_ASSET_SYMLINK,
    HED_ASSET_TRAVERSAL,
)
from hedron_core.diagnostics import error
from hedron_core.identifiers import asset_filename_stem, content_digest
from hedron_core.manifests import ASSET_MANIFEST_FORMAT, AssetEntry, AssetManifest

__all__ = [
    "AssetBuildResult",
    "build_asset_manifest",
    "fingerprint_file",
    "resolve_under_roots",
]


@dataclass(frozen=True, slots=True)
class AssetBuildResult:
    manifest: AssetManifest
    output_dir: Path


def resolve_under_roots(
    path: Path,
    *,
    roots: Sequence[Path],
    allow_symlink: bool = False,
) -> Path:
    resolved = path.resolve()
    if (resolved.is_symlink() or path.is_symlink()) and not allow_symlink:
        raise error(
            HED_ASSET_SYMLINK,
            title="Symlinked asset rejected",
            explanation=f"Asset {path} is a symlink.",
            remediation="Use a real file under a registered root.",
        )
    if not any(resolved == root.resolve() or root.resolve() in resolved.parents for root in roots):
        raise error(
            HED_ASSET_TRAVERSAL,
            title="Asset path traversal rejected",
            explanation=f"Asset {path} is outside registered roots.",
            remediation="Register the directory or move the asset.",
        )
    if not resolved.is_file():
        raise error(
            HED_ASSET_MISSING,
            title="Asset missing",
            explanation=f"Asset file {path} was not found.",
            remediation="Add the file or fix the reference.",
        )
    return resolved


def fingerprint_file(
    source: Path,
    *,
    output_dir: Path,
    logical_id: str,
    kind: str,
    prefix: str | None = None,
    attributes: Mapping[str, str] | None = None,
) -> AssetEntry:
    try:
        data = source.read_bytes()
    except FileNotFoundError as exc:
        raise error(
            HED_ASSET_MISSING,
            title="Asset missing",
            explanation=f"Asset file {source} was not found.",
            remediation="Add the file or fix the reference.",
        ) from exc
    digest = content_digest(data)
    stem = asset_filename_stem(digest)
    suffix = source.suffix or ""
    name_prefix = prefix or source.stem
    filename = f"{name_prefix}.{stem}{suffix}"
    # Collision lengthening
    dest = output_dir / filename
    length = 20
    while dest.exists() and content_digest(dest.read_bytes()) != digest:
        length += 4
        if length > 64:
            raise error(
                HED_ASSET_COLLISION,
                title="Asset fingerprint collision",
                explanation=f"Could not resolve filename collision for {logical_id}.",
                remediation="Change asset content or logical id.",
            )
        filename = f"{name_prefix}.{digest[:length]}{suffix}"
        dest = output_dir / filename
    output_dir.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copy2(source, dest)
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    return AssetEntry(
        logical_id=logical_id,
        kind=kind,
        path=filename,
        digest=digest,
        content_type=content_type,
        attributes=dict(attributes or {}),
    )


def fingerprint_bytes(
    data: bytes,
    *,
    output_dir: Path,
    logical_id: str,
    kind: str,
    filename_prefix: str,
    suffix: str,
    content_type: str,
    attributes: Mapping[str, str] | None = None,
) -> AssetEntry:
    digest = content_digest(data)
    stem = asset_filename_stem(digest)
    filename = f"{filename_prefix}.{stem}{suffix}"
    dest = output_dir / filename
    output_dir.mkdir(parents=True, exist_ok=True)
    if dest.exists() and content_digest(dest.read_bytes()) != digest:
        filename = f"{filename_prefix}.{digest[:24]}{suffix}"
        dest = output_dir / filename
    if not dest.exists():
        dest.write_bytes(data)
    return AssetEntry(
        logical_id=logical_id,
        kind=kind,
        path=filename,
        digest=digest,
        content_type=content_type,
        attributes=dict(attributes or {}),
    )


def build_asset_manifest(entries: Sequence[AssetEntry]) -> AssetManifest:
    # Reject remote hrefs sneaked into entries
    for entry in entries:
        if entry.path.startswith(("http://", "https://", "//")):
            raise error(
                HED_ASSET_REMOTE,
                title="Remote asset rejected",
                explanation=f"Asset {entry.logical_id} points at a remote URL.",
                remediation="Vendor the asset locally and fingerprint it.",
            )
    return AssetManifest(format_version=ASSET_MANIFEST_FORMAT, assets=tuple(entries))
