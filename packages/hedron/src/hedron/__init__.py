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


__version__ = "0.13.0"

# Stable + beta public facade. Live transports live in ``hedron.experimental``
# (compat attribute access retained via ``__getattr__``). Optional data/charts/auth
# extras remain lazy and are not part of the stable tier.
__all__ = [
    "Alert",
    "Aside",
    "Auto",
    "AutoForm",
    "Badge",
    "Button",
    "Card",
    "ChatInput",
    "ChatMessage",
    "Checkbox",
    "CodeBlock",
    "CodeViewer",
    "ColorMode",
    "ColorModeToggle",
    "Component",
    "ComponentRef",
    "ComponentResponse",
    "Container",
    "DescriptionList",
    "Dialog",
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
    "Grid",
    "HTML",
    "Head",
    "Header",
    "Heading",
    "Hedron",
    "HedronRoute",
    "HedronRouter",
    "HtmxRequest",
    "IconButton",
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
    "Main",
    "Metric",
    "Model",
    "Nav",
    "OobUpdate",
    "Page",
    "PageResponse",
    "Pagination",
    "Poll",
    "Progress",
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
    "SessionState",
    "Sidebar",
    "Skeleton",
    "Stack",
    "Status",
    "StyleSymbols",
    "SubmitButton",
    "Table",
    "Tabs",
    "Text",
    "TextArea",
    "TextInput",
    "Theme",
    "Title",
    "Toast",
    "TrustedHtml",
    "UrlPurpose",
    "__version__",
    "action_attrs",
    "addressable",
    "apply_color_mode_cookie",
    "approved_headers",
    "await_if_needed",
    "cache_component",
    "cache_data",
    "compile_css",
    "csrf_token_for_request",
    "default_interaction_policy",
    "form_sync_attrs",
    "gather",
    "get_icon",
    "hedron_response",
    "html",
    "htmx_context",
    "htmx_request",
    "invalidate_tags",
    "list_icons",
    "merge_htmx_headers",
    "mount_hedron_static",
    "oob_swap",
    "read_color_mode_preference",
    "redirect_external",
    "redirect_local",
    "register_icon",
    "render",
    "resolve_color_mode",
    "resolve_route_path",
    "resolved_theme_from_request",
    "run_sync",
    "safe_download_response",
    "session_state",
    "styles_from_manifest",
    "trusted_svg",
]
