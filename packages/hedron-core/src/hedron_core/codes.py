"""Stable diagnostic code catalog (complete through phase 0.19 accessibility)."""

from __future__ import annotations

# Config
HED_CONFIG_UNKNOWN_KEY = "HED-CONFIG-0001"
HED_CONFIG_UNSUPPORTED_VERSION = "HED-CONFIG-0002"
HED_CONFIG_INVALID = "HED-CONFIG-0003"

# Build
HED_BUILD_UNSUPPORTED_VERSION = "HED-BUILD-0001"
HED_BUILD_FAILED = "HED-BUILD-0002"
HED_BUILD_MISSING_MANIFEST = "HED-BUILD-0003"
HED_BUILD_RUNTIME_COMPILE = "HED-BUILD-0004"

# Assets
HED_ASSET_UNSUPPORTED_VERSION = "HED-ASSET-0001"
HED_ASSET_TRAVERSAL = "HED-ASSET-0002"
HED_ASSET_REMOTE = "HED-ASSET-0003"
HED_ASSET_MISSING = "HED-ASSET-0004"
HED_ASSET_COLLISION = "HED-ASSET-0005"
HED_ASSET_SYMLINK = "HED-ASSET-0006"
HED_ASSET_MIME = "HED-ASSET-0007"
HED_BROWSER_DUPLICATE = "HED-ASSET-0010"
HED_BROWSER_INVALID = "HED-ASSET-0011"
# Application asset plan (0.53 / ASSET-053)
HED_ASSET_0531 = "HED-ASSET-0531"  # duplicate application asset logical_id
HED_ASSET_0532 = "HED-ASSET-0532"  # missing application asset dependency
HED_ASSET_0533 = "HED-ASSET-0533"  # application asset dependency cycle
HED_ASSET_0534 = "HED-ASSET-0534"  # invalid application asset placement
HED_ASSET_0535 = "HED-ASSET-0535"  # invalid application asset kind
HED_ASSET_0536 = "HED-ASSET-0536"  # remote CDN / non-local application asset
HED_ASSET_0537 = "HED-ASSET-0537"  # fragment / inline script rejected
HED_ASSET_0538 = "HED-ASSET-0538"  # invalid CSP integrity value

# CSS
HED_CSS_UNSUPPORTED_VERSION = "HED-CSS-0001"
HED_CSS_PARSE = "HED-CSS-0002"
HED_CSS_UNKNOWN_SYMBOL = "HED-CSS-0003"
HED_CSS_UNSAFE_GLOBAL = "HED-CSS-0004"
HED_CSS_REMOTE = "HED-CSS-0005"
HED_CSS_INLINE = "HED-CSS-0006"
HED_CSS_DUPLICATE = "HED-CSS-0007"
HED_CSS_UNUSED = "HED-CSS-0008"

# Themes
HED_THEME_UNKNOWN = "HED-THEME-0001"
HED_THEME_MISSING_TOKEN = "HED-THEME-0002"
HED_THEME_INVALID = "HED-THEME-0003"
HED_THEME_DUPLICATE = "HED-THEME-0004"
HED_THEME_STYLE_CONTRACT = "HED-THEME-0005"
HED_THEME_ELEMENT_TOKEN = "HED-THEME-0006"

# Plugins
HED_PLUGIN_MISSING = "HED-PLUGIN-0001"
HED_PLUGIN_INCOMPATIBLE = "HED-PLUGIN-0002"
HED_PLUGIN_CYCLE = "HED-PLUGIN-0003"
HED_PLUGIN_DUPLICATE = "HED-PLUGIN-0004"
HED_PLUGIN_FAILED = "HED-PLUGIN-0005"

# Explorer (0.50)
HED_EXPLORER_0001 = "HED-EXPLORER-0001"  # truncated table / cursor pagination required
HED_EXPLORER_0002 = "HED-EXPLORER-0002"  # provider timeout/crash isolation
HED_EXPLORER_0003 = "HED-EXPLORER-0003"  # provider payload ceiling exceeded

# Render / HTML / model / route / security
HED_HTML_0001 = "HED-HTML-0001"
HED_HTML_0002 = "HED-HTML-0002"
HED_HTML_0003 = "HED-HTML-0003"
HED_HTML_0004 = "HED-HTML-0004"
HED_HTML_0005 = "HED-HTML-0005"
HED_HTML_0006 = "HED-HTML-0006"
HED_RENDER_0001 = "HED-RENDER-0001"
HED_RENDER_0002 = "HED-RENDER-0002"
HED_RENDER_0003 = "HED-RENDER-0003"
HED_RENDER_0004 = "HED-RENDER-0004"
HED_RENDER_0005 = "HED-RENDER-0005"
HED_RENDER_0006 = "HED-RENDER-0006"
HED_RENDER_0007 = "HED-RENDER-0007"
HED_RENDER_0008 = "HED-RENDER-0008"
HED_RENDER_0009 = "HED-RENDER-0009"
HED_RENDER_0010 = "HED-RENDER-0010"
HED_RENDER_0011 = "HED-RENDER-0011"
HED_RENDER_0012 = "HED-RENDER-0012"
HED_RENDER_0013 = "HED-RENDER-0013"
HED_RENDER_0014 = "HED-RENDER-0014"
HED_MODEL_0001 = "HED-MODEL-0001"
HED_MODEL_0002 = "HED-MODEL-0002"
HED_MODEL_0003 = "HED-MODEL-0003"
HED_MODEL_0004 = "HED-MODEL-0004"
HED_MODEL_0005 = "HED-MODEL-0005"
HED_MODEL_0006 = "HED-MODEL-0006"
HED_ROUTE_0001 = "HED-ROUTE-0001"
HED_SEC_0001 = "HED-SEC-0001"
HED_SEC_0002 = "HED-SEC-0002"
HED_SEC_0003 = "HED-SEC-0003"
HED_SEC_0004 = "HED-SEC-0004"
HED_SEC_0005 = "HED-SEC-0005"
HED_SEC_0006 = "HED-SEC-0006"
HED_SEC_0007 = "HED-SEC-0007"
HED_SEC_0008 = "HED-SEC-0008"
HED_SEC_0009 = "HED-SEC-0009"
HED_SEC_0010 = "HED-SEC-0010"
HED_SEC_0011 = "HED-SEC-0011"
HED_SEC_0020 = "HED-SEC-0020"

# Auto / icons / content / auth / compat
HED_AUTO_0001 = "HED-AUTO-0001"
HED_AUTO_0002 = "HED-AUTO-0002"
HED_AUTO_0003 = "HED-AUTO-0003"
HED_AUTO_0004 = "HED-AUTO-0004"
HED_ICON_0001 = "HED-ICON-0001"
HED_ICON_0002 = "HED-ICON-0002"
HED_ICON_0003 = "HED-ICON-0003"
HED_ICON_0004 = "HED-ICON-0004"
HED_CONTENT_0001 = "HED-CONTENT-0001"
HED_CONTENT_0002 = "HED-CONTENT-0002"
HED_CONTENT_0003 = "HED-CONTENT-0003"
HED_CONTENT_0004 = "HED-CONTENT-0004"
HED_CONTENT_0005 = "HED-CONTENT-0005"
HED_CONTENT_0006 = "HED-CONTENT-0006"
HED_CONTENT_0007 = "HED-CONTENT-0007"
HED_AUTH_0001 = "HED-AUTH-0001"
HED_COMPAT_0001 = "HED-COMPAT-0001"
HED_COMPAT_0002 = "HED-COMPAT-0002"
HED_COMPAT_0003 = "HED-COMPAT-0003"

# Charts
HED_CHART_0001 = "HED-CHART-0001"
HED_CHART_0002 = "HED-CHART-0002"
HED_CHART_0003 = "HED-CHART-0003"
HED_CHART_0004 = "HED-CHART-0004"
HED_CHART_0005 = "HED-CHART-0005"
HED_CHART_0006 = "HED-CHART-0006"
HED_CHART_0007 = "HED-CHART-0007"
HED_CHART_0010 = "HED-CHART-0010"
HED_CHART_0011 = "HED-CHART-0011"
HED_CHART_0012 = "HED-CHART-0012"
HED_CHART_0013 = "HED-CHART-0013"
HED_CHART_0014 = "HED-CHART-0014"
HED_CHART_0020 = "HED-CHART-0020"
HED_CHART_0021 = "HED-CHART-0021"
HED_CHART_0022 = "HED-CHART-0022"
HED_CHART_0023 = "HED-CHART-0023"
HED_CHART_0024 = "HED-CHART-0024"
HED_CHART_0025 = "HED-CHART-0025"
HED_CHART_0026 = "HED-CHART-0026"
HED_CHART_0030 = "HED-CHART-0030"
HED_CHART_0031 = "HED-CHART-0031"
HED_CHART_0032 = "HED-CHART-0032"
HED_CHART_0033 = "HED-CHART-0033"
HED_CHART_0061 = "HED-CHART-0061"
HED_CHART_0062 = "HED-CHART-0062"
HED_CHART_0063 = "HED-CHART-0063"
HED_CHART_0070 = "HED-CHART-0070"
HED_CHART_0071 = "HED-CHART-0071"
HED_CHART_0072 = "HED-CHART-0072"
HED_CHART_0073 = "HED-CHART-0073"

# Data
HED_DATA_0001 = "HED-DATA-0001"
HED_DATA_0002 = "HED-DATA-0002"
HED_DATA_0003 = "HED-DATA-0003"
HED_DATA_0004 = "HED-DATA-0004"
HED_DATA_0005 = "HED-DATA-0005"
HED_DATA_0006 = "HED-DATA-0006"
HED_DATA_0010 = "HED-DATA-0010"
HED_DATA_0011 = "HED-DATA-0011"
HED_DATA_0012 = "HED-DATA-0012"
HED_DATA_0013 = "HED-DATA-0013"
HED_DATA_0020 = "HED-DATA-0020"
HED_DATA_0025 = "HED-DATA-0025"
HED_DATA_0026 = "HED-DATA-0026"
HED_DATA_0027 = "HED-DATA-0027"
HED_DATA_0030 = "HED-DATA-0030"
HED_DATA_0031 = "HED-DATA-0031"
HED_DATA_0032 = "HED-DATA-0032"
HED_DATA_0033 = "HED-DATA-0033"
HED_DATA_0034 = "HED-DATA-0034"
HED_DATA_0040 = "HED-DATA-0040"
HED_DATA_0041 = "HED-DATA-0041"
HED_DATA_0050 = "HED-DATA-0050"
HED_DATA_0051 = "HED-DATA-0051"
HED_DATA_0060 = "HED-DATA-0060"
HED_DATA_0061 = "HED-DATA-0061"

# Jinja / HDJ
HED_JINJA_0002 = "HED-JINJA-0002"
HED_JINJA_0003 = "HED-JINJA-0003"
HED_JINJA_0004 = "HED-JINJA-0004"
HED_JINJA_0005 = "HED-JINJA-0005"
HED_JINJA_0006 = "HED-JINJA-0006"
HED_JINJA_0007 = "HED-JINJA-0007"
HED_JINJA_0008 = "HED-JINJA-0008"
HED_JINJA_0009 = "HED-JINJA-0009"
HED_JINJA_0010 = "HED-JINJA-0010"
HED_JINJA_0012 = "HED-JINJA-0012"
HED_JINJA_0013 = "HED-JINJA-0013"
HED_JINJA_0014 = "HED-JINJA-0014"
HED_JINJA_0015 = "HED-JINJA-0015"
HED_JINJA_0017 = "HED-JINJA-0017"
HED_JINJA_0018 = "HED-JINJA-0018"
HED_JINJA_0019 = "HED-JINJA-0019"
HED_JINJA_0020 = "HED-JINJA-0020"
HED_JINJA_0021 = "HED-JINJA-0021"
HED_JINJA_0022 = "HED-JINJA-0022"
HED_JINJA_0023 = "HED-JINJA-0023"
HED_JINJA_0024 = "HED-JINJA-0024"
HED_JINJA_0025 = "HED-JINJA-0025"
HED_JINJA_0026 = "HED-JINJA-0026"
HED_JINJA_0027 = "HED-JINJA-0027"
HED_JINJA_0030 = "HED-JINJA-0030"
HED_JINJA_0031 = "HED-JINJA-0031"
HED_JINJA_0032 = "HED-JINJA-0032"
HED_JINJA_0033 = "HED-JINJA-0033"
HED_HDJ_0100 = "HED-HDJ-0100"
HED_HDJ_0110 = "HED-HDJ-0110"
HED_HDJ_0111 = "HED-HDJ-0111"
HED_HDJ_0112 = "HED-HDJ-0112"

# Prepare / concurrency / tracing / audit (0.13)
HED_PREPARE_0001 = "HED-PREPARE-0001"
HED_PREPARE_0002 = "HED-PREPARE-0002"
HED_PREPARE_0003 = "HED-PREPARE-0003"
HED_CONC_0001 = "HED-CONC-0001"
HED_TRACE_0001 = "HED-TRACE-0001"
HED_AUDIT_0001 = "HED-AUDIT-0001"
HED_JOB_0001 = "HED-JOB-0001"

# HTMX / fragment regions (0.15 ergonomics)
HED_HTMX_0001 = "HED-HTMX-0001"
HED_HTMX_0002 = "HED-HTMX-0002"  # select_oob + OobUpdate same-target conflict

# First-class HTMX extension integration (0.48 RFC-0075 / D-083)
HED_EXT_0001 = "HED-EXT-0001"  # compatibility-default injection (sse + head-support)
HED_EXT_0002 = "HED-EXT-0002"  # unknown or excluded public id
HED_EXT_0003 = "HED-EXT-0003"  # morph undeclared / not admitted
HED_EXT_0004 = "HED-EXT-0004"  # opt-out conflicts with component requirement
HED_EXT_0005 = "HED-EXT-0005"  # missing vendored asset or digest mismatch
HED_EXT_0006 = "HED-EXT-0006"  # preload policy (mutation / user-derived URL)
HED_EXT_0007 = "HED-EXT-0007"  # incompatible declaration shape or combination
HED_EXT_0008 = "HED-EXT-0008"  # undeclared fragment requirement
HED_EXT_0009 = "HED-EXT-0009"  # request-derived or CDN asset URL
HED_EXT_0010 = "HED-EXT-0010"  # invalid SSE token or Last-Event-ID
HED_EXT_0011 = "HED-EXT-0011"  # head merge reject (inline/remote/nonce/unregistered)

# Refreshable views / commands / typed updates (0.43 RFC-0070)
HED_VIEW_0001 = "HED-VIEW-0001"  # unsafe or duplicate explicit key
HED_VIEW_0002 = "HED-VIEW-0002"  # duplicate unbound mount
HED_VIEW_0003 = "HED-VIEW-0003"  # unbound parameterized handle
HED_VIEW_0004 = "HED-VIEW-0004"  # structural bind failure
HED_CMD_0001 = "HED-CMD-0001"  # command cannot use a safe method
HED_CMD_0002 = "HED-CMD-0002"  # progressive-enhancement claim without fallback
HED_UPDATE_0001 = "HED-UPDATE-0001"  # mixed refresh and patch
HED_UPDATE_0002 = "HED-UPDATE-0002"  # duplicate patch target
HED_UPDATE_0003 = "HED-UPDATE-0003"  # foreign or unregistered handle
HED_UPDATE_0004 = "HED-UPDATE-0004"  # refresh/patch target limit exceeded
HED_UPDATE_0005 = "HED-UPDATE-0005"  # unsafe or unknown swap
HED_UPDATE_0006 = "HED-UPDATE-0006"  # OOB content with status 204
HED_UPDATE_0007 = "HED-UPDATE-0007"  # unbound parameterized patch target
HED_UPDATE_0008 = "HED-UPDATE-0008"  # missing primary patch
HED_UPDATE_0009 = "HED-UPDATE-0009"  # refresh event payload too large
HED_HOST_0001 = "HED-HOST-0001"  # unsafe fragment host tag or attribute

# Map / GeoJSON (0.15 RFC-0033)
HED_MAP_0001 = "HED-MAP-0001"
HED_MAP_0002 = "HED-MAP-0002"
HED_MAP_0003 = "HED-MAP-0003"
HED_MAP_0004 = "HED-MAP-0004"

# First-class maps (0.47 RFC-0074 / D-082)
HED_MAP_SPEC_0001 = "HED-MAP-SPEC-0001"
HED_MAP_SPEC_0002 = "HED-MAP-SPEC-0002"
HED_MAP_SPEC_0003 = "HED-MAP-SPEC-0003"
HED_MAP_SPEC_0004 = "HED-MAP-SPEC-0004"
HED_MAP_SOURCE_0001 = "HED-MAP-SOURCE-0001"
HED_MAP_SOURCE_0002 = "HED-MAP-SOURCE-0002"
HED_MAP_SOURCE_0003 = "HED-MAP-SOURCE-0003"
HED_MAP_POLICY_0001 = "HED-MAP-POLICY-0001"
HED_MAP_POLICY_0002 = "HED-MAP-POLICY-0002"
HED_MAP_STYLE_0001 = "HED-MAP-STYLE-0001"
HED_MAP_STYLE_0002 = "HED-MAP-STYLE-0002"
HED_MAP_OFFLINE_0001 = "HED-MAP-OFFLINE-0001"
HED_MAP_OFFLINE_0002 = "HED-MAP-OFFLINE-0002"
HED_MAP_OFFLINE_0003 = "HED-MAP-OFFLINE-0003"
HED_MAP_RUNTIME_0001 = "HED-MAP-RUNTIME-0001"
HED_MAP_RUNTIME_0002 = "HED-MAP-RUNTIME-0002"
HED_MAP_RUNTIME_0003 = "HED-MAP-RUNTIME-0003"
HED_MAP_EVENT_0001 = "HED-MAP-EVENT-0001"
HED_MAP_EVENT_0002 = "HED-MAP-EVENT-0002"
HED_MAP_EVENT_0003 = "HED-MAP-EVENT-0003"

# Interaction graph (0.17 RFC-0040)
HED_GRAPH_0001 = "HED-GRAPH-0001"  # missing dependency
HED_GRAPH_0002 = "HED-GRAPH-0002"  # cycle
HED_GRAPH_0003 = "HED-GRAPH-0003"  # duplicate writer
HED_GRAPH_0004 = "HED-GRAPH-0004"  # empty targets
HED_GRAPH_0005 = "HED-GRAPH-0005"  # invalid / duplicate binding id
HED_GRAPH_0006 = "HED-GRAPH-0006"  # replay disconnect / schedule interruption

# Property / collection patches (0.17 RFC-0041)
HED_PATCH_0001 = "HED-PATCH-0001"  # schema / op invalid
HED_PATCH_0002 = "HED-PATCH-0002"  # version / precondition mismatch
HED_PATCH_0003 = "HED-PATCH-0003"  # operation or payload cap exceeded
HED_PATCH_0004 = "HED-PATCH-0004"  # conflict / apply failure

# Model demos / inference (0.18)
HED_DEMO_0001 = "HED-DEMO-0001"  # unregistered callable / missing action
HED_DEMO_0002 = "HED-DEMO-0002"  # ambiguous schema / undeclared side effects
HED_DEMO_0003 = "HED-DEMO-0003"  # missing authorization / resource / exposure policy
HED_INFER_0001 = "HED-INFER-0001"  # admission / capacity overload
HED_INFER_0002 = "HED-INFER-0002"  # concurrency group / batch isolation failure
HED_INFER_0003 = "HED-INFER-0003"  # cancel / timeout / disconnect
HED_FEEDBACK_0001 = "HED-FEEDBACK-0001"  # missing consent / retention / tenant policy
HED_WORKFLOW_0001 = "HED-WORKFLOW-0001"  # schema / cycle / type failure
HED_WORKFLOW_0002 = "HED-WORKFLOW-0002"  # authorization / publish / conflict
HED_WORKFLOW_0003 = "HED-WORKFLOW-0003"  # arbitrary code / host path / auto-exposure

# Accessibility (0.19)
HED_A11Y_0001 = "HED-A11Y-0001"  # run axe / browser a11y analysis reminder
HED_A11Y_0010 = "HED-A11Y-0010"  # expired accessibility waiver
HED_A11Y_0011 = "HED-A11Y-0011"  # automatic conformance claim refused
HED_A11Y_0012 = "HED-A11Y-0012"  # statement export requires human approval

# Posit Workbench adapter (0.29 RFC-0062)
HED_WB_0001 = "HED-WB-0001"  # invalid configuration / conflicting mount or origin
HED_WB_0002 = "HED-WB-0002"  # malformed or rejected rserver-url output
HED_WB_0003 = "HED-WB-0003"  # rserver-url binary missing or failed
HED_WB_0004 = "HED-WB-0004"  # bind / listen failure
HED_WB_0005 = "HED-WB-0005"  # application import or factory failure
HED_WB_0006 = "HED-WB-0006"  # adversarial or malformed request target rejected
HED_WB_0007 = "HED-WB-0007"  # platform / image cannot run (e.g. non-amd64)
HED_WB_0008 = "HED-WB-0008"  # deprecated compatibility alias used
HED_WB_0009 = "HED-WB-0009"  # unsupported Workbench launch topology

# Unified Posit adapter (0.33 RFC-0066)
HED_POSIT_0101 = "HED-POSIT-0101"  # conflicting product evidence
HED_POSIT_0301 = "HED-POSIT-0301"  # invalid Connect base header (spoof / peer)
HED_POSIT_0302 = "HED-POSIT-0302"  # Connect base path validation failed
HED_POSIT_0303 = "HED-POSIT-0303"  # duplicate Connect base headers
HED_POSIT_0304 = "HED-POSIT-0304"  # Connect base path does not match ASGI root_path
HED_POSIT_0401 = "HED-POSIT-0401"  # authenticated_header_v1 not Supported in 0.33
HED_POSIT_0508 = "HED-POSIT-0508"  # refusing literal cookie Path=auto via registry
HED_POSIT_0512 = "HED-POSIT-0512"  # diagnostic: literal cookie Path=auto
HED_POSIT_0513 = "HED-POSIT-0513"  # diagnostic: cookie Path does not match mount
HED_POSIT_0514 = "HED-POSIT-0514"  # diagnostic: Location/redirect not mount-prefixed
HED_POSIT_0515 = "HED-POSIT-0515"  # diagnostic: Location escapes app mount
HED_POSIT_0516 = "HED-POSIT-0516"  # diagnostic: unregistered owned cookie name

# Streamlit AST migrator (0.31 RFC-0061)
HED_MIG_ST_0001 = "HED-MIG-ST-0001"  # unresolved / dynamic Streamlit symbol
HED_MIG_ST_0002 = "HED-MIG-ST-0002"  # unsupported or version-unknown API
HED_MIG_ST_0003 = "HED-MIG-ST-0003"  # ambiguous widget-state owner
HED_MIG_ST_0004 = "HED-MIG-ST-0004"  # callback or rerun control flow
HED_MIG_ST_0005 = "HED-MIG-ST-0005"  # interleaved or duplicate side effect
HED_MIG_ST_0006 = "HED-MIG-ST-0006"  # cache / resource lifecycle review
HED_MIG_ST_0007 = "HED-MIG-ST-0007"  # raw HTML / unsafe URL / file / secret / component
HED_MIG_ST_0008 = "HED-MIG-ST-0008"  # authentication / authorization / tenant boundary
HED_MIG_ST_0009 = "HED-MIG-ST-0009"  # accessibility label / order / fallback review
HED_MIG_ST_0010 = "HED-MIG-ST-0010"  # dependency / hosting non-parity
HED_MIG_ST_0011 = "HED-MIG-ST-0011"  # parse / discovery / analysis limit failure
HED_MIG_ST_0012 = "HED-MIG-ST-0012"  # output destination refused or write failure
HED_MIG_ST_0013 = "HED-MIG-ST-0013"  # scaffolded mapping requires review
HED_MIG_ST_0014 = "HED-MIG-ST-0014"  # report-only construct (no generated code)


# Web Component element ABI (0.36 RFC-0060 / D-064)
HED_ELEMENT_0001 = "HED-ELEMENT-0001"  # tag or ABI definition conflict
HED_ELEMENT_0002 = "HED-ELEMENT-0002"  # incompatible server/module ABI pair
HED_ELEMENT_0003 = "HED-ELEMENT-0003"  # hedron- prefix / naming violation
HED_ELEMENT_0004 = "HED-ELEMENT-0004"  # missing or undeclared module/CSS asset
HED_ELEMENT_0005 = "HED-ELEMENT-0005"  # structured-input schema/bound/encoding failure
HED_ELEMENT_0006 = "HED-ELEMENT-0006"  # module timeout / init / upgrade failure
HED_ELEMENT_0007 = "HED-ELEMENT-0007"  # incomplete/invalid form_contract at registration
HED_ELEMENT_ASSET_0001 = "HED-ELEMENT-ASSET-0001"  # packaged asset name escapes static/
HED_ELEMENT_ASSET_0002 = "HED-ELEMENT-ASSET-0002"  # packaged element asset missing
HED_ELEMENT_AUTHOR_0001 = "HED-ELEMENT-AUTHOR-0001"  # incomplete third-party author metadata
HED_ELEMENT_AUTHOR_0002 = "HED-ELEMENT-AUTHOR-0002"  # invalid author tag or a11y_contract
HED_ELEMENT_STATE_0001 = "HED-ELEMENT-STATE-0001"  # unknown/missing ownership mode
HED_ELEMENT_STATE_0002 = "HED-ELEMENT-STATE-0002"  # illegal persistence / capability owned
HED_ELEMENT_STATE_0003 = "HED-ELEMENT-STATE-0003"  # controlled update loop / illegal intent
HED_ELEMENT_STATE_0004 = "HED-ELEMENT-STATE-0004"  # dirty-draft incoming without policy
HED_ELEMENT_STATE_0005 = "HED-ELEMENT-STATE-0005"  # conflict entered; LWW refused
HED_ELEMENT_STATE_0006 = "HED-ELEMENT-STATE-0006"  # transfer attempted before 0.40

# Type-driven authoring (0.44 RFC-0071 / D-076). HED-TYPE-BIND-SOURCE maps to 0001.
HED_TYPE_0001 = "HED-TYPE-0001"  # dependency/request/security name supplied to bind/form
HED_TYPE_BIND_SOURCE = HED_TYPE_0001
HED_TYPE_0002 = "HED-TYPE-0002"  # duplicate or conflicting Hedron markers
HED_TYPE_0003 = "HED-TYPE-0003"  # invalid boundary model / validation
HED_TYPE_0004 = "HED-TYPE-0004"  # TypeSchema bounds or fingerprint mismatch
HED_TYPE_0005 = "HED-TYPE-0005"  # form generation inventory / Control.kind
HED_TYPE_0006 = "HED-TYPE-0006"  # declared effect subset mismatch
HED_TYPE_0007 = "HED-TYPE-0007"  # OutcomeMap coverage / mapping
HED_TYPE_0008 = "HED-TYPE-0008"  # class handler lifecycle
HED_TYPE_0009 = "HED-TYPE-0009"  # host/adapter TypeSchema disposition
HED_TYPE_0010 = "HED-TYPE-0010"  # sensitive leak / identity contradiction
# FastAPI/Pydantic convergence (0.49 RFC-0076 / D-084). Do not reuse TYPE 0001–0010.
HED_FP_0001 = "HED-FP-0001"  # lifetime / DependsOn compile or background capture
HED_FP_0002 = "HED-FP-0002"  # BoundaryBindingPlan ineligible native-model / fallback
HED_FP_0003 = "HED-FP-0003"  # TypeSchema v2 sanitizer / dual-version load
HED_FP_0004 = "HED-FP-0004"  # tagged public-wire union / unknown kind
HED_FP_0005 = "HED-FP-0005"  # late registration after seal / OpenAPI cache
HED_FP_0006 = "HED-FP-0006"  # RequiresScopes / strict content-type (non-granting)
HED_FP_0007 = "HED-FP-0007"  # cached TypeAdapter / JSON bounds / duplicate keys
HED_FP_0008 = "HED-FP-0008"  # settings/research leakage into Supported surfaces
# Interaction catalog / projections (0.45 RFC-0072 / D-077)
HED_CATALOG_0001 = "HED-CATALOG-0001"  # version / fingerprint / ownership mismatch
HED_CATALOG_0002 = "HED-CATALOG-0002"  # duplicate logical id or ambiguous ownership
HED_CATALOG_0003 = "HED-CATALOG-0003"  # mutation after catalog seal
HED_CATALOG_0004 = "HED-CATALOG-0004"  # required catalog entry missing
HED_CATALOG_0005 = "HED-CATALOG-0005"  # catalog / manifest bounds exceeded
HED_CATALOG_0006 = "HED-CATALOG-0006"  # required manifest missing or corrupt
HED_CATALOG_0007 = "HED-CATALOG-0007"  # adversarial or non-canonical JSON
HED_CATALOG_0008 = "HED-CATALOG-0008"  # production profile leakage / forbidden keys
HED_PROJECTION_0001 = "HED-PROJECTION-0001"  # duplicate or reserved namespace
HED_PROJECTION_0002 = "HED-PROJECTION-0002"  # projection bounds or schema failure
HED_PROJECTION_0003 = "HED-PROJECTION-0003"  # unknown optional projection version
HED_PROJECTION_0004 = "HED-PROJECTION-0004"  # untrusted provider invocation
HED_PROJECTION_0005 = "HED-PROJECTION-0005"  # host / consumer exception
HED_PROJECTION_0006 = "HED-PROJECTION-0006"  # provider disable/uninstall mismatch
# Feature bundles (0.46 RFC-0073 / D-075 / D-079)
HED_BUNDLE_0001 = "HED-BUNDLE-0001"  # include/eject after registry or catalog seal
HED_BUNDLE_0002 = "HED-BUNDLE-0002"  # duplicate bundle/handle/route/namespace
HED_BUNDLE_0003 = "HED-BUNDLE-0003"  # dependency cycle, missing dep, or depth
HED_BUNDLE_0004 = "HED-BUNDLE-0004"  # missing required capability
HED_BUNDLE_0005 = "HED-BUNDLE-0005"  # bundle/workspace/chart bounds exceeded
HED_BUNDLE_0006 = "HED-BUNDLE-0006"  # include failure; rollback required
HED_BUNDLE_0007 = "HED-BUNDLE-0007"  # invalid bundle shape or identity
HED_BUNDLE_0008 = "HED-BUNDLE-0008"  # conflict with an existing artifact
HED_BUNDLE_0009 = "HED-BUNDLE-0009"  # eject/uninstall after seal or unknown id
HED_BUNDLE_0010 = "HED-BUNDLE-0010"  # third-party isolation / private API

HED_SIM_ASSET_0001 = "HED-SIM-ASSET-0001"  # packaged sim asset name escapes static/
HED_SIM_ASSET_0002 = "HED-SIM-ASSET-0002"  # packaged sim asset missing


def registered_codes() -> frozenset[str]:
    """Return every ``HED-*`` code constant defined in this module."""
    return frozenset(
        value
        for name, value in globals().items()
        if isinstance(value, str) and value.startswith("HED-") and name.isupper()
    )


ALL_CODES: frozenset[str] = registered_codes()
