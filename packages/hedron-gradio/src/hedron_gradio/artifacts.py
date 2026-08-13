"""Bounded in-process artifact storage with retention cleanup."""

from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass, field

from hedron_gradio.errors import GradioRemoteError

__all__ = ["ArtifactStore", "ArtifactRecord"]

_ARTIFACT_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_UNSAFE_NAME = re.compile(r"[\\/]|(?:\.\.)")


@dataclass
class ArtifactRecord:
    name: str
    data: bytes
    created_at: float = field(default_factory=time.monotonic)


class ArtifactStore:
    """Bounded artifact store with TTL eviction."""

    def __init__(
        self,
        *,
        max_bytes: int,
        retention_seconds: float,
        allowed_extensions: frozenset[str] | None = None,
    ) -> None:
        if max_bytes <= 0:
            raise ValueError("max_bytes must be > 0")
        if retention_seconds <= 0:
            raise ValueError("retention_seconds must be > 0")
        self._max_bytes = max_bytes
        self._retention_seconds = retention_seconds
        self._allowed_extensions = allowed_extensions or frozenset(
            {".txt", ".json", ".png", ".jpg", ".jpeg", ".webp", ".csv", ".wav", ".mp3"}
        )
        self._records: dict[str, ArtifactRecord] = {}
        self._total_bytes = 0

    def _validate_name(self, name: str) -> None:
        if not name or _UNSAFE_NAME.search(name):
            raise GradioRemoteError(f"Unsafe artifact name: {name!r}")
        if "." in name:
            ext = "." + name.rsplit(".", 1)[-1].lower()
            if ext not in self._allowed_extensions:
                raise GradioRemoteError(f"Disallowed artifact extension: {ext!r}")

    def _evict_expired(self) -> None:
        now = time.monotonic()
        expired = [
            artifact_id
            for artifact_id, record in self._records.items()
            if now - record.created_at > self._retention_seconds
        ]
        for artifact_id in expired:
            self._delete_unlocked(artifact_id)

    def _delete_unlocked(self, artifact_id: str) -> None:
        record = self._records.pop(artifact_id, None)
        if record is not None:
            self._total_bytes -= len(record.data)

    def store(self, name: str, data: bytes) -> str:
        self._evict_expired()
        self._validate_name(name)
        if len(data) > self._max_bytes:
            raise GradioRemoteError(
                f"Artifact exceeds max size ({len(data)} > {self._max_bytes})"
            )
        artifact_id = f"{name}:{uuid.uuid4().hex}"
        if not _ARTIFACT_ID.match(artifact_id):
            raise GradioRemoteError("Generated artifact id failed validation")
        projected = self._total_bytes + len(data)
        if projected > self._max_bytes:
            raise GradioRemoteError("Artifact store capacity exceeded")
        self._records[artifact_id] = ArtifactRecord(name=name, data=data)
        self._total_bytes = projected
        return artifact_id

    def fetch(self, artifact_id: str) -> bytes:
        self._evict_expired()
        if not _ARTIFACT_ID.match(artifact_id):
            raise GradioRemoteError(f"Invalid artifact id: {artifact_id!r}")
        record = self._records.get(artifact_id)
        if record is None:
            raise GradioRemoteError(f"Unknown artifact id: {artifact_id}")
        return record.data

    def delete(self, artifact_id: str) -> bool:
        if artifact_id not in self._records:
            return False
        self._delete_unlocked(artifact_id)
        return True

    def clear(self) -> None:
        self._records.clear()
        self._total_bytes = 0

    @property
    def total_bytes(self) -> int:
        self._evict_expired()
        return self._total_bytes
