from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Confirm:
    message: str
    confirm_label: str = "Confirm"
    cancel_label: str = "Cancel"
