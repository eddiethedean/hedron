"""Compatibility ``HedronWorkbench`` subclass of ``HedronPosit``."""

from __future__ import annotations

from typing import Any

from hedron_posit import HedronPosit
from hedron_posit.config import WorkbenchConfig, WorkbenchMode, WorkbenchTopology


class HedronWorkbench(HedronPosit):
    """Thin compatibility subclass of ``HedronPosit``.

    Preserves the ``HedronWorkbench`` type name, ``__hedron_workbench__`` marker,
    and public 0.32 constructor keywords. Prefer ``HedronPosit`` for new apps.
    """

    __hedron_workbench__ = True
    __hedron_posit__ = True

    def __init__(
        self,
        *args: Any,
        workbench: WorkbenchConfig | None = None,
        workbench_mode: WorkbenchMode | str | None = None,
        workbench_mount: str | None = None,
        workbench_public_base_url: str | None = None,
        workbench_debug: bool | None = None,
        workbench_topology: WorkbenchTopology | str | None = None,
        external_base_url: str | None = None,
        root_path: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            *args,
            workbench=workbench,
            workbench_mode=workbench_mode,
            workbench_mount=workbench_mount,
            workbench_public_base_url=workbench_public_base_url,
            workbench_debug=workbench_debug,
            workbench_topology=workbench_topology,
            external_base_url=external_base_url,
            root_path=root_path,
            **kwargs,
        )
