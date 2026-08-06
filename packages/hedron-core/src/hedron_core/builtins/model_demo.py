"""Model-demo presentation built-ins (RFC-0046 / PRESENT-018)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from hedron_core.builtins._base import class_names, mark_data
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.typing_aliases import HtmlAttrValue

__all__ = [
    "Dialogue",
    "DialogueTurn",
    "ParameterViewer",
    "PredictionLabel",
    "PredictionScore",
]


class PredictionScore(Props):
    class_id: str
    score: float
    precision: float | None = None
    calibrated: bool = False


class PredictionLabelProps(Props):
    scores: tuple[PredictionScore, ...]
    title: str = "Predictions"
    threshold: float | None = None
    class_: str | None = None
    mark: str | None = None


class PredictionLabel(Component[PredictionLabelProps]):
    """Ranked prediction labels with class identity and accessible table encoding."""

    props_type = PredictionLabelProps
    logical_name = "PredictionLabel"
    distribution = "hedron-core"

    def __init__(
        self,
        scores: Sequence[PredictionScore | Mapping[str, Any]],
        *,
        title: str = "Predictions",
        threshold: float | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        resolved: list[PredictionScore] = []
        for item in scores:
            if isinstance(item, PredictionScore):
                resolved.append(item)
            else:
                resolved.append(
                    PredictionScore(
                        class_id=str(item["class_id"]),
                        score=float(item["score"]),
                        precision=(
                            float(item["precision"]) if item.get("precision") is not None else None
                        ),
                        calibrated=bool(item.get("calibrated", False)),
                    )
                )
        super().__init__(
            PredictionLabelProps(
                scores=tuple(resolved),
                title=title,
                threshold=threshold,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        rows: list[NodeLike] = [
            html.tr(
                html.th("Class"),
                html.th("Score"),
                html.th("Precision"),
                html.th("Calibrated"),
            )
        ]
        for score in self.props.scores:
            rows.append(
                html.tr(
                    html.td(score.class_id),
                    html.td(f"{score.score:.4f}"),
                    html.td("—" if score.precision is None else f"{score.precision:.4f}"),
                    html.td("yes" if score.calibrated else "no"),
                    data={"class-id": score.class_id},
                )
            )
        attrs: dict[str, HtmlAttrValue] = {
            "class_": class_names("hedron-prediction-label", self.props.class_),
            "role": "table",
            "aria": {"label": self.props.title},
        }
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        caption = html.caption(self.props.title)
        if self.props.threshold is not None:
            caption = html.caption(f"{self.props.title} (threshold={self.props.threshold})")
        return html.table(caption, html.thead(rows[0]), html.tbody(*rows[1:]), **attrs)


class ParameterEntry(Props):
    key: str
    display: str


class ParameterViewerProps(Props):
    entries: tuple[ParameterEntry, ...]
    title: str = "Parameters"
    class_: str | None = None
    mark: str | None = None


class ParameterViewer(Component[ParameterViewerProps]):
    """Schema-driven parameter documentation with secret redaction."""

    props_type = ParameterViewerProps
    logical_name = "ParameterViewer"
    distribution = "hedron-core"

    def __init__(
        self,
        parameters: Mapping[str, Any],
        *,
        title: str = "Parameters",
        secret_keys: Sequence[str] = (),
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        secrets = set(secret_keys)
        entries = tuple(
            ParameterEntry(
                key=str(key),
                display="[redacted]" if str(key) in secrets else repr(value),
            )
            for key, value in parameters.items()
        )
        super().__init__(
            ParameterViewerProps(
                entries=entries,
                title=title,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        items: list[NodeLike] = [
            html.div(
                html.dt(entry.key),
                html.dd(entry.display),
                class_="hedron-parameter",
                data={"param": entry.key},
            )
            for entry in self.props.entries
        ]
        attrs: dict[str, HtmlAttrValue] = {
            "class_": class_names("hedron-parameter-viewer", self.props.class_),
            "aria": {"label": self.props.title},
        }
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.section(html.h3(self.props.title), html.dl(*items), **attrs)


class DialogueTurn(Props):
    speaker: str
    text: str
    start_ms: int | None = None
    end_ms: int | None = None
    tags: tuple[str, ...] = ()


class DialogueProps(Props):
    turns: tuple[DialogueTurn, ...]
    title: str = "Dialogue"
    class_: str | None = None
    mark: str | None = None


class Dialogue(Component[DialogueProps]):
    """Multi-speaker transcript with accessible speaker labels (not color-only)."""

    props_type = DialogueProps
    logical_name = "Dialogue"
    distribution = "hedron-core"

    def __init__(
        self,
        turns: Sequence[DialogueTurn | Mapping[str, Any]],
        *,
        title: str = "Dialogue",
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        resolved: list[DialogueTurn] = []
        for turn in turns:
            if isinstance(turn, DialogueTurn):
                resolved.append(turn)
            else:
                resolved.append(
                    DialogueTurn(
                        speaker=str(turn["speaker"]),
                        text=str(turn["text"]),
                        start_ms=turn.get("start_ms"),
                        end_ms=turn.get("end_ms"),
                        tags=tuple(turn.get("tags") or ()),
                    )
                )
        super().__init__(
            DialogueProps(
                turns=tuple(resolved),
                title=title,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        articles: list[NodeLike] = []
        for turn in self.props.turns:
            timing = ""
            if turn.start_ms is not None or turn.end_ms is not None:
                timing = f" [{turn.start_ms or 0}–{turn.end_ms or 0} ms]"
            tag_text = f" ({', '.join(turn.tags)})" if turn.tags else ""
            articles.append(
                html.article(
                    html.header(
                        html.strong(turn.speaker, class_="hedron-dialogue-speaker"),
                        html.span(timing + tag_text, class_="hedron-dialogue-meta"),
                    ),
                    html.p(turn.text),
                    data={"speaker": turn.speaker},
                    aria={"label": f"Speaker {turn.speaker}"},
                )
            )
        attrs: dict[str, HtmlAttrValue] = {
            "class_": class_names("hedron-dialogue", self.props.class_),
            "aria": {"label": self.props.title},
        }
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.section(html.h3(self.props.title), *articles, **attrs)
