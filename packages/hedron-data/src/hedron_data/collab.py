"""Collaborative editing provenance, merge, and recovery helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime

from hedron_core.typing_aliases import JsonValue
from hedron_data.sources import CellUpdate, Conflict, DataChanges, DataSaveResult, FieldError

__all__ = [
    "CollaborativeConflict",
    "EditProvenance",
    "merge_changes",
    "recover_pending",
]


@dataclass(frozen=True, slots=True)
class EditProvenance:
    actor_id: str
    client_id: str
    timestamp_iso: str

    @classmethod
    def now(cls, *, actor_id: str, client_id: str) -> EditProvenance:
        return cls(
            actor_id=actor_id,
            client_id=client_id,
            timestamp_iso=datetime.now(UTC).isoformat(),
        )


@dataclass(frozen=True, slots=True)
class CollaborativeConflict(Conflict):
    local_actor: str | None = None
    remote_actor: str | None = None


def merge_changes(
    base_version: str | None,
    local: DataChanges[Mapping[str, JsonValue]],
    remote: DataChanges[Mapping[str, JsonValue]],
    *,
    local_actor: str | None = None,
    remote_actor: str | None = None,
) -> DataSaveResult[Mapping[str, JsonValue]]:
    """Merge two change sets; same-cell edits become collaborative conflicts."""
    if local.dataset_version not in (None, base_version) or remote.dataset_version not in (
        None,
        base_version,
    ):
        return DataSaveResult(
            ok=False,
            errors=(
                FieldError(
                    row_key=None,
                    field=None,
                    message="Change set dataset_version does not match base_version",
                ),
            ),
            version=base_version,
        )
    remote_keys = {(u.row_key, u.field): u for u in remote.updates}
    accepted: list[CellUpdate] = []
    conflicts: list[CollaborativeConflict] = []
    consumed_remote: set[tuple[object, object]] = set()

    def _insert_key(row: Mapping[str, JsonValue]) -> str:
        if "id" in row:
            return str(row["id"])
        return str(next(iter(row.values()), ""))

    local_inserts = {_insert_key(row) for row in local.inserts if isinstance(row, Mapping)}
    remote_inserts = {_insert_key(row) for row in remote.inserts if isinstance(row, Mapping)}
    local_deletes = set(local.deletes)
    remote_deletes = set(remote.deletes)
    overlap = (
        (local_inserts & remote_inserts)
        | (local_inserts & remote_deletes)
        | (remote_inserts & local_deletes)
    )
    for key in sorted(overlap):
        if not key:
            continue
        conflicts.append(
            CollaborativeConflict(
                row_key=key,
                field=None,
                server_value=None,
                client_value=None,
                message="Concurrent insert/delete",
                local_actor=local_actor,
                remote_actor=remote_actor,
            )
        )
    if conflicts:
        return DataSaveResult(ok=False, conflicts=tuple(conflicts), version=base_version)
    for update in local.updates:
        key = (update.row_key, update.field)
        other = remote_keys.get(key)
        if other is not None and other.value != update.value:
            conflicts.append(
                CollaborativeConflict(
                    row_key=update.row_key,
                    field=update.field,
                    server_value=other.value,
                    client_value=update.value,
                    message="Concurrent cell edit",
                    local_actor=local_actor,
                    remote_actor=remote_actor,
                )
            )
        else:
            accepted.append(update)
            if other is not None:
                consumed_remote.add(key)
    if conflicts:
        return DataSaveResult(ok=False, conflicts=tuple(conflicts), version=base_version)
    remote_only = tuple(u for u in remote.updates if (u.row_key, u.field) not in consumed_remote)
    merged = DataChanges(
        updates=tuple(accepted) + remote_only,
        inserts=tuple(local.inserts) + tuple(remote.inserts),
        deletes=tuple(dict.fromkeys([*local.deletes, *remote.deletes])),
        dataset_version=base_version,
    )
    return DataSaveResult(ok=True, accepted=merged, version=base_version)


def recover_pending(
    pending: DataChanges[Mapping[str, JsonValue]],
    server_version: str | None,
) -> DataChanges[Mapping[str, JsonValue]]:
    """Rebase pending client edits onto the latest server version."""
    return DataChanges(
        updates=pending.updates,
        inserts=pending.inserts,
        deletes=pending.deletes,
        dataset_version=server_version,
    )
