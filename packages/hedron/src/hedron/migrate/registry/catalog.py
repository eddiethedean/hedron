"""Versioned Streamlit → Hedron mapping catalog (Streamlit 1.60.x audit)."""

from __future__ import annotations

from dataclasses import dataclass

from hedron.migrate.ir import Confidence, Disposition

CATALOG_VERSION = "1.60.0-hedron-0.31"
STREAMLIT_AUDIT_BASELINE = "1.60.x"


@dataclass(frozen=True, slots=True)
class MappingRule:
    symbol: str
    disposition: Disposition
    confidence: Confidence
    hedron_hint: str
    finding_code: str | None = None
    note: str = ""


def _t(symbol: str, hint: str, confidence: Confidence = Confidence.EXACT) -> MappingRule:
    return MappingRule(symbol, Disposition.TRANSLATED, confidence, hint)


def _s(
    symbol: str,
    hint: str,
    *,
    confidence: Confidence = Confidence.BOUNDED,
    code: str = "HED-MIG-ST-0013",
    note: str = "",
) -> MappingRule:
    return MappingRule(symbol, Disposition.SCAFFOLDED, confidence, hint, code, note)


def _r(
    symbol: str,
    hint: str,
    *,
    code: str = "HED-MIG-ST-0014",
    confidence: Confidence = Confidence.AMBIGUOUS,
    note: str = "",
) -> MappingRule:
    return MappingRule(symbol, Disposition.REPORT_ONLY, confidence, hint, code, note)


def _u(
    symbol: str,
    hint: str,
    *,
    code: str = "HED-MIG-ST-0002",
    note: str = "",
) -> MappingRule:
    return MappingRule(symbol, Disposition.UNSUPPORTED, Confidence.EXACT, hint, code, note)


# Phase 0.31 Supported-ish subset from streamlit-migration-matrix.md / RFC-0061 §4.
_RULES: tuple[MappingRule, ...] = (
    # Text / layout / navigation
    _t("st.title", "Heading(level=1)"),
    _t("st.header", "Heading(level=2)"),
    _t("st.subheader", "Heading(level=3)"),
    _s("st.write", "Auto/Text/Markdown", note="magic/write is not a side-effect API"),
    _t("st.markdown", "Markdown"),
    _t("st.code", "CodeBlock"),
    _t("st.json", "JSONViewer"),
    _t("st.sidebar", "Sidebar", Confidence.BOUNDED),
    _t("st.columns", "Grid", Confidence.BOUNDED),
    _t("st.container", "Container", Confidence.BOUNDED),
    _t("st.tabs", "Tabs", Confidence.BOUNDED),
    _t("st.expander", "Expander"),
    _t("st.popover", "Popover"),
    _r("st.empty", "declared region + fragment"),
    _s("st.Page", "@app.page route"),
    _s("st.navigation", "navigation components"),
    _s("st.page_link", "Link"),
    _s("st.switch_page", "redirect response"),
    _s("st.set_page_config", "Hedron(...)/Page(title=...)"),
    # Inputs / forms
    _s("st.button", "SubmitButton + @app.action", code="HED-MIG-ST-0005"),
    _t("st.form", "Form"),
    _t("st.form_submit_button", "SubmitButton"),
    _t("st.text_input", "TextInput"),
    _t("st.text_area", "TextArea"),
    _t("st.number_input", "NumberInput"),
    _t("st.slider", "RangeInput / html.input(type=range)"),
    _t("st.select_slider", "SelectSlider"),
    _t("st.selectbox", "Select"),
    _t("st.multiselect", "MultiSelect"),
    _t("st.checkbox", "Checkbox"),
    _t("st.toggle", "ToggleSwitch"),
    _t("st.radio", "RadioGroup"),
    _t("st.segmented_control", "SegmentedControl"),
    _t("st.pills", "Pills"),
    _t("st.date_input", "DateInput"),
    _t("st.time_input", "TimeInput"),
    _t("st.color_picker", "ColorInput"),
    _t("st.feedback", "RatingInput"),
    _s("st.file_uploader", "FileUpload", code="HED-MIG-ST-0007"),
    _r("st.camera_input", "CameraCapture", code="HED-MIG-ST-0007"),
    _r("st.audio_input", "MicrophoneCapture", code="HED-MIG-ST-0007"),
    # Data / charts / media
    _t("st.metric", "Metric"),
    _s("st.dataframe", "DataTable / Table", note="requires hedron[data] when typed"),
    _s("st.table", "Table"),
    _r("st.data_editor", "DataEditor", code="HED-MIG-ST-0014"),
    _r("st.column_config", "column configuration", code="HED-MIG-ST-0014"),
    _s(
        "st.line_chart",
        "MatplotlibChart / Table fallback",
        note="conservative static chart path",
        code="HED-MIG-ST-0013",
    ),
    _s("st.area_chart", "MatplotlibChart / Table fallback"),
    _s("st.bar_chart", "MatplotlibChart / Table fallback"),
    _s("st.scatter_chart", "MatplotlibChart / Table fallback"),
    _s("st.pyplot", "MatplotlibChart", confidence=Confidence.BOUNDED),
    _s("st.plotly_chart", "PlotlyChart (experimental)", confidence=Confidence.AMBIGUOUS),
    _s("st.altair_chart", "AltairChart (experimental)", confidence=Confidence.AMBIGUOUS),
    _r("st.map", "Map + accessible alternative", code="HED-MIG-ST-0009"),
    _r("st.pydeck_chart", "Map layers", code="HED-MIG-ST-0009"),
    _t("st.image", "Image"),
    _t("st.audio", "Audio"),
    _t("st.video", "Video"),
    _s("st.download_button", "DownloadButton", code="HED-MIG-ST-0007"),
    _r("st.graphviz_chart", "diagram adapter", code="HED-MIG-ST-0010"),
    # Status / chat
    _t("st.success", "Alert(success)"),
    _t("st.info", "Alert(info)"),
    _t("st.warning", "Alert(warning)"),
    _t("st.error", "Alert(error)"),
    _s("st.spinner", "Loading"),
    _s("st.status", "Status"),
    _s("st.progress", "Progress + Poll"),
    _t("st.toast", "Toast / swap(toast=...)"),
    _r("st.chat_message", "ChatMessage", code="HED-MIG-ST-0014"),
    _r("st.chat_input", "ChatInput", code="HED-MIG-ST-0014"),
    _r("st.write_stream", "polling job output", code="HED-MIG-ST-0014"),
    _u("st.balloons", "no decorative parity", note="No parity"),
    _u("st.snow", "no decorative parity", note="No parity"),
    # Execution / state / cache
    _s("st.fragment", "app.region / @app.fragment"),
    _s("st.dialog", "Dialog + fragment/action"),
    _u("st.rerun", "no rerun loop", code="HED-MIG-ST-0004"),
    _u("st.stop", "early return / HTTP exception", code="HED-MIG-ST-0004"),
    _r("st.session_state", "classify ownership", code="HED-MIG-ST-0003"),
    _t("st.query_params", "typed Query parameters"),
    _s("st.cache_data", "cache_data", code="HED-MIG-ST-0006"),
    _s("st.cache_resource", "lifespan DI", code="HED-MIG-ST-0006"),
    _r("st.connection", "host DI", code="HED-MIG-ST-0010"),
    _r("st.secrets", "environment / secret manager", code="HED-MIG-ST-0007"),
    _s("st.context", "Request + browser context"),
    _r("st.login", "OIDC/session helpers", code="HED-MIG-ST-0008"),
    _r("st.logout", "OIDC/session helpers", code="HED-MIG-ST-0008"),
    _r("st.user", "app-owned authz", code="HED-MIG-ST-0008"),
    _s("st.experimental_rerun", "no rerun loop", code="HED-MIG-ST-0004"),
    _s("st.experimental_fragment", "app.region / fragment"),
)


def all_rules() -> dict[str, MappingRule]:
    return {rule.symbol: rule for rule in _RULES}


def lookup(symbol: str) -> MappingRule | None:
    return all_rules().get(symbol)


def supported_symbols() -> frozenset[str]:
    return frozenset(all_rules())
