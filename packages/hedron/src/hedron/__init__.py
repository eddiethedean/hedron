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
from hedron.responses import (
    HTML,
    ComponentResponse,
    FileComponentResponse,
    FragmentResponse,
    PageResponse,
    hedron_response,
    merge_htmx_headers,
)
from hedron.routing import ComponentRef, HedronRoute, HedronRouter, resolve_route_path
from hedron.security import (
    SecurityPolicy,
    SecurityProfile,
    csrf_token_for_request,
    redirect_external,
    redirect_local,
)
from hedron.state import SessionState, session_state

# Re-export beginner core API.
from hedron_core import (  # noqa: F401
    ActionDock,
    Alert,
    Aside,
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
    DateInput,
    DateTimeInput,
    DescriptionList,
    Dialog,
    DirectoryUpload,
    Divider,
    Expander,
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
    IconButton,
    IFrame,
    Image,
    Inline,
    JSONViewer,
    Label,
    Link,
    LinkButton,
    List,
    Logo,
    Main,
    Map,
    Math,
    MenuButton,
    Metric,
    MicrophoneCapture,
    Model,
    MultiSelect,
    Nav,
    NumberInput,
    Page,
    PageIcon,
    PdfViewer,
    Pills,
    Popover,
    Progress,
    Props,
    RadioGroup,
    RangeInput,
    RatingInput,
    RenderContext,
    RenderMode,
    RenderResult,
    SafeUrl,
    Secret,
    Section,
    SegmentedControl,
    Select,
    SelectSlider,
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
        import hedron.experimental as _experimental

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
                'Install with: pip install "hedron[charts]" or pip install hedron-charts'
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


__version__ = "0.15.0"

# Stable + beta public facade. Live transports live in ``hedron.experimental``
# (compat attribute access retained via ``__getattr__``). Optional data/charts/auth
# extras remain lazy and are not part of the stable tier.
__all__ = [
    "ActionDock",
    "Alert",
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
    "FormErrors",
    "FormField",
    "FormModel",
    "Fragment",
    "FragmentRegion",
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
    "SecurityProfile",
    "SegmentedControl",
    "Select",
    "SelectSlider",
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
