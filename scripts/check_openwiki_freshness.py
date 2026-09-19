#!/usr/bin/env python3
"""Verify that the committed OpenWiki pages cover the current source tree.

The source fingerprint intentionally mirrors OpenWiki 0.5.x's
``openwiki-source-fingerprint-v1`` contract. Keeping this check in the
repository means the local ``ci_checks.sh all`` gate can fail before expensive
tests when source changes need a local OpenWiki update. It never calls a
model, writes the wiki, or contacts a service.
"""

from __future__ import annotations

import hashlib
import json
import os
import posixpath
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OPENWIKI_DIR = ROOT / "openwiki"
MANIFEST_PATH = OPENWIKI_DIR / ".page-manifest.json"
LAST_UPDATE_PATH = OPENWIKI_DIR / ".last-update.json"
IGNORE_PATH = ROOT / ".openwikiignore"
SOURCE_FINGERPRINT_VERSION = "openwiki-source-fingerprint-v1"
OPENWIKI_RESERVED_FILES = {"index.md", "log.md", "instructions.md"}


def run_git(*args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "--no-pager", *args],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        detail = getattr(error, "stderr", b"")
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", "replace").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}") from error
    return result.stdout


def decode(value: bytes) -> str:
    return value.decode("utf-8", "surrogateescape")


def split_nul(value: bytes) -> list[bytes]:
    if not value:
        return []
    if not value.endswith(b"\0"):
        raise RuntimeError("git returned non-NUL-terminated output")
    return value[:-1].split(b"\0")


def repository_head() -> str:
    try:
        head = decode(run_git("rev-parse", "--verify", "HEAD")).strip()
        if head:
            return head
    except RuntimeError:
        pass
    symbolic_head = decode(run_git("symbolic-ref", "-q", "HEAD")).strip()
    if not symbolic_head:
        raise RuntimeError("unable to resolve the repository HEAD")
    return f"unborn:{symbolic_head}"


class IgnoreRule:
    def __init__(self, pattern: str) -> None:
        normalized = pattern.replace("\\", "/")
        self.negated = normalized.startswith("!")
        if self.negated:
            normalized = normalized[1:]
        normalized = re.sub(r"^\./+", "", normalized)
        normalized = re.sub(r"/+", "/", normalized)
        anchored = normalized.startswith("/")
        self.directory_only = normalized.endswith("/")
        normalized = re.sub(r"^/+", "", normalized)
        normalized = re.sub(r"/+$", "", normalized)
        if not normalized:
            self.matcher: re.Pattern[str] | None = None
            return
        source = self._glob_to_regex(normalized)
        if anchored or "/" in normalized:
            expression = rf"^{source}(?:/.*)?$"
        else:
            expression = rf"(^|/){source}(/.*)?$"
        self.matcher = re.compile(expression, re.IGNORECASE)

    @staticmethod
    def _glob_to_regex(pattern: str) -> str:
        source: list[str] = []
        index = 0
        while index < len(pattern):
            character = pattern[index]
            next_character = pattern[index + 1] if index + 1 < len(pattern) else ""
            if character == "*" and next_character == "*":
                after = pattern[index + 2] if index + 2 < len(pattern) else ""
                if after == "/":
                    source.append("(?:.*/)?")
                    index += 3
                else:
                    source.append(".*")
                    index += 2
                continue
            if character == "*":
                source.append("[^/]*")
            elif character == "?":
                source.append("[^/]")
            else:
                source.append(re.escape(character))
            index += 1
        return "".join(source)

    @staticmethod
    def normalize_path(value: str) -> str:
        slashed = value.replace("\\", "/")
        normalized = posixpath.normpath("/" + slashed.lstrip("/"))
        return normalized.strip("/")

    def matches(self, value: str, is_directory: bool) -> bool:
        if self.matcher is None:
            return False
        normalized = self.normalize_path(value)
        if not self.matcher.fullmatch(normalized):
            return False
        return not self.directory_only or is_directory or "/" in normalized


class OpenWikiIgnore:
    def __init__(self) -> None:
        if IGNORE_PATH.exists():
            lines = IGNORE_PATH.read_text(encoding="utf-8").splitlines()
        else:
            lines = []
        self.rules = [
            IgnoreRule(line.strip())
            for line in lines
            if line.strip() and not line.strip().startswith("#")
        ]

    def ignores(self, value: str) -> bool:
        ignored = False
        is_directory = False
        try:
            is_directory = stat.S_ISDIR((ROOT / Path(value)).lstat().st_mode)
        except FileNotFoundError:
            pass
        for rule in self.rules:
            if rule.matches(value, is_directory):
                ignored = not rule.negated
        return ignored


def is_openwiki_path(value: str) -> bool:
    return value == "openwiki" or value.startswith("openwiki/")


def is_source_path(value: str, ignore: OpenWikiIgnore) -> bool:
    if value == ".openwikiignore":
        return True
    if value == ".git" or value.startswith(".git/"):
        return False
    return not is_openwiki_path(value) and not ignore.ignores(value)


def update_field(digest: Any, label: str, value: bytes | str) -> None:
    encoded = value if isinstance(value, bytes) else value.encode("utf-8", "surrogateescape")
    digest.update(label.encode("utf-8"))
    digest.update(b"\0")
    digest.update(str(len(encoded)).encode("ascii"))
    digest.update(b"\0")
    digest.update(encoded)
    digest.update(b"\0")


def parse_status() -> list[tuple[str, str]]:
    entries = []
    output = run_git(
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--no-renames",
        "-z",
    )
    for record in split_nul(output):
        if len(record) < 4 or record[2:3] != b" ":
            raise RuntimeError("git returned malformed porcelain status output")
        entries.append((decode(record[:2]), decode(record[3:])))
    return entries


def tracked_paths_at(revision: str) -> set[str]:
    return {
        decode(value)
        for value in split_nul(run_git("ls-tree", "-r", "--name-only", "-z", revision))
    }


def source_fingerprint(
    ignore: OpenWikiIgnore,
    *,
    head: str | None = None,
    statuses: list[tuple[str, str]] | None = None,
    baseline: str | None = None,
) -> tuple[str, str]:
    resolved_head = repository_head() if head is None else head
    tracked = {
        decode(value)
        for value in split_nul(run_git("ls-files", "--cached", "-z"))
    }
    if baseline is not None:
        # A completed OpenWiki run normally observes a dirty worktree and is
        # then committed. Include paths that existed in that pre-commit tree so
        # deleted or renamed tracked files replay the same source snapshot.
        tracked.update(tracked_paths_at(baseline))
    candidates = tracked | {
        decode(value)
        for value in split_nul(run_git("ls-files", "--others", "--exclude-standard", "-z"))
    }
    if IGNORE_PATH.exists():
        candidates.add(".openwikiignore")

    visible = sorted(value for value in candidates if is_source_path(value, ignore))
    visible_statuses = sorted(
        (code, value)
        for code, value in (parse_status() if statuses is None else statuses)
        if is_source_path(value, ignore)
    )

    digest = hashlib.sha256()
    update_field(digest, "format", SOURCE_FINGERPRINT_VERSION)
    update_field(digest, "head", resolved_head)
    for code, value in visible_statuses:
        update_field(digest, "status-code", code)
        update_field(digest, "status-path", value)

    for source_path in visible:
        update_field(digest, "path", source_path)
        absolute_path = ROOT.joinpath(*source_path.split("/"))
        try:
            metadata = absolute_path.lstat()
        except FileNotFoundError:
            if source_path in tracked:
                update_field(digest, "kind", "tracked-missing")
                continue
            raise RuntimeError(f"source path disappeared while checking: {source_path}")

        if stat.S_ISREG(metadata.st_mode):
            update_field(digest, "executable", "yes" if metadata.st_mode & 0o111 else "no")
            update_field(digest, "kind", "file")
            update_field(digest, "bytes", absolute_path.read_bytes())
        elif stat.S_ISLNK(metadata.st_mode):
            update_field(digest, "executable", "yes" if metadata.st_mode & 0o111 else "no")
            update_field(digest, "kind", "symlink")
            update_field(digest, "target", os.fsencode(os.readlink(absolute_path)))
        elif stat.S_ISDIR(metadata.st_mode):
            update_field(digest, "executable", "yes" if metadata.st_mode & 0o111 else "no")
            update_field(digest, "kind", "directory")
        else:
            raise RuntimeError(f"unsupported source entry type: {source_path}")

    return f"sha256:{digest.hexdigest()}", resolved_head


def committed_snapshot_statuses(baseline: str, head: str) -> list[tuple[str, str]]:
    fields = split_nul(
        run_git("diff", "--name-status", "--no-renames", "-z", baseline, head, "--")
    )
    if len(fields) % 2:
        raise RuntimeError("git returned malformed NUL-delimited diff output")

    statuses: list[tuple[str, str]] = []
    for index in range(0, len(fields), 2):
        change = decode(fields[index])
        path = decode(fields[index + 1])
        kind = change[:1]
        if kind == "A":
            code = "??"
        elif kind == "D":
            code = " D"
        else:
            code = f" {kind}"
        statuses.append((code, path))
    return statuses


def post_commit_fingerprint(
    ignore: OpenWikiIgnore, baseline: str, head: str
) -> tuple[str, str] | None:
    if baseline == head or parse_status():
        return None
    try:
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", baseline, head],
            cwd=ROOT,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    statuses = committed_snapshot_statuses(baseline, head)
    return source_fingerprint(
        ignore,
        head=baseline,
        statuses=statuses,
        baseline=baseline,
    )


def page_path_from_key(key: str) -> Path:
    if not key.startswith("/openwiki/") or not key.endswith(".md"):
        raise ValueError(f"non-factual manifest page: {key}")
    relative = key.removeprefix("/openwiki/")
    parts = relative.split("/")
    if not relative or any(part in {".", "..", ".claims"} for part in parts):
        raise ValueError(f"reserved or unsafe manifest page: {key}")
    if parts[-1].lower() in OPENWIKI_RESERVED_FILES:
        raise ValueError(f"reserved or unsafe manifest page: {key}")
    return OPENWIKI_DIR / Path(*parts)


def factual_pages_on_disk() -> set[str]:
    pages = set()
    if not OPENWIKI_DIR.exists():
        return pages
    for path in OPENWIKI_DIR.rglob("*.md"):
        if not path.is_file() or ".claims" in path.parts:
            continue
        if path.name.lower() in OPENWIKI_RESERVED_FILES:
            continue
        relative = path.relative_to(OPENWIKI_DIR).as_posix()
        pages.add(f"/openwiki/{relative}")
    return pages


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"unable to read valid JSON from {path}: {error}") from error
    if not isinstance(value, dict):
        raise RuntimeError(f"expected an object in {path}")
    return value


def check_manifest(fingerprint: str, head: str) -> list[str]:
    errors: list[str] = []
    if not LAST_UPDATE_PATH.is_file():
        errors.append("openwiki/.last-update.json is missing")
    else:
        metadata = load_json(LAST_UPDATE_PATH)
        if metadata.get("status") != "complete":
            errors.append("OpenWiki last-update status is not complete")
        if metadata.get("gitHead") != head:
            errors.append("OpenWiki last-update checkpoint is not the current Git HEAD")

    if not MANIFEST_PATH.is_file():
        return [*errors, "openwiki/.page-manifest.json is missing"]

    manifest = load_json(MANIFEST_PATH)
    if manifest.get("schemaVersion") != 1:
        errors.append("OpenWiki page manifest schemaVersion must be 1")
    pages = manifest.get("pages")
    if not isinstance(pages, dict) or not pages:
        return [*errors, "OpenWiki page manifest has no factual pages"]

    manifest_pages = set(pages)
    disk_pages = factual_pages_on_disk()
    for page in sorted(disk_pages - manifest_pages):
        errors.append(f"factual page is not covered by the manifest: {page}")
    for page in sorted(manifest_pages - disk_pages):
        errors.append(f"manifest page is missing on disk: {page}")

    for page in sorted(manifest_pages):
        entry = pages[page]
        if not isinstance(entry, dict):
            errors.append(f"manifest entry is not an object: {page}")
            continue
        try:
            markdown_path = page_path_from_key(page)
        except ValueError as error:
            errors.append(str(error))
            continue
        if entry.get("sourceFingerprint") != fingerprint:
            errors.append(f"source fingerprint is stale for {page}")
        if entry.get("gitHead") != head:
            errors.append(f"Git HEAD checkpoint is stale for {page}")

        page_version = entry.get("pageVersion")
        if not markdown_path.is_file():
            continue
        actual_page_version = f"sha256:{hashlib.sha256(markdown_path.read_bytes()).hexdigest()}"
        if page_version != actual_page_version:
            errors.append(f"pageVersion does not match Markdown bytes for {page}")

        relative = markdown_path.relative_to(OPENWIKI_DIR).with_suffix(".json")
        claims_path = OPENWIKI_DIR / ".claims" / relative
        if not claims_path.is_file():
            errors.append(f"verified Claims sidecar is missing for {page}")
            continue
        try:
            claims = load_json(claims_path)
        except RuntimeError as error:
            errors.append(str(error))
            continue
        if claims.get("schemaVersion") != 1:
            errors.append(f"Claims schemaVersion must be 1 for {page}")
        if claims.get("pageVersion") != actual_page_version:
            errors.append(f"Claims pageVersion does not match Markdown bytes for {page}")
        if not claims.get("verification"):
            errors.append(f"Claims are not verified for {page}")
        if not isinstance(claims.get("claims"), list) or not claims["claims"]:
            errors.append(f"no grounded Claims are recorded for {page}")

    return errors


def main() -> int:
    try:
        ignore = OpenWikiIgnore()
        fingerprint, head = source_fingerprint(ignore)
        errors = check_manifest(fingerprint, head)
        if errors and not parse_status() and LAST_UPDATE_PATH.is_file():
            metadata = load_json(LAST_UPDATE_PATH)
            baseline = metadata.get("gitHead")
            if isinstance(baseline, str):
                replayed = post_commit_fingerprint(ignore, baseline, head)
                if replayed is not None:
                    replay_fingerprint, replay_head = replayed
                    replay_errors = check_manifest(replay_fingerprint, replay_head)
                    if not replay_errors:
                        errors = []
    except (RuntimeError, OSError, ValueError) as error:
        errors = [str(error)]

    if errors:
        print("OpenWiki is stale or incomplete:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        print(
            "Run a local OpenWiki update in Codex, then rerun "
            "scripts/ci_checks.sh all.",
            file=sys.stderr,
        )
        return 1

    print(f"ok: OpenWiki is current ({len(factual_pages_on_disk())} factual pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
