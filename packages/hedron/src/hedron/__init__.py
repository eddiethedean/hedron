"""hedron: FastAPI-native typed component framework."""

from __future__ import annotations

from typing import TYPE_CHECKING

from hedron.app import Hedron, mount_hedron_static
from hedron.async_utils import await_if_needed, gather, run_sync
from hedron.browser import browser_context, browser_context_from_request
from hedron.builtins import (
    AutoForm,
    ErrorState,
    InfiniteScroll,
    Lazy,
    Loading,
    LoginCsrfField,
    Pagination,
    Poll,
    RefreshButton,
    action_attrs,
    oob_swap,
)
from hedron.builtins.chat import ChatInput
from hedron.builtins.files import DownloadButton, FileUpload, safe_download_response
from hedron.builtins.media import (
    ByteRangeNotSatisfiable,
    download_all_zip,
    media_file_response,
    parse_byte_range,
)
from hedron.cache import cache_component, cache_data
from hedron.color_mode import (
    apply_color_mode_cookie,
    read_color_mode_preference,
    resolved_theme_from_request,
)
from hedron.htmx import approved_headers, htmx_context
from hedron.interaction import (
    FragmentRegion,
    FragmentRegionError,
    HtmxRequest,
    InteractionPolicy,
    InteractionResult,
    OobUpdate,
    default_interaction_policy,
    form_sync_attrs,
    htmx_request,
    redirect_htmx,
    retarget,
    swap,
    swap_oob,
)
from hedron.mount import (
    MountPath,
    cookie_path_for_mount,
    mount_from_request,
    normalize_mount_path,
    prefix_local_path,
    resolve_mount_path,
    resolve_mount_path_from_environ,
)
from hedron.recorder import (
    InteractionRecorder,
    RecordedExchange,
    RecordingSnippet,
)
from hedron.responses import (
    HTML,
    ComponentResponse,
    FileComponentResponse,
    FragmentResponse,
    PageResponse,
    hedron_response,
    merge_htmx_headers,
    render_component_response,
    render_interaction,
)
from hedron.routing import ComponentRef, HedronRoute, HedronRouter, resolve_route_path
from hedron.security import (
    SecurityHeadersPolicy,
    SecurityPolicy,
    SecurityProfile,
    csrf_token_for_request,
    redirect_external,
    redirect_local,
)
from hedron.state import SessionState, session_state

# Re-export beginner core API.
from hedron_core import (
    ActionDock,
    ActionRegistry,
    Alert,
    AppShell,
    Aside,
    AttrHost,
    Audio,
    Auto,
    Badge,
    BottomDock,
    BrowserContext,
    BrowserStorage,
    BrowserStorageUnavailable,
    Button,
    CameraCapture,
    Card,
    Carousel,
    ChatMessage,
    Checkbox,
    ChipInput,
    CircularProgress,
    ClipboardCopy,
    CodeBlock,
    CodeViewer,
    ColorInput,
    ColorMode,
    ColorModeToggle,
    Component,
    ConfirmButton,
    Container,
    ContextMenu,
    CsrfField,
    CsrfStrategy,
    CsrfValidationError,
    DateInput,
    DateTimeInput,
    DescriptionList,
    Dialog,
    Dialogue,
    DialogueTurn,
    DirectoryUpload,
    Divider,
    DoubleSubmitCookieCsrf,
    ExampleItem,
    ExampleSet,
    Expander,
    FeedbackPolicy,
    Field,
    Footer,
    Form,
    FormErrors,
    FormField,
    FormModel,
    Fragment,
    Gallery,
    GeoJSONLayer,
    GeolocationButton,
    GeolocationHint,
    Grid,
    Head,
    Header,
    Heading,
    Help,
    HelpInspector,
    HtmxLink,
    Hx,
    IconButton,
    IFrame,
    Image,
    InferenceInterface,
    InferencePolicy,
    InferenceWorkflow,
    Inline,
    JSONViewer,
    Label,
    Link,
    LinkButton,
    List,
    Logo,
    Main,
    MainPanel,
    Map,
    Math,
    MenuButton,
    Metric,
    MicrophoneCapture,
    Model,
    ModelDemo,
    MultiSelect,
    Nav,
    NavLink,
    NumberInput,
    OobHost,
    Page,
    PageIcon,
    ParameterViewer,
    PdfViewer,
    Pills,
    Popover,
    PredictionFeedback,
    PredictionLabel,
    PredictionScore,
    Progress,
    Props,
    RadioGroup,
    RangeInput,
    RatingInput,
    RegisteredAction,
    RenderContext,
    RenderMode,
    RenderResult,
    SafeUrl,
    Secret,
    Section,
    SegmentedControl,
    Select,
    SelectSlider,
    SessionTokenCsrf,
    Sidebar,
    Skeleton,
    Spacer,
    Stack,
    Status,
    StorageQuotaExceeded,
    StyleSymbols,
    SubmitButton,
    Table,
    Tabs,
    Text,
    TextArea,
    TextInput,
    Theme,
    TimeInput,
    Timeline,
    Title,
    Toast,
    ToggleSwitch,
    Tooltip,
    TrustedHtml,
    UrlPurpose,
    Video,
    ViewportHint,
    addressable,
    compile_css,
    get_icon,
    html,
    invalidate_tags,
    list_icons,
    redact_cookie_value,
    register_icon,
    render,
    resolve_color_mode,
    styles_from_manifest,
    trusted_svg,
)
from hedron_core.builtins.forms_extra import DirectoryUploadFile, validate_directory_upload
from hedron_core.builtins.map_geo import MarkerSpec
from hedron_core.builtins.media import GalleryItem

if TYPE_CHECKING:
    from hedron.auth import OAuthHelper as OAuthHelper
    from hedron.auth import create_oauth_client as create_oauth_client
    from hedron.content import Markdown as Markdown
    from hedron.content import highlight_code as highlight_code
    from hedron.content import process_image as process_image
    from hedron.content import validate_email_address as validate_email_address
    from hedron_charts import AltairChart as AltairChart
    from hedron_charts import AreaChart as AreaChart
    from hedron_charts import BarChart as BarChart
    from hedron_charts import LineChart as LineChart
    from hedron_charts import MatplotlibChart as MatplotlibChart
    from hedron_charts import PlotlyChart as PlotlyChart
    from hedron_charts import ScatterChart as ScatterChart

_DATA_EXPORTS = frozenset(
    {
        "DataChanges",
        "DataEditor",
        "DataPage",
        "DataQuery",
        "DataSaveResult",
        "DataTable",
        "InMemoryDataSource",
    }
)
_CHART_EXPORTS = frozenset(
    {
        "AltairChart",
        "AreaChart",
        "BarChart",
        "LineChart",
        "MatplotlibChart",
        "PlotlyChart",
        "ScatterChart",
    }
)
_EXPERIMENTAL_EXPORTS = frozenset(
    {
        "ALLOW_MISSING_ORIGIN",
        "HX_PRELOADED",
        "NavigationPreloadPolicy",
        "SseResponse",
        "StreamingComponentResponse",
        "accept_page_session_channel",
        "apply_preload_headers",
        "evaluate_preload_request",
        "extension_script_tags",
        "job_status_sse_response",
        "origin_allowed",
        "send_region_update",
        "sse_response",
        "stream_chunked_list",
        "stream_document",
        "stream_tokens",
    }
)


def __getattr__(name: str) -> object:
    if name in _EXPERIMENTAL_EXPORTS:
        import warnings

        import hedron.experimental as _experimental

        warnings.warn(
            f"hedron.{name} is experimental; import from hedron.experimental "
            "(polling remains the Supported production fallback).",
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(_experimental, name)
    if name in _DATA_EXPORTS:
        try:
            import hedron_data as _hedron_data
        except ImportError as exc:  # pragma: no cover - exercised when extra missing
            raise ImportError(
                f"{name} requires the hedron-data package. "
                'Install with: pip install "hedron[data]" or pip install hedron-data'
            ) from exc
        return getattr(_hedron_data, name)
    if name in _CHART_EXPORTS:
        try:
            import hedron_charts as _hedron_charts
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                f"{name} requires the hedron-charts package. "
                'Install with: pip install "hedron[charts]>=0.29.0,<0.30" or '
                'pip install "hedron-charts>=0.1.10,<0.2". '
                "See https://hedron.readthedocs.io/en/latest/COMPATIBILITY/"
            ) from exc
        return getattr(_hedron_charts, name)
    if name == "Markdown":
        from hedron.content import Markdown

        return Markdown
    if name in {"validate_email_address", "highlight_code", "process_image"}:
        import hedron.content as _content

        return getattr(_content, name)
    if name in {"OAuthHelper", "create_oauth_client"}:
        import hedron.auth as _auth

        return getattr(_auth, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__version__ = "0.42.0"

# Stable + beta public facade. Live transports live in ``hedron.experimental``
# (compat attribute access retained via ``__getattr__``). Optional data/charts/auth
# extras remain lazy and are not part of the stable tier.
__all__ = [
    "ActionDock",
    "Alert",
    "RegisteredAction",
    "PredictionScore",
    "PredictionLabel",
    "PredictionFeedback",
    "ParameterViewer",
    "ModelDemo",
    "InferenceWorkflow",
    "InferencePolicy",
    "InferenceInterface",
    "FeedbackPolicy",
    "ExampleSet",
    "ExampleItem",
    "DialogueTurn",
    "Dialogue",
    "ActionRegistry",
    "Aside",
    "Audio",
    "Auto",
    "AutoForm",
    "Badge",
    "BottomDock",
    "BrowserContext",
    "BrowserStorage",
    "BrowserStorageUnavailable",
    "Button",
    "ByteRangeNotSatisfiable",
    "CameraCapture",
    "Card",
    "Carousel",
    "ChatInput",
    "ChatMessage",
    "Checkbox",
    "ChipInput",
    "CircularProgress",
    "ClipboardCopy",
    "CodeBlock",
    "CodeViewer",
    "ColorInput",
    "ColorMode",
    "ColorModeToggle",
    "Component",
    "ComponentRef",
    "ComponentResponse",
    "ConfirmButton",
    "Container",
    "ContextMenu",
    "DateInput",
    "DateTimeInput",
    "DescriptionList",
    "Dialog",
    "DirectoryUpload",
    "DirectoryUploadFile",
    "Divider",
    "DownloadButton",
    "ErrorState",
    "Expander",
    "Field",
    "FileComponentResponse",
    "FileUpload",
    "Footer",
    "Form",
    "CsrfField",
    "LoginCsrfField",
    "Hx",
    "FormErrors",
    "FormField",
    "FormModel",
    "Fragment",
    "FragmentRegion",
    "FragmentRegionError",
    "FragmentResponse",
    "Gallery",
    "GalleryItem",
    "GeoJSONLayer",
    "GeolocationButton",
    "GeolocationHint",
    "Grid",
    "HTML",
    "Head",
    "Header",
    "Heading",
    "Hedron",
    "HedronRoute",
    "HedronRouter",
    "Help",
    "HelpInspector",
    "HtmxRequest",
    "IconButton",
    "IFrame",
    "Image",
    "InfiniteScroll",
    "Inline",
    "InteractionPolicy",
    "InteractionResult",
    "JSONViewer",
    "Label",
    "Lazy",
    "Link",
    "HtmxLink",
    "NavLink",
    "OobHost",
    "AttrHost",
    "AppShell",
    "MainPanel",
    "LinkButton",
    "List",
    "Loading",
    "Logo",
    "Main",
    "Map",
    "MarkerSpec",
    "Math",
    "MenuButton",
    "Metric",
    "MicrophoneCapture",
    "Model",
    "MultiSelect",
    "Nav",
    "NumberInput",
    "OobUpdate",
    "Page",
    "PageIcon",
    "PageResponse",
    "Pagination",
    "PdfViewer",
    "Pills",
    "Poll",
    "Popover",
    "Progress",
    "Props",
    "RadioGroup",
    "RangeInput",
    "RatingInput",
    "RefreshButton",
    "RenderContext",
    "RenderMode",
    "RenderResult",
    "SafeUrl",
    "Secret",
    "Section",
    "SecurityPolicy",
    "SecurityHeadersPolicy",
    "SecurityProfile",
    "SegmentedControl",
    "Select",
    "SelectSlider",
    "MountPath",
    "cookie_path_for_mount",
    "mount_from_request",
    "normalize_mount_path",
    "prefix_local_path",
    "resolve_mount_path",
    "resolve_mount_path_from_environ",
    "SessionState",
    "Sidebar",
    "Skeleton",
    "Spacer",
    "Stack",
    "Status",
    "StorageQuotaExceeded",
    "StyleSymbols",
    "SubmitButton",
    "Table",
    "Tabs",
    "Text",
    "TextArea",
    "TextInput",
    "Theme",
    "TimeInput",
    "Timeline",
    "Title",
    "Toast",
    "ToggleSwitch",
    "Tooltip",
    "TrustedHtml",
    "UrlPurpose",
    "Video",
    "ViewportHint",
    "__version__",
    "action_attrs",
    "addressable",
    "apply_color_mode_cookie",
    "approved_headers",
    "await_if_needed",
    "browser_context",
    "browser_context_from_request",
    "cache_component",
    "cache_data",
    "compile_css",
    "CsrfStrategy",
    "CsrfValidationError",
    "DoubleSubmitCookieCsrf",
    "SessionTokenCsrf",
    "csrf_token_for_request",
    "default_interaction_policy",
    "download_all_zip",
    "form_sync_attrs",
    "gather",
    "get_icon",
    "hedron_response",
    "html",
    "htmx_context",
    "htmx_request",
    "invalidate_tags",
    "list_icons",
    "media_file_response",
    "merge_htmx_headers",
    "mount_hedron_static",
    "oob_swap",
    "parse_byte_range",
    "read_color_mode_preference",
    "redact_cookie_value",
    "redirect_external",
    "redirect_htmx",
    "redirect_local",
    "register_icon",
    "render",
    "render_component_response",
    "render_interaction",
    "InteractionRecorder",
    "RecordedExchange",
    "RecordingSnippet",
    "resolve_color_mode",
    "resolve_route_path",
    "resolved_theme_from_request",
    "retarget",
    "run_sync",
    "safe_download_response",
    "session_state",
    "styles_from_manifest",
    "swap",
    "swap_oob",
    "trusted_svg",
    "validate_directory_upload",
]
