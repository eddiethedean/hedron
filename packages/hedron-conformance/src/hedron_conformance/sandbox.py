"""Security / sandbox helpers for untrusted conformance suites (SANDBOX-052)."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

# Process kill / hard timeout default (seconds).
PROCESS_KILL_TIMEOUT_S = 30.0

# Archive bomb defaults (bytes / member counts).
DEFAULT_MAX_ARCHIVE_BYTES = 50_000_000
DEFAULT_MAX_ARCHIVE_MEMBERS = 10_000
DEFAULT_MAX_EXPANDED_BYTES = 200_000_000

NO_NETWORK_MARKER = "HEDRON_CONFORMANCE_NO_NETWORK"

_SECRET_ENV_RE = re.compile(
    r"(secret|password|passwd|token|api[_-]?key|access[_-]?key|private[_-]?key|"
    r"credential|auth[_-]?token|session[_-]?key)",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class SandboxPolicy:
    """Conservative defaults for evaluating untrusted suites offline."""

    max_archive_bytes: int = DEFAULT_MAX_ARCHIVE_BYTES
    max_archive_members: int = DEFAULT_MAX_ARCHIVE_MEMBERS
    max_expanded_bytes: int = DEFAULT_MAX_EXPANDED_BYTES
    process_kill_timeout_s: float = PROCESS_KILL_TIMEOUT_S
    allow_network: bool = False
    no_network_marker: str = NO_NETWORK_MARKER
    refuse_secret_env: bool = True

    def env_for_subprocess(self, base: Mapping[str, str] | None = None) -> dict[str, str]:
        """Build an env mapping safe for a sandboxed evaluator process."""
        out: dict[str, str] = dict(base or {})
        if not self.allow_network:
            out[self.no_network_marker] = "1"
        if self.refuse_secret_env:
            for name in list(out):
                if looks_like_secret_env(name):
                    raise ValueError(
                        f"refusing to capture secret-looking env var {name!r} into sandbox"
                    )
        return out


class SuitePathError(ValueError):
    """Raised when a suite path escapes the allowed root."""


def validate_suite_path(path: Path | str, *, root: Path | str) -> Path:
    """Resolve ``path`` under ``root``; reject traversal and absolute escapes."""
    root_path = Path(root).resolve()
    candidate = Path(path)
    # Reject obvious traversal tokens before resolve (defense in depth).
    posix = PurePosixPath(candidate.as_posix())
    if ".." in posix.parts:
        raise SuitePathError(f"path traversal rejected: {path!s}")
    resolved = candidate.resolve() if candidate.is_absolute() else (root_path / candidate).resolve()
    try:
        resolved.relative_to(root_path)
    except ValueError as exc:
        raise SuitePathError(f"suite path {path!s} escapes root {root_path}") from exc
    return resolved


def looks_like_secret_env(name: str) -> bool:
    """Return True when an env var name looks like a secret credential."""
    return bool(_SECRET_ENV_RE.search(name))


def refuse_secret_env_capture(env: Mapping[str, str]) -> list[str]:
    """Return secret-looking keys that must not be captured into reports."""
    return sorted(name for name in env if looks_like_secret_env(name))


__all__ = [
    "DEFAULT_MAX_ARCHIVE_BYTES",
    "DEFAULT_MAX_ARCHIVE_MEMBERS",
    "DEFAULT_MAX_EXPANDED_BYTES",
    "NO_NETWORK_MARKER",
    "PROCESS_KILL_TIMEOUT_S",
    "SandboxPolicy",
    "SuitePathError",
    "looks_like_secret_env",
    "refuse_secret_env_capture",
    "validate_suite_path",
]
