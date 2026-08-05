from hedron_data.collab import EditProvenance, merge_changes, recover_pending
from hedron_data.sources import CellUpdate, DataChanges


def test_collab_merge_and_recover() -> None:
    local = DataChanges(
        updates=(CellUpdate(row_key="1", field="v", value=1),), dataset_version="v1"
    )
    remote = DataChanges(
        updates=(CellUpdate(row_key="1", field="v", value=2),), dataset_version="v1"
    )
    result = merge_changes("v1", local, remote, local_actor="a", remote_actor="b")
    assert result.ok is False
    assert result.conflicts
    pending = recover_pending(local, "v2")
    assert pending.dataset_version == "v2"
    assert EditProvenance.now(actor_id="a", client_id="c").actor_id == "a"
