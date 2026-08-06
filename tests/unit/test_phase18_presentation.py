"""Phase 0.18 PRESENT-018: PredictionLabel / ParameterViewer / Dialogue."""

from __future__ import annotations

from hedron_core import Dialogue, ParameterViewer, PredictionLabel, render
from hedron_core.rendering import RenderMode


def test_prediction_label_accessible_table() -> None:
    node = PredictionLabel(
        [
            {"class_id": "cat", "score": 0.9, "precision": 0.01, "calibrated": True},
            {"class_id": "dog", "score": 0.1, "calibrated": False},
        ],
        title="Scores",
        mark="pred",
    )
    result = render(node, mode=RenderMode.FRAGMENT)
    html = result.html
    assert "cat" in html and "dog" in html
    assert 'role="table"' in html or "<table" in html
    assert "data-hedron-mark" in html or "pred" in html


def test_parameter_viewer_redacts_secrets() -> None:
    node = ParameterViewer(
        {"lr": 0.01, "api_token": "sekrit"},
        secret_keys=("api_token",),
        mark="params",
    )
    html = render(node, mode=RenderMode.FRAGMENT).html
    assert "0.01" in html
    assert "[redacted]" in html
    assert "sekrit" not in html


def test_dialogue_speaker_labels_not_color_only() -> None:
    node = Dialogue(
        [
            {"speaker": "A", "text": "Hello", "start_ms": 0, "end_ms": 500, "tags": ("greeting",)},
            {"speaker": "B", "text": "Hi", "start_ms": 500, "end_ms": 900},
        ],
        mark="dlg",
    )
    html = render(node, mode=RenderMode.FRAGMENT).html
    assert "Speaker A" in html or "hedron-dialogue-speaker" in html
    assert "Hello" in html and "Hi" in html
    assert "aria-label" in html
