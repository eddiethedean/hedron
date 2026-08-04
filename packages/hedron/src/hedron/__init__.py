"""hedron: FastAPI-native typed component framework."""

from __future__ import annotations

from typing import TYPE_CHECKING

from hedron.app import Hedron, mount_hedron_static
from hedron.async_utils import await_if_needed, gather, run_sync
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
)
from hedron.preload import (
    HX_PRELOADED,
    NavigationPreloadPolicy,
    apply_preload_headers,
    evaluate_preload_request,
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
from hedron.sse import SseResponse, extension_script_tags, job_status_sse_response, sse_response
from hedron.state import SessionState, session_state
from hedron.streaming import (
    StreamingComponentResponse,
    stream_chunked_list,
    stream_document,
    stream_tokens,
)
from hedron.websocket_channel import (
    ALLOW_MISSING_ORIGIN,
    accept_page_session_channel,
    origin_allowed,
    send_region_update,
)

# Re-export beginner core API.
from hedron_core import (  # noqa: F401
    Alert,
    Aside,
    Auto,
    Badge,
    Button,
    Card,
    ChatMessage,
    Checkbox,
    CodeBlock,
    CodeViewer,
    ColorMode,
    ColorModeToggle,
    Component,
    Container,
    DescriptionList,
    Dialog,
    Divider,
    Expander,
    Field,
    Footer,
    Form,
    FormErrors,
    FormField,
    FormModel,
    Fragment,
    Grid,
    Head,
    Header,
    Heading,
    IconButton,
    Image,
    Inline,
    JSONViewer,
    Label,
    Link,
    LinkButton,
    List,
    Main,
    Metric,
    Model,
    Nav,
    Page,
    Progress,
    Props,
    RadioGroup,
    RenderContext,
    RenderMode,
    RenderResult,
    SafeUrl,
    Secret,
    Section,
    Select,
    Sidebar,
    Skeleton,
    Stack,
    Status,
    StyleSymbols,
    SubmitButton,
    Table,
    Tabs,
    Text,
    TextArea,
    TextInput,
    Theme,
    Title,
    Toast,
    TrustedHtml,
    UrlPurpose,
    addressable,
    compile_css,
    get_icon,
    html,
    invalidate_tags,
    list_icons,
    register_icon,
    render,
    resolve_color_mode,
    styles_from_manifest,
    trusted_svg,
)

if TYPE_CHECKING:
    from hedron.auth import OAuthHelper as OAuthHelper
    from hedron.auth import create_oauth_client as create_oauth_client
    from hedron.content import Markdown as Markdown
    from hedron.content import highlight_code as highlight_code
    from hedron.content import process_image as process_image
    from hedron.content import validate_email_address as validate_email_address
    from hedron_charts import AltairChart as AltairChart
    from hedron_charts import LineChart as LineChart
    from hedron_charts import MatplotlibChart as MatplotlibChart
    from hedron_charts import PlotlyChart as PlotlyChart
    from hedron_data import (
        DataChanges,
        DataEditor,
        DataPage,
        DataQuery,
        DataSaveResult,
        DataTable,
        InMemoryDataSource,
    )

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
        "LineChart",
        "MatplotlibChart",
        "PlotlyChart",
    }
)


def __getattr__(name: str) -> object:
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


__version__ = "0.10.1"

__all__ = [
    "Alert",
    "Aside",
    "AutoForm",
    "Badge",
    "Button",
    "Card",
    "ChatInput",
    "ChatMessage",
    "Checkbox",
    "CodeBlock",
    "Component",
    "ComponentRef",
    "ComponentResponse",
    "Container",
    "DescriptionList",
    "Dialog",
    "Divider",
    "ErrorState",
    "Field",
    "FileComponentResponse",
    "Footer",
    "Form",
    "FormErrors",
    "FormField",
    "FormModel",
    "Fragment",
    "FragmentResponse",
    "Grid",
    "HTML",
    "HX_PRELOADED",
    "Head",
    "Header",
    "Heading",
    "Hedron",
    "HedronRoute",
    "HedronRouter",
    "IconButton",
    "Image",
    "InfiniteScroll",
    "Inline",
    "Label",
    "Lazy",
    "Link",
    "LinkButton",
    "List",
    "Loading",
    "Main",
    "Model",
    "Nav",
    "NavigationPreloadPolicy",
    "Page",
    "PageResponse",
    "Pagination",
    "Poll",
    "Props",
    "RadioGroup",
    "RefreshButton",
    "RenderContext",
    "RenderMode",
    "RenderResult",
    "SafeUrl",
    "Secret",
    "Section",
    "SecurityPolicy",
    "SecurityProfile",
    "Select",
    "csrf_token_for_request",
    "SessionState",
    "Skeleton",
    "SseResponse",
    "Stack",
    "StreamingComponentResponse",
    "StyleSymbols",
    "SubmitButton",
    "Table",
    "Text",
    "TextArea",
    "TextInput",
    "Theme",
    "Title",
    "TrustedHtml",
    "UrlPurpose",
    "ALLOW_MISSING_ORIGIN",
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
    "Auto",
    "AltairChart",
    "CodeViewer",
    "ColorMode",
    "ColorModeToggle",
    "DataChanges",
    "DataEditor",
    "DataPage",
    "DataQuery",
    "DataSaveResult",
    "DataTable",
    "DownloadButton",
    "Expander",
    "FileUpload",
    "FragmentRegion",
    "HtmxRequest",
    "InMemoryDataSource",
    "InteractionPolicy",
    "InteractionResult",
    "JSONViewer",
    "LineChart",
    "Markdown",
    "MatplotlibChart",
    "Metric",
    "OAuthHelper",
    "OobUpdate",
    "PlotlyChart",
    "Progress",
    "Sidebar",
    "Status",
    "Tabs",
    "Toast",
    "apply_color_mode_cookie",
    "cache_component",
    "cache_data",
    "gather",
    "run_sync",
    "await_if_needed",
    "create_oauth_client",
    "default_interaction_policy",
    "form_sync_attrs",
    "get_icon",
    "highlight_code",
    "htmx_request",
    "invalidate_tags",
    "list_icons",
    "process_image",
    "read_color_mode_preference",
    "register_icon",
    "resolve_color_mode",
    "resolved_theme_from_request",
    "safe_download_response",
    "trusted_svg",
    "validate_email_address",
    "__version__",
    "action_attrs",
    "addressable",
    "approved_headers",
    "compile_css",
    "hedron_response",
    "html",
    "htmx_context",
    "merge_htmx_headers",
    "mount_hedron_static",
    "oob_swap",
    "redirect_external",
    "redirect_local",
    "render",
    "resolve_route_path",
    "session_state",
    "styles_from_manifest",
]
