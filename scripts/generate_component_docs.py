#!/usr/bin/env python3
# ruff: noqa: E501
"""Generate the dedicated documentation page for every public Hedron component.

The manifest in this file is deliberately explicit.  It doubles as the reviewable
component-docs inventory and lets CI detect a newly exported component that has no demo.
Run ``uv run python scripts/generate_component_docs.py`` after changing the manifest and
``uv run python scripts/generate_component_docs.py --check`` to verify generated pages.
"""

from __future__ import annotations

import argparse
import ast
import difflib
import inspect
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "components"
DEMOS = ROOT / "docs"


def _format_sim_live_demo(sim_name: str) -> str:
    """Demo/Code tabs: simulated island + full runnable Hedron ``app.py``."""
    import sys

    if str(DEMOS) not in sys.path:
        sys.path.insert(0, str(DEMOS))
    from demos.tabs import format_demo_code_tabs

    return format_demo_code_tabs(
        sim_name,
        demo_blurb=(
            "Docs simulation — not a running Hedron server. Interactive demos show a "
            "“Simulated HTMX” trace when applicable."
        ),
    )


# Keep install snippets aligned with docs/release.toml / check_docs_train_ssot.py.
_ALPHA_EXTRAS = frozenset({"notebook", "mcp", "gradio"})
_RELEASE = tomllib.loads((ROOT / "docs" / "release.toml").read_text(encoding="utf-8"))["release"]
_PIN_FLOOR = (
    _RELEASE["pypi_pin_floor"]
    if _RELEASE.get("registry_status") == "deferred"
    else _RELEASE["pin_floor"]
)
_PIN_CEILING = (
    _RELEASE["pypi_pin_ceiling"]
    if _RELEASE.get("registry_status") == "deferred"
    else _RELEASE["pin_ceiling"]
)
_TRAIN_PIN = f">={_PIN_FLOOR},<{_PIN_CEILING}"
_ALPHA_PIN = ">=0.1.0,<0.2"
_CHARTS_PIN = ">=0.2.0,<0.3"
_CHARTS_FLAGSHIP_PIN = _TRAIN_PIN
_NATIVE_PIN = ">=0.1.2,<0.2"


def _install_requirement(package: str) -> str:
    """Return a pip requirement with the current train / Alpha upper bound."""
    match = re.fullmatch(r"hedron\[([^\]]+)\]", package)
    if match is not None:
        extra = match.group(1).split(",", 1)[0].strip()
        if extra == "charts":
            pin = _CHARTS_FLAGSHIP_PIN
        elif extra == "native":
            pin = _CHARTS_FLAGSHIP_PIN  # flagship extra pin tracks train; package is 0.1.x
        elif extra in _ALPHA_EXTRAS:
            pin = _ALPHA_PIN
        else:
            pin = _TRAIN_PIN
        return f"{package}{pin}"
    if package == "hedron-charts" or package.startswith("hedron-charts["):
        return f"{package}{_CHARTS_PIN}"
    if package == "hedron-native" or package.startswith("hedron-native["):
        return f"{package}{_NATIVE_PIN}"
    return package


def _optional_install_text(package: str) -> str:
    """Return the optional-provider installation note."""
    return (
        "\n\nInstall the optional provider before importing this component:"
        f'\n\n```bash\npip install "{_install_requirement(package)}"\n```'
    )


@dataclass(frozen=True)
class ComponentDoc:
    name: str
    group: str
    summary: str
    signature: str
    example: str
    params: tuple[tuple[str, str, str], ...]
    detail: str
    a11y: str
    pitfall: str
    package: str = "hedron"
    server: str = "No"
    demo: str = "static"

    @property
    def slug(self) -> str:
        words = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", self.name)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", words).lower()


GROUPS = {
    "document": ("Document and composition", "Full pages, metadata, and fragment composition."),
    "landmarks": (
        "Landmarks",
        "Semantic regions that give a page its accessible structure. "
        "`Header`, `Main`, `Nav`, `Aside`, `Footer`, and `Section` are real typed exports "
        "with allowlisted safe HTML attributes, not factory variables.",
    ),
    "layout": ("Layout", "Explicit containers and one-dimensional or grid composition."),
    "content": ("Content", "Text, links, media, code, lists, tables, and Markdown."),
    "surfaces": ("Surfaces and status", "Cards, labels, alerts, and loading placeholders."),
    "controls": ("Controls", "Buttons and links for commands and navigation."),
    "forms": ("Forms", "Typed, labelled controls and validation presentation."),
    "interaction": ("Interaction", "FastAPI and HTMX-oriented request/response components."),
    "data": ("Data", "Automatic rendering, tabular display, and editable data."),
    "utilities": ("Utilities", "Metrics, viewers, progress, status, disclosure, tabs, and files."),
    "theme": ("Theme", "User-facing color-mode preference controls."),
    "charts": ("Charts", "Accessible visualization components and optional plotting adapters."),
}

_PHASE_061_COMPONENTS = frozenset(
    {"Tabs", "Container", "NavGroup", "AmbientBackdrop", "Identity", "AsyncRegion", "AppShell"}
)


def p(name: str, type_: str, meaning: str) -> tuple[str, str, str]:
    return name, type_, meaning


COMPONENTS = (
    ComponentDoc(
        "Page",
        "document",
        "Render a complete HTML document with safe head defaults and a body.",
        "Page(*body, lang='en', title=None, head=None, children=None, data_theme=None, data_hedron_theme=None, dir=None, scripts=None, script_defer=True)",
        "Page(Header(Heading('Account', level=1)), Main(Text('Signed in')), title='Account')",
        (
            p(
                "body / children",
                "NodeLike",
                "Body nodes; use either positional children or `children=`.",
            ),
            p("lang", "str", "The document language written to `<html lang>`."),
            p("title", "str | None", "Convenience document title."),
            p("head", "NodeLike | None", "Additional trusted head nodes."),
            p("data_theme", "str | None", "Initial `data-theme` value."),
            p(
                "data_hedron_theme",
                "str | None",
                "Named Hedron theme for this document; overrides the app selection.",
            ),
            p("dir", "str | None", "Optional `dir` on `<html>` (`ltr` / `rtl` / `auto`)."),
            p(
                "scripts",
                "Sequence[SafeUrl] | None",
                "Allowlisted same-origin `SafeUrl` ASSET scripts; free-form `<script>` nodes stay out of the tree.",
            ),
            p(
                "script_defer",
                "bool",
                "When true (default), emitted script tags use `defer`.",
            ),
        ),
        "`Page` owns the outer `html`, `head`, and `body` elements. It always emits UTF-8 and responsive viewport metadata, then adds the title and optional head slot before rendering body children. Optional `scripts=` emits allowlisted same-origin script tags after body children.",
        "Set `lang` to the language of the page and keep exactly one main landmark in the body. Pass only `SafeUrl` ASSET paths in `scripts=` (root-relative, same-origin).",
        "Do not return `Page` for an HTMX fragment request; use `Fragment` and fragment render mode instead.",
        server="Page response",
    ),
    ComponentDoc(
        "Fragment",
        "document",
        "Return several sibling nodes without adding a wrapper element.",
        "Fragment(*nodes, children=None)",
        "Fragment(Alert('Saved', tone='success'), Text('The record is current.'))",
        (
            p("nodes", "NodeLike", "Positional renderable sibling nodes."),
            p(
                "children",
                "NodeLike | sequence | None",
                "Keyword alternative; combines with positional nodes.",
            ),
        ),
        "A fragment flattens its children into the render stream. It is ideal for targeted HTMX responses because it does not change the target's surrounding layout or introduce an accidental DOM node.",
        "After a swap, focus and live-region behavior still belong to the response content; a wrapper-free result does not announce itself.",
        "Do not rely on a fragment to carry an `id`, class, or HTMX target—there is no wrapper on which to place attributes.",
        server="Common for HTMX",
        demo="fragment",
    ),
    ComponentDoc(
        "Head",
        "document",
        "Compose explicit document-head children when building lower-level document output.",
        "Head(*nodes, children=None)",
        "Head(Title('Reports'), html.meta(name='description', content='Weekly reports'))",
        (
            p("nodes", "NodeLike", "Positional head-safe nodes such as `Title` and `html.meta`."),
            p(
                "children",
                "NodeLike | sequence | None",
                "Keyword alternative; combines with positional nodes.",
            ),
        ),
        "`Head` renders a semantic `<head>` node. Most applications should prefer `Page(title=..., head=...)`, while `Head` is useful to libraries and tests that need explicit document composition.",
        "Give every page a useful title; metadata has no visible fallback for assistive-technology users.",
        "Never place user-supplied raw markup in the head. Use validated native elements and `TrustedHtml` only at a reviewed trust boundary.",
    ),
    ComponentDoc(
        "Title",
        "document",
        "Set the browser-tab and history-entry title.",
        "Title(text=None, *, children=None)",
        "Title('Billing · Acme')",
        (
            p("text", "str | None", "Preferred title text."),
            p("children", "str | None", "Alternative authoring form when `text` is omitted."),
        ),
        "`Title` emits exactly one `<title>` element. Put it in a `Head`, or use the simpler `title=` argument on `Page`.",
        "Use a concise, unique title whose most specific information comes first.",
        "This is document metadata, not a visible heading. Pair it with a page `Heading(level=1)`.",
    ),
    *tuple(
        ComponentDoc(
            name,
            "landmarks",
            f"Render the semantic `{tag}` landmark for {purpose}.",
            f"{name}(*nodes, children=None, class_=None, id=None, lang=None, dir=None, role=None, aria=None, data=None, ...)",
            f"{name}(Heading('{label}', level={level}), Text('{copy}'))",
            (
                p("nodes", "NodeLike", "Positional content belonging to this semantic region."),
                p(
                    "children",
                    "NodeLike | sequence | None",
                    "Keyword alternative; combines with positional nodes.",
                ),
                p("class_", "str | None", "Optional authored class name."),
                p("id", "str | None", "Stable fragment or target identifier."),
                p(
                    "lang / dir / role / title / tabindex / aria / data / hidden",
                    "allowlisted",
                    "Safe HTML attributes; hostile roles like `presentation` / `none` are rejected.",
                ),
            ),
            f"`{name}` emits a native `<{tag}>`, preserving semantic navigation instead of using a generic div. Children may be passed individually or as one non-string sequence. Landmark helpers are real typed classes with an allowlisted attribute set.",
            a11y,
            pitfall,
        )
        for name, tag, purpose, label, level, copy, a11y, pitfall in (
            (
                "Header",
                "header",
                "introductory content",
                "Acme",
                1,
                "Workspace overview",
                "Do not nest a page-level header inside main; a section may have its own header when it labels that section.",
                "A header is not automatically a banner landmark when nested. Choose placement intentionally.",
            ),
            (
                "Main",
                "main",
                "the page's primary content",
                "Dashboard",
                1,
                "Current workspace activity",
                "Use one visible main landmark per full page so keyboard and screen-reader users can reach primary content directly.",
                "Do not put repeated navigation, footers, or modal content inside main.",
            ),
            (
                "Nav",
                "nav",
                "a major collection of navigation links",
                "Documentation",
                2,
                "Guides and reference",
                "Give each navigation landmark a distinct accessible label when a page contains more than one.",
                "Do not use Nav for every group of links; reserve it for significant navigation.",
            ),
            (
                "Aside",
                "aside",
                "related but secondary content",
                "On this page",
                2,
                "Related settings",
                "The aside should remain understandable as complementary content when read separately from the main flow.",
                "Do not place content required to complete the primary task only in an aside.",
            ),
            (
                "Footer",
                "footer",
                "closing information for a page or section",
                "Support",
                2,
                "Contact the platform team",
                "Use explicit link text and keep legal or support navigation grouped meaningfully.",
                "A nested section footer is not the page-wide contentinfo landmark.",
            ),
            (
                "Section",
                "section",
                "a thematically grouped region",
                "Recent activity",
                2,
                "Three deployments succeeded",
                "Every significant section should have a heading that gives the region an accessible name.",
                "If the content has no meaningful heading, a generic container may be more appropriate.",
            ),
        )
    ),
    ComponentDoc(
        "Container",
        "layout",
        "Constrain and center a readable block of page content.",
        "Container(*nodes, children=None, id=None, class_=None, query='none', name=None, max_width=None, align=None, padding=None)",
        "Container(Heading('Profile', level=1), Text('Manage your public details.'), query='inline-size', name='profile')",
        (
            p("nodes", "NodeLike", "Positional content inside the width constraint."),
            p(
                "children",
                "NodeLike | sequence | None",
                "Keyword alternative for generated or declarative child lists; combines with positional nodes.",
            ),
            p("id", "str | None", "Stable DOM target for links, tests, and HTMX swaps."),
            p(
                "class_",
                "str | None",
                "Application class appended after `hedron-container`; the built-in theme hook is retained.",
            ),
            p("query", "Literal['none', 'inline-size']", "Opt into an inline-size query boundary. Default: `'none'` (existing viewport behavior)."),
            p("name", "str | None", "Validated container name, valid only with `query='inline-size'`."),
            p("max_width", "xs | sm | md | lg | xl | full | None", "Finite readable-width token."),
            p("align", "start | center | end | None", "Inline alignment inside the containing block."),
            p("padding", "none | sm | md | lg | None", "Theme-owned block spacing token."),
        ),
        "The component emits an addressable div and always retains the `hedron-container` theme hook. In 0.59, `query='inline-size'` opts the boundary into container-aware responsive styling and `name=` adds a validated named-container marker. Phase 0.61 adds finite width, alignment, and spacing markers without changing the default viewport behavior. Positional nodes and `children=` use the same normalization rules, and an application class augments rather than disables the built-in layout.",
        "A container has no semantics of its own, so keep headings and landmarks inside it.",
        "Do not use Container as a substitute for Main or Section. Do not assume `query='inline-size'` is a viewport breakpoint; use the existing responsive maps when viewport semantics are intended.",
    ),
    ComponentDoc(
        "PageHeader",
        "layout",
        "Eyebrow/title/description header with optional status and actions.",
        "PageHeader(*, title, eyebrow=None, description=None, status=None, actions=None, id=None, class_=None)",
        "PageHeader(title='Pipelines', eyebrow='Operate', description='Source to destination jobs.', actions=ActionGroup(Button('New')))",
        (
            p("title", "str | NodeLike", "Primary heading text or node."),
            p("eyebrow", "str | NodeLike | None", "Optional overline label."),
            p("description", "str | NodeLike | None", "Supporting copy under the title."),
            p("status", "NodeLike | None", "Optional status chip or badge."),
            p("actions", "NodeLike | None", "Primary action cluster (often ActionGroup)."),
        ),
        "PageHeader is the workspace page pattern for title, context, and actions without application CSS.",
        "Keep one PageHeader per primary view and put long forms below it.",
        "Do not nest PageHeader inside another PageHeader.",
    ),
    ComponentDoc(
        "SplitView",
        "layout",
        "Two-pane layout with closed ratio and responsive collapse.",
        "SplitView(primary, secondary, *, ratio='1:1', collapse='md', gap='1rem', id=None, class_=None)",
        "SplitView(Card(Text('Source')), Card(Text('Destination')), ratio='2:1')",
        (
            p("primary / secondary", "NodeLike", "Left and right panes."),
            p("ratio", "str", "Closed split ratio such as `1:1`, `2:1`, or `1:3`."),
            p("collapse", "str", "Breakpoint where panes stack (`never` / `sm` / `md` / `lg`)."),
        ),
        "SplitView owns unequal column ratios through theme CSS so application authors never hand-write grid templates.",
        "Prefer SplitView for source/destination or directory/detail workspaces.",
        "Do not pass arbitrary CSS grid templates; use the closed ratio set.",
    ),
    ComponentDoc(
        "MasterDetail",
        "layout",
        "Responsive master-detail layout with named fragment regions.",
        "MasterDetail(master, detail=None, *, ratio='1:2', collapse='md', master_id='master', detail_id='detail', state='ready', empty_message='Select an item')",
        "MasterDetail(Text('Items'), Text('Detail'), master_id='master', detail_id='detail')",
        (
            p("master / detail", "NodeLike", "List pane and detail pane content."),
            p("state", "str", "`ready` / `loading` / `empty` / `error` / `permission`."),
            p("master_id / detail_id", "str", "Named fragment region ids for HTMX swaps."),
            p("ratio", "str", "Closed split ratio such as `1:2` or `1:1`."),
            p("collapse", "str", "Breakpoint where panes stack (`never` / `sm` / `md` / `lg`)."),
        ),
        "MasterDetail composes list/detail workspaces with theme-owned ratios and region ids for fragment updates.",
        "Use permission/empty/error states so denied or missing selections never leak detail content.",
        "Do not invent CSS escapes for pane sizing; stay on the closed ratio vocabulary.",
    ),
    ComponentDoc(
        "FormGrid",
        "layout",
        "Responsive field grid for forms and settings panels.",
        "FormGrid(*fields, *, columns=2, collapse='md', gap='1rem', id=None, class_=None)",
        "FormGrid(FormField('Name', TextInput(name='name')), FormField('Email', TextInput(name='email')))",
        (
            p("fields", "NodeLike", "Form fields or labelled controls."),
            p("columns", "int | Mapping", "Column count or responsive map."),
            p("collapse", "str", "Breakpoint where the grid stacks."),
        ),
        "FormGrid lays out labelled controls with theme-owned gutters and collapse behavior.",
        "Keep related fields in one FormGrid; use Stack for vertical-only sections.",
        "Do not mix FormGrid with equal-column Grid when you need ratio control—use SplitView.",
    ),
    ComponentDoc(
        "ActionGroup",
        "layout",
        "Aligned cluster of actions for headers and footers.",
        "ActionGroup(*actions, *, align='end', gap='0.5rem', id=None, class_=None)",
        "ActionGroup(Button('Cancel', appearance='ghost'), Button('Save'), align='end')",
        (
            p("actions", "NodeLike", "Buttons or links in the cluster."),
            p("align", "str", "`start` / `center` / `end` / `between`."),
        ),
        "ActionGroup keeps toolbar spacing and alignment in the default theme.",
        "Place primary actions last in LTR layouts.",
        "Do not use ActionGroup for navigation lists—use Nav / NavLink.",
    ),
    ComponentDoc(
        "Stack",
        "layout",
        "Arrange children vertically with a validated, consistent gap.",
        "Stack(*nodes, children=None, gap='1rem', id=None, class_=None)",
        "Stack(Heading('Settings', level=2), Text('Profile'), Button('Save'), gap='lg')",
        (
            p("nodes", "NodeLike", "Positional items in visual and DOM order."),
            p(
                "children",
                "NodeLike | sequence | None",
                "Keyword child list; combines with positional nodes.",
            ),
            p("gap", "CSS length", "Validated `rem`, `em`, `px`, or `%` spacing."),
            p("id", "str | None", "Stable DOM target for the stack region."),
            p("class_", "str | None", "Optional class appended to `hedron-stack`."),
        ),
        "`Stack` writes layout intent and the validated gap to data attributes consumed by the theme; the shipped theme applies that exact gap without requiring an unsafe inline style. Its built-in class is retained when you add an application class. DOM order is unchanged, so the visual sequence matches reading and keyboard order.",
        "Keep DOM order meaningful and never use CSS reordering to change the task sequence.",
        "Values such as `calc(...)`, viewport units, and arbitrary CSS are rejected; use a supported length token.",
    ),
    ComponentDoc(
        "Inline",
        "layout",
        "Arrange related children in a wrapping horizontal row.",
        "Inline(*nodes, children=None, gap='0.5rem', id=None, class_=None)",
        "Inline(Button('Save'), LinkButton('Cancel', '/account'), gap='md')",
        (
            p("nodes", "NodeLike", "Positional inline items in DOM order."),
            p(
                "children",
                "NodeLike | sequence | None",
                "Keyword child list; combines with positional nodes.",
            ),
            p("gap", "CSS length", "Validated spacing token."),
            p("id", "str | None", "Stable DOM target for the row."),
            p("class_", "str | None", "Optional class appended to `hedron-inline`."),
        ),
        "`Inline` expresses one-dimensional horizontal composition while allowing the theme to wrap items at narrow widths. It emits data attributes rather than unsafe inline style.",
        "Ensure controls remain understandable when the row wraps and do not communicate meaning using position alone.",
        "Do not assume an Inline will stay on one physical line on small screens.",
    ),
    ComponentDoc(
        "Grid",
        "layout",
        "Lay out explicit child components in a responsive grid.",
        "Grid(*nodes, children=None, columns=2, gap='1rem', id=None, class_=None)",
        "Grid(Card(Text('Latency')), Card(Text('Errors')), Card(Text('Traffic')), columns=3)",
        (
            p("nodes", "NodeLike", "Positional grid cells in reading order."),
            p(
                "children",
                "NodeLike | sequence | None",
                "Keyword child list; combines with positional nodes.",
            ),
            p("columns", "int", "Requested column count; must be at least one."),
            p("gap", "CSS length", "Validated row and column gap."),
            p("id", "str | None", "Stable DOM target for the grid region."),
            p("class_", "str | None", "Optional class appended to `hedron-grid`."),
        ),
        "Grid is declarative composition: it returns one component, not mutable positional column handles. The theme reads column and gap data attributes and may collapse columns responsively.",
        "Source order must remain the intended reading order at every breakpoint.",
        "Do not hold a column handle and mutate it later; construct every cell as a child.",
    ),
    ComponentDoc(
        "GridItem",
        "layout",
        "Place one cell with named track and span tokens inside Grid.",
        "GridItem(*nodes, *, span=1, align='stretch', id=None, class_=None)",
        "GridItem(Card(Text('Wide')), span=2)",
        (
            p("nodes", "NodeLike", "Cell content."),
            p("span", "int | breakpoint map", "Column span (1–6), optionally responsive."),
            p("align", "start | center | end | stretch", "Cell alignment within the track."),
        ),
        "GridItem uses presentation markers for CSP-safe placement without inline style.",
        "Keep reading order sensible when spans change the visual grid.",
        "Do not invent arbitrary CSS track names outside the supported token set.",
    ),
    ComponentDoc(
        "Divider",
        "layout",
        "Separate adjacent groups with a semantic horizontal or vertical rule.",
        "Divider(orientation='horizontal')",
        "Inline(Text('Overview'), Divider('vertical'), Text('Activity'))",
        (p("orientation", "'horizontal' | 'vertical'", "Separator direction."),),
        "A horizontal divider emits `<hr>`. A vertical divider emits an element with `role=separator` and `aria-orientation=vertical`, allowing the theme to size it for inline layouts.",
        "Use a divider only when the grouping is not already obvious from headings or whitespace.",
        "A vertical separator needs a layout that gives it visible height.",
    ),
    ComponentDoc(
        "Heading",
        "content",
        "Create an explicit heading level without inferring document hierarchy.",
        "Heading(content='', *, level=2)",
        "Heading('Deployment history', level=2)",
        (
            p("content", "str", "Escaped heading text."),
            p("level", "1 | 2 | 3 | 4 | 5 | 6", "Exact native heading level."),
        ),
        "The requested level maps directly to `h1` through `h6`. Hedron does not guess levels because reusable components need their caller to own document structure.",
        "Do not skip levels merely for appearance; style headings with CSS and preserve a logical outline.",
        "A page should generally have one descriptive level-one heading.",
    ),
    ComponentDoc(
        "Text",
        "content",
        "Render escaped text with an explicit paragraph or inline text element.",
        "Text(content='', *, as_='p')",
        "Stack(Text('Changes saved.'), Text('Updated now', as_='small'))",
        (
            p("content", "str", "Escaped text content."),
            p("as_", "p | span | strong | em | small", "Exact permitted native text element."),
        ),
        "Text defaults to a paragraph and can render a span, strong, emphasis, or small element when those semantics are intentional. Content is serialized as text, so HTML-looking user input is displayed rather than executed.",
        "Choose `strong` and `em` for meaning rather than appearance, and use real list, heading, label, and link components when those semantics apply.",
        "Do not use a collection of spans to imitate a paragraph or use `strong` merely to obtain bold styling.",
    ),
    ComponentDoc(
        "Link",
        "content",
        "Navigate with a validated internal or external anchor.",
        "Link(label, href, *, external=False)",
        "Link('View audit log', '/audit')",
        (
            p("label", "str", "Visible link text."),
            p("href", "SafeUrl | str", "Validated navigation URL."),
            p("external", "bool", "Allow an external URL and open it defensively in a new tab."),
        ),
        "URLs pass through Hedron's SafeUrl navigation policy. External links receive `target=_blank` and `rel=noopener noreferrer`; internal links remain ordinary same-context anchors and work without JavaScript.",
        "Link text should identify the destination out of context; tell users when a destination opens a different site or context if that is not obvious.",
        "Use LinkButton only for a navigation link that is intentionally styled like a button—do not turn a command into a fake link.",
    ),
    ComponentDoc(
        "HtmxLink",
        "controls",
        "Navigate with a SafeUrl href and typed HTMX attributes for in-shell swaps.",
        "HtmxLink(label, href, *, method='get', target=None, swap='outerHTML', select=None, select_oob=None, push_url=False, preload=None, active=False, class_=None)",
        "HtmxLink('Reports', '/reports', target='#main-panel', swap='innerHTML', select='#main-panel')",
        (
            p("label", "str", "Visible link text."),
            p("href", "SafeUrl | str", "Validated navigation URL (also the no-JS fallback)."),
            p("method", "str", "HTMX verb mapped to hx-get / hx-post / … (default get)."),
            p(
                "target / swap",
                "str | None",
                "Approved hx-target and hx-swap for the primary region.",
            ),
            p(
                "select",
                "str | None",
                "Optional hx-select for the primary fragment in the response.",
            ),
            p(
                "select_oob",
                "str | None",
                "Optional hx-select-oob for response nodes that should be treated as OOB. "
                "Do not combine with a server OobUpdate for the same id.",
            ),
            p("push_url", "bool | str", "Optional hx-push-url for in-shell history."),
            p(
                "preload",
                "str | None",
                "Optional GET-only HTMX preload initiation: mousedown, mouseover, or touchstart. "
                "Registers the preload extension; never a compatibility default.",
            ),
            p("active", "bool", "Optional active styling hook for current location."),
            p("class_", "str | None", "Additional CSS classes."),
        ),
        "HtmxLink keeps ordinary anchor navigation as the progressive-enhancement path while attaching typed HTMX attrs. "
        "`select` / `select_oob` pull nodes from the response; server `OobUpdate` emits `hx-swap-oob` envelopes. "
        "Use one OOB mechanism per target—prefer explicit `OobUpdate(..., swap='innerHTML')` and omit matching `select_oob` "
        "so semantic shell hosts (for example `<nav aria-label=...>`) keep their tag and accessible name.",
        "Prefer descriptive labels and stable region ids for `target`. Keep CSRF and region authorization on the receiving action.",
        "Do not set `select_oob` for an id that the same navigation flow also updates via `OobUpdate`—that combination can replace landmark hosts with Hedron's OOB wrapper. "
        "Do not use HtmxLink for mutating form posts that belong on Button or Form; it is navigation-first.",
    ),
    ComponentDoc(
        "NavLink",
        "controls",
        "Alias of HtmxLink for navigation lists and AppShell side nav.",
        "NavLink(label, href, *, method='get', target=None, swap='outerHTML', select=None, select_oob=None, push_url=False, active=False, class_=None)",
        "NavLink('Home', '/', target='#main-panel', swap='innerHTML', active=True)",
        (p("…", "same as HtmxLink", "NavLink is the same component class as HtmxLink."),),
        "NavLink is an intentional DX alias of HtmxLink so shell navigation reads clearly under Nav / AppShell. Behavior, allowlists, and SafeUrl policy are identical—including the one-OOB-mechanism-per-target rule for `select_oob` vs `OobUpdate`.",
        "Use NavLink in primary navigation; use Link for ordinary content links without HTMX shell targets.",
        "Do not register both names as separate plugins—only one component class exists. "
        "Do not combine NavLink `select_oob` with a matching `OobUpdate` for the same shell host id.",
    ),
    ComponentDoc(
        "Brand",
        "utilities",
        "Product mark for AppShell chrome without application CSS.",
        "Brand(name, *, href=None, mark=None, id=None, class_=None)",
        "Brand('Hedron', href='/')",
        (
            p("name", "str", "Product or workspace name."),
            p("href", "SafeUrl | str | None", "Optional home navigation target."),
            p("mark", "NodeLike | None", "Optional logo/mark slot."),
        ),
        "Brand emits a typed chrome mark with first-party presentation markers.",
        "Keep brand text readable when an image mark is present.",
        "Do not style Brand with application CSS; use presentation tokens.",
    ),
    ComponentDoc(
        "AccountSummary",
        "utilities",
        "Compact signed-in account summary for shell chrome.",
        "AccountSummary(name, *, detail=None, href=None, id=None, class_=None)",
        "AccountSummary('Ada Lovelace', detail='Admin', href='/account')",
        (
            p("name", "str", "Display name."),
            p("detail", "str | None", "Optional role or email line."),
            p("href", "SafeUrl | str | None", "Optional account destination."),
        ),
        "AccountSummary is a compact chrome identity strip, not a full profile page.",
        "Pair with Avatar/Identity when a face mark is required.",
        "Do not nest interactive controls inside the summary link.",
    ),
    ComponentDoc(
        "EnvironmentBanner",
        "utilities",
        "Non-production environment banner for shell chrome.",
        "EnvironmentBanner(label, *, tone='warning', id=None, class_=None)",
        "EnvironmentBanner('Staging', tone='warning')",
        (
            p("label", "str", "Environment label shown to operators."),
            p("tone", "info | warning | danger", "Semantic urgency token."),
        ),
        "EnvironmentBanner keeps staging/canary honesty visible without custom CSS.",
        "Prefer warning for non-prod and danger for break-glass hosts.",
        "Do not use this banner for ordinary product marketing copy.",
    ),
    ComponentDoc(
        "NavStatus",
        "utilities",
        "Compact navigation status chip for shell sidebars.",
        "NavStatus(label, *, tone='neutral', id=None, class_=None)",
        "NavStatus('3 updates', tone='info')",
        (
            p("label", "str", "Status text."),
            p("tone", "neutral | info | success | warning | danger", "Semantic tone."),
        ),
        "NavStatus is a chrome status marker for nav regions.",
        "Keep labels short so the chip remains scannable.",
        "Do not use NavStatus as a live region for assertive errors.",
    ),
    ComponentDoc(
        "AppFooter",
        "utilities",
        "Typed application footer region for AppShell chrome.",
        "AppFooter(*nodes, *, width=None, id=None, class_=None)",
        "AppFooter(Text('© Acme'), Text('Support'))",
        (
            p("nodes", "NodeLike", "Footer body content."),
            p("width", "content | narrow | wide | full | None", "Optional content width token."),
        ),
        "AppFooter provides a presentation-token footer without application CSS.",
        "Keep legal and support links keyboard-reachable.",
        "Do not place primary navigation exclusively in the footer.",
    ),
    ComponentDoc(
        "OobHost",
        "interaction",
        "Stable out-of-band swap root with a reserved id.",
        "OobHost(*nodes, *, id, tag='div', class_=None)",
        "OobHost(Toast('Saved'), id='toast-host')",
        (
            p("id", "str", "Required stable element id for OOB targeting."),
            p("tag", "str", "Host element tag (default div)."),
            p("class_", "str | None", "Optional CSS classes."),
        ),
        "OobHost reserves a predictable DOM root for `oob_swap` updates. Pair with authorize_oob_update and reserved-id rules so fragments cannot target arbitrary selectors.",
        "Give each OOB host a unique page-local id and keep toast/status regions outside MainPanel when they must survive panel swaps.",
        "Do not reuse an OobHost id for ordinary fragment regions.",
    ),
    ComponentDoc(
        "AttrHost",
        "interaction",
        "Stable element that can receive attribute-only OOB updates.",
        "AttrHost(*nodes, *, id, tag='div', attrs=None, class_=None)",
        "AttrHost(Text('Ready'), id='status-host', attrs={'data-state': 'idle'})",
        (
            p("id", "str", "Required stable element id."),
            p("attrs", "mapping | None", "Initial attributes eligible for attr OOB patches."),
            p("tag / class_", "str", "Host element and optional classes."),
        ),
        "AttrHost is the companion to OobHost for attribute swaps (for example busy/disabled flags) without replacing the whole subtree.",
        "Keep attribute names on an allowlist and authorize updates the same way as content OOB.",
        "Do not treat AttrHost as a general DOM mutation API.",
    ),
    ComponentDoc(
        "SseRegion",
        "interaction",
        "Typed SSE host that registers the sse extension and connects to a same-origin stream.",
        "SseRegion(*children, *, connect, swap='message', close=None, id=None, class_=None)",
        "SseRegion(Text('Connecting…'), connect='/jobs/status', swap='message', close='done')",
        (
            p("connect", "SafeUrl | str", "Same-origin SSE endpoint (sse-connect)."),
            p("swap", "str", "Closed sse-swap event token (default message)."),
            p("close", "str | None", "Optional sse-close event that tears the stream down."),
            p("id / class_", "str | None", "Host element identity."),
        ),
        "SseRegion wraps existing experimental SSE helpers with a demand-driven `sse` asset. Polling remains the Supported production fallback; do not treat this region as a correctness path.",
        "Keep a meaningful fallback child for no-JS and failed reconnect. Pair job streams with a Poll region on the same status.",
        "Do not point connect at user-derived or external URLs. Empty Page.htmx_extensions with SseRegion fails closed (HED-EXT-0004).",
        package="hedron",
    ),
    ComponentDoc(
        "SseTrigger",
        "interaction",
        "Listen for a named SSE event and optionally issue a cacheable GET swap.",
        "SseTrigger(*children, *, event, href=None, target=None, swap=None)",
        "SseTrigger(Text('Waiting'), event='job-status', href='/jobs/panel', target='#job')",
        (
            p("event", "str", "Closed sse-swap / sse: event token."),
            p("href", "SafeUrl | str | None", "Optional same-origin GET issued on the event."),
            p("target / swap", "str | None", "Optional hx-target and hx-swap for the GET."),
        ),
        "SseTrigger emits `hx-trigger=\"sse:<event>\"` and registers the sse extension. It does not promote live transport to Supported.",
        "Announce resulting fragment swaps through existing live regions rather than inventing extra polite noise.",
        "Do not use SseTrigger for mutating methods. Prefer Poll when the stream is unavailable.",
        package="hedron",
    ),
    ComponentDoc(
        "MainPanel",
        "layout",
        "Primary HTMX swap region for AppShell document/fragment dual paths.",
        "MainPanel(*nodes, *, id='main-panel', class_=None)",
        "MainPanel(Heading('Dashboard', level=1), Text('Overview'), id='main-panel')",
        (
            p("id", "str", "Stable region id targeted by NavLink/HtmxLink swaps."),
            p("class_", "str | None", "Optional CSS classes."),
        ),
        "MainPanel is the body region AppShell composes for full-document and fragment responses. Keep navigable content here so shell chrome remains stable across swaps.",
        "Authorize the panel id in fragment_regions / InteractionPolicy for HTMX targets.",
        "Do not nest multiple competing main panels on one page.",
    ),
    ComponentDoc(
        "AppShell",
        "layout",
        "Document shell with optional side nav and a MainPanel body.",
        "AppShell(*body, *, nav=None, nav_groups=None, panel_id='main-panel', class_=None, id=None)",
        "AppShell(Heading('Home', level=1), nav=Nav(NavGroup('Workspace', NavLink('Home', '/'), NavLink('Reports', '/reports'))), panel_id='main-panel')",
        (
            p("body", "NodeLike", "Primary content placed inside MainPanel."),
            p("nav", "NodeLike | None", "Optional side navigation (often Nav of NavLinks)."),
            p("nav_groups", "Mapping[str, Sequence[NodeLike]] | Sequence[tuple[str, Sequence[NodeLike]]] | None", "Ordered grouped navigation lowered through `NavGroup`."),
            p("panel_id", "str", "Id forwarded to the composed MainPanel."),
        ),
        "AppShell composes landmark-friendly chrome with a swappable MainPanel so full page loads and HTMX fragment swaps share one layout. "
        "Use HtmxLink/NavLink targeting the panel id for the primary swap. When side chrome must update too, return an explicit "
        "`OobUpdate(element_id=..., swap='innerHTML')` and do **not** also set `select_oob` for that same id—"
        "`hx-select-oob` selects response nodes for OOB handling, while `OobUpdate` already emits `hx-swap-oob`.",
        "Keep global chrome outside MainPanel; put page-specific content inside the body slot. "
        "Prefer one OOB mechanism per target so `<nav>` / landmark hosts keep their tag and `aria-*` attributes.",
        "Do not use AppShell as a generic card or modal wrapper. "
        "Do not combine `select_oob='#side-nav'` with `OobUpdate(element_id='side-nav')` on the same navigation flow.",
    ),
    ComponentDoc(
        "SkipLink",
        "layout",
        "Keyboard bypass link to the shell main panel.",
        "SkipLink(target='#main-panel', *, label='Skip to main content', id=None, class_=None)",
        "SkipLink(target='#main-panel')",
        (
            p("target", "SafeUrl | str", "Same-document fragment such as `#main-panel`."),
            p("label", "str", "Discernible link text for assistive technology."),
        ),
        "SkipLink is styled by the default theme so authors never write CSS for the focusable bypass control.",
        "Place SkipLink as the first focusable element in the document and point it at AppShell's panel id.",
        "Do not use an external URL or an empty fragment as the target.",
    ),
    ComponentDoc(
        "RequestIndicator",
        "interaction",
        "Polite HTMX busy indicator with theme-owned placement.",
        "RequestIndicator(label='Loading…', *, placement='inline', visible_label=True, id=None, class_=None)",
        "RequestIndicator(label='Saving…', placement='top', id='save-indicator')",
        (
            p("label", "str", "Busy-state text announced to assistive technology."),
            p("placement", "inline | top | bottom", "Closed placement vocabulary."),
            p("visible_label", "bool", "When false, keep the label visually hidden but announced."),
        ),
        "RequestIndicator carries HTMX's `htmx-indicator` class and a polite live region so busy state is never color-only.",
        "Reference the indicator id from HTMX controls via `indicator='#…'`.",
        "Do not invent custom spinner CSS; use placement and the default theme.",
    ),
    ComponentDoc(
        "ProcessFlow",
        "layout",
        "Accessible ordered workflow rendered as a process list.",
        "ProcessFlow(*steps, *, label, direction='horizontal', collapse='md', id=None, class_=None)",
        "ProcessFlow(FlowStep('Ingest', status='complete'), FlowStep('Validate', status='current'), FlowStep('Publish'), label='Release pipeline')",
        (
            p("steps", "FlowStep", "Ordered FlowStep children."),
            p("label", "str", "Accessible name for the process list."),
            p("direction", "horizontal | vertical", "Closed layout direction."),
            p("collapse", "never | sm | md | lg", "Breakpoint where horizontal flows stack."),
        ),
        "ProcessFlow owns spacing and collapse through the default theme and requires FlowStep status text so state is never color-only.",
        "Keep one ProcessFlow per operational workflow and update step status from the server.",
        "Do not use ProcessFlow for primary navigation—use Nav / NavLink.",
    ),
    ComponentDoc(
        "FlowStep",
        "layout",
        "One stage of a ProcessFlow with explicit status text.",
        "FlowStep(label, *nodes, *, status='pending', description=None, status_text=None, id=None, class_=None)",
        "FlowStep('Validate schemas', status='current', description='Checking required columns')",
        (
            p("label", "str", "Discernible step name."),
            p("status", "complete | current | pending | blocked | skipped", "Closed status vocabulary."),
            p("description", "str | None", "Optional supporting copy."),
            p("status_text", "str | None", "Optional override for the default status phrase."),
        ),
        "Each FlowStep renders a textual status so progress is understandable without color perception.",
        "Mark exactly one step `current` unless the flow is idle or complete.",
        "Do not communicate status with icons alone; keep the status text.",
    ),
    ComponentDoc(
        "ConnectorNode",
        "layout",
        "Provider-neutral source or destination node for data-movement workflows.",
        "ConnectorNode(label, *nodes, children=None, kind='source', state='ready', detail=None, runtime=None, leading=None, id=None, class_=None)",
        "ConnectorNode('Warehouse', kind='target', state='ready', detail='Destination', runtime='Postgres')",
        (
            p("label", "str", "Discernible source or destination name."),
            p("nodes / children", "NodeLike", "Optional metadata content rendered inside the node."),
            p("kind", "source | target", "Connector role in the workflow."),
            p("state", "ready | blocked | running | succeeded | failed", "Explicit operational state."),
            p("detail / runtime", "str | None", "Supporting context such as object or runtime."),
            p("leading", "NodeLike | None", "Optional provider mark or identity content."),
        ),
        "ConnectorNode owns provider-neutral semantic markers and the baseline responsive node treatment. Applications supply provider identity and metadata as content, so workflow styling does not depend on private application selectors.",
        "Keep the label and state text visible; state is never communicated by color alone.",
        "Do not encode a provider name into the component type or replace the state text with an icon-only indicator.",
    ),
    ComponentDoc(
        "ConnectorFlow",
        "layout",
        "Responsive connector canvas for source, track, and destination workflow nodes.",
        "ConnectorFlow(*nodes, children=None, direction='horizontal', collapse='md', id=None, class_=None)",
        "ConnectorFlow(ConnectorNode('CSV', kind='source'), ConnectorTrack(label='Transfer'), ConnectorNode('Warehouse', kind='target'), direction='horizontal')",
        (
            p("nodes / children", "NodeLike", "ConnectorNode and ConnectorTrack children in reading order."),
            p("direction", "horizontal | vertical", "Primary flow orientation."),
            p("collapse", "never | sm | md | lg", "Breakpoint where a horizontal flow stacks."),
        ),
        "ConnectorFlow provides a responsive, semantic canvas while preserving source order for fallback and reduced-motion rendering. It reuses the process-flow layout contract so applications do not need bespoke connector CSS.",
        "Choose an orientation that remains understandable when the flow collapses, and keep node state text in each node.",
        "Do not use ConnectorFlow as primary navigation or rely on JavaScript to make the workflow legible.",
    ),
    ComponentDoc(
        "ConnectorTrack",
        "layout",
        "Accessible visual link between provider-neutral workflow nodes.",
        "ConnectorTrack(*nodes, children=None, active=False, label=None, id=None, class_=None)",
        "ConnectorTrack(Text('TLS 1.3 · Encrypted in transit'), label='Transfer stages', active=True)",
        (
            p("nodes / children", "NodeLike", "Track annotation or process content."),
            p("active", "bool", "Opt-in active motion hook; the static track remains present."),
            p("label", "str | None", "Accessible label for the track when needed."),
        ),
        "ConnectorTrack keeps the line and annotations useful without motion. Active animation is progressive enhancement and is disabled under reduced-motion preferences.",
        "Give the track a concise label when its annotation is not otherwise clear from the adjacent nodes.",
        "Do not make the animated state the only indication that a transfer is running.",
    ),
    ComponentDoc(
        "Image",
        "content",
        "Render an image with a validated source and required alternative text.",
        "Image(src, *, alt, width=None, height=None, allow_external=False)",
        "Image('/static/team.jpg', alt='The platform team at the 2026 meetup', width=960, height=540)",
        (
            p("src", "SafeUrl | str", "Validated asset URL."),
            p(
                "alt",
                "str",
                "Required text alternative; use an empty string for decorative images.",
            ),
            p("width / height", "int | None", "Intrinsic dimensions to reduce layout shift."),
            p("allow_external", "bool", "Permit a validated external asset origin."),
        ),
        "Image applies the SafeUrl asset policy and always writes the supplied alternative. Supplying intrinsic dimensions lets the browser reserve space before the asset arrives. Loading strategy is not a constructor option on this built-in.",
        "Describe the image's purpose in context; use `alt=''` only when nearby content already conveys everything.",
        "Do not enable external assets casually: review privacy, CSP, availability, and tracking implications.",
    ),
    ComponentDoc(
        "CodeBlock",
        "content",
        "Display escaped preformatted code with an optional language hook.",
        "CodeBlock(code, *, language=None)",
        "CodeBlock(\"from hedron import Text\\nText('Hello')\", language='python')",
        (
            p("code", "str", "Literal code to display."),
            p("language", "str | None", "Language class for a highlighter."),
        ),
        "The output is a `pre` containing `code`; the language becomes a class hook but syntax highlighting is an asset-layer concern. Code is escaped, never interpreted as markup.",
        "Keep long lines scrollable and introduce large examples with prose describing their purpose.",
        "Do not pass secrets, tokens, or unredacted production payloads into documentation code blocks.",
    ),
    ComponentDoc(
        "List",
        "content",
        "Render ordered or unordered items from child values.",
        "List(*items, ordered=False)",
        "List('Create a branch', 'Add the component', 'Run checks', ordered=True)",
        (
            p("items", "NodeLike", "Values wrapped in list items."),
            p("ordered", "bool", "Use `<ol>` when sequence matters."),
        ),
        "Each supplied item becomes one native `li` inside `ul` or `ol`. Nested structure should be built explicitly so list hierarchy remains inspectable.",
        "Choose ordered lists only when changing the sequence changes the meaning.",
        "Do not type bullet characters into Text; use List so assistive technology receives list semantics.",
    ),
    ComponentDoc(
        "DescriptionList",
        "content",
        "Present term/value pairs as a native description list.",
        "DescriptionList(*pairs)",
        "DescriptionList(('Region', 'us-east-1'), ('Status', Badge('Healthy', tone='success')))",
        (p("pairs", "tuple[NodeLike, NodeLike]", "Term and description pairs."),),
        "Every pair becomes a `dt` followed by a `dd`. Values can be components, which makes the component useful for metadata, summaries, and key/value inspection.",
        "Terms should be concise and values should make sense when announced immediately after their term.",
        "Use Table instead when rows share column headers or users need to compare several records.",
    ),
    ComponentDoc(
        "Table",
        "content",
        "Render a small static data table with explicit headers.",
        "Table(headers, rows, *, caption=None)",
        "Table(['Service', 'Status'], [['API', 'Healthy'], ['Worker', 'Healthy']], caption='Service health')",
        (
            p("headers", "Sequence[str]", "Column headings."),
            p("rows", "Sequence[Sequence[NodeLike]]", "Rows matching the header count."),
            p("caption", "str | None", "Accessible table name and context."),
        ),
        "The component emits a native table, optional caption, a header row using column-scoped header cells, and a body. It is intentionally static; use DataTable for paging and larger datasets.",
        "Add a concise caption when surrounding prose does not already identify the table.",
        "Keep every row the same width as the headers; do not use a table only for visual alignment.",
    ),
    ComponentDoc(
        "Markdown",
        "content",
        "Render Markdown through the optional, escaped content pipeline.",
        "Markdown(source)",
        'Markdown("## Release notes\\n\\n- Safer URLs\\n- Faster rendering")',
        (p("source", "str", "Markdown source text."),),
        "Markdown uses the optional markdown dependency and returns reviewed rendered output. Raw HTML handling and sanitization are governed by the content pipeline; it is not a shortcut around TrustedHtml.",
        "Authors still own heading hierarchy, meaningful link text, table captions, and image alternatives in the source.",
        "Install `hedron[markdown]` and never assume arbitrary embedded HTML is trusted.",
        package="hedron[markdown]",
    ),
    ComponentDoc(
        "Card",
        "surfaces",
        "Group a titled piece of related content in a styled surface.",
        "Card(*nodes, children=None, title=None, header=None, footer=None, id=None, class_=None)",
        "Card(Text('Build completed in 42 seconds.'), title='Latest deployment', footer=Link('View logs', '/logs'))",
        (
            p("nodes", "NodeLike", "Positional card body content."),
            p(
                "children",
                "NodeLike | sequence | None",
                "Keyword body content; combines with positional nodes.",
            ),
            p(
                "title",
                "str | None",
                "Convenience title rendered as an `h3` when no header slot is supplied.",
            ),
            p("header", "NodeLike | None", "Custom header slot; takes precedence over title."),
            p("footer", "NodeLike | None", "Actions or supporting content."),
            p("id", "str | None", "Stable ID when the complete card is a swap target."),
            p("class_", "str | None", "Application class appended to `hedron-card`."),
        ),
        "Card emits an addressable article with distinct header, body, and optional footer wrappers. The convenience `title` becomes an h3; use the `header` slot when the surrounding document requires another heading level or richer content. Its body accepts ordinary nested components, including layouts and forms, through the same renderer pipeline.",
        "Choose a custom Heading in `header` when an automatic h3 would skip or repeat levels.",
        "Do not make an entire complex card clickable when it contains other interactive controls.",
    ),
    ComponentDoc(
        "Surface",
        "surfaces",
        "Compose a presentation-token surface without application CSS.",
        "Surface(*nodes, *, elevation='plain', padding='md', shape='rounded', width=None, id=None, class_=None)",
        "Surface(Text('Workspace body'), elevation='raised', padding='lg')",
        (
            p("nodes", "NodeLike", "Surface body content."),
            p("elevation", "plain | raised", "Named elevation token."),
            p("padding", "none | xs | sm | md | lg | xl", "Named padding token."),
            p("shape", "square | rounded | pill", "Named shape token."),
            p("width", "content | narrow | wide | full | None", "Optional width token."),
        ),
        "Surface is the zero-application-CSS building block for panels. Presentation is marker-driven (`data-hedron-*`) and styled by first-party CSS.",
        "Prefer Surface over ad-hoc div wrappers when you need a raised or padded region.",
        "Do not pass inline style or arbitrary CSS lengths; use the named token vocabularies.",
    ),
    ComponentDoc(
        "StyleScope",
        "surfaces",
        "Bound a subtree to theme, finite variant, color mode, and density markers only.",
        "StyleScope(*nodes, *, theme=None, color_mode=None, density=None, variant=None, id=None, class_=None, mark=None)",
        "StyleScope(Text('Scoped panel'), theme='aurora', variant='dense', color_mode='dark', density='compact')",
        (
            p("nodes", "NodeLike", "StyleScope body content."),
            p("theme", "str | None", "Optional registered theme name emitted as `data-hedron-theme`."),
            p("variant", "str | None", "Optional finite registered variant emitted as `data-hedron-variant`. Unknown names fail closed."),
            p("color_mode", "light | dark | None", "Optional color-mode marker (`data-hedron-color-mode`)."),
            p("density", "compact | comfortable | spacious | None", "Optional density marker (`data-hedron-density`)."),
        ),
        "StyleScope is a visible boundary for theme, finite variant, color mode, and density only. Presentation is marker-driven (`data-hedron-*`) and styled by first-party CSS; recipe defaults are rejected.",
        "Prefer StyleScope when a region must override theme, finite variant, color mode, or density without application CSS.",
        "Do not pass recipe defaults or arbitrary CSS; only theme, finite variant, color_mode, and density are supported.",
    ),
    ComponentDoc(
        "Badge",
        "surfaces",
        "Display compact categorical metadata with a named tone.",
        "Badge(text, *, tone='neutral')",
        "Inline(Badge('Beta', tone='info'), Badge('Healthy', tone='success'))",
        (
            p("text", "str", "Short badge label."),
            p("tone", "neutral | info | success | warning | danger", "Semantic styling token."),
        ),
        "Badge emits visible text and a tone data attribute for theming. Tones are finite so products can keep color usage consistent.",
        "The text must carry the meaning; tone color is supplementary.",
        "Do not use a badge as a live announcement or interactive control.",
    ),
    ComponentDoc(
        "Alert",
        "surfaces",
        "Present an important text message using an appropriate live-region policy.",
        "Alert(message, *, tone='info', title=None)",
        "Alert('Your changes were saved.', tone='success', title='Saved')",
        (
            p("message", "str", "Escaped alert text."),
            p("tone", "info | success | warning | danger", "Visual and semantic urgency."),
            p("title", "str | None", "Optional concise heading text."),
        ),
        "Alerts group an optional strong title and escaped message with tone styling. Danger messaging uses alert semantics; lower-urgency messages use status semantics to avoid unnecessary interruption.",
        "Reserve assertive alerts for errors requiring immediate attention and move focus only when the next action would otherwise be unclear.",
        "Alert accepts text, not arbitrary child components; compose a custom semantic region when the message needs structured controls.",
    ),
    ComponentDoc(
        "Skeleton",
        "surfaces",
        "Reserve space for content that is still loading.",
        "Skeleton(*, lines=3)",
        "Skeleton(lines=4)",
        (p("lines", "int", "Number of presentation-only placeholder rows."),),
        "Skeleton emits the requested placeholder lines, hides each line from the accessibility tree, and marks the wrapper busy. Pair it with a separate status message or the Loading component when users need progress context.",
        "Because the visual lines are hidden semantically, provide an adjacent live status for meaningful waits.",
        "Validate `lines` in application configuration; zero or negative values produce an empty busy wrapper rather than a useful placeholder.",
    ),
    ComponentDoc(
        "StateView",
        "surfaces",
        "Unified loading, empty, error, permission, offline, and success surface.",
        "StateView(title, *nodes, *, kind='empty', description=None, detail=None, actions=None, id=None, class_=None)",
        "StateView('No pipelines yet', kind='empty', description='Create a pipeline to start ingesting data.', actions=Button('New pipeline'))",
        (
            p("title", "str", "Primary message for the state."),
            p("kind", "loading | empty | error | permission | offline | success", "Closed state vocabulary."),
            p("description / detail", "str | None", "Optional supporting copy."),
            p("actions", "NodeLike | None", "Optional recovery or next-step controls."),
        ),
        "StateView chooses an appropriate live-region role and always shows a textual kind label so state is never color- or icon-only.",
        "Prefer StateView for empty tables, failed loads, and permission blocks instead of ad-hoc cards.",
        "Do not use StateView for ordinary inline validation—use FormErrors or Alert.",
    ),
    ComponentDoc(
        "Typography",
        "content",
        "Role-first text helper bound to the type scale.",
        "Typography(content, *, role='body', as_='p', class_=None)",
        "Typography('Release readiness', role='title')",
        (
            p("content", "str", "Escaped text content."),
            p("role", "str", "Closed typography role from the theme scale."),
            p("as_", "p | span | div | strong | em | small | code", "Native element to emit."),
        ),
        "Typography maps author intent (role) to theme CSS classes without requiring application type CSS.",
        "Use Heading for document outline levels; use Typography for scale-driven body, caption, and title text.",
        "Do not invent CSS font sizes for product chrome—pick a role.",
    ),
    ComponentDoc(
        "Icon",
        "content",
        "Trusted registry SVG with a bounded size vocabulary.",
        "Icon(name, *, size='md', title=None, decorative=False, id=None, class_=None)",
        "Icon('check', size='sm', title='Complete')",
        (
            p("name", "str", "Registered icon name from the trusted registry."),
            p("size", "str", "Closed size vocabulary (`sm` / `md` / `lg` / …)."),
            p("title", "str | None", "Accessible name override when not decorative."),
            p("decorative", "bool", "When true, hide the icon from the accessibility tree."),
        ),
        "Icon fails closed on unknown names and never accepts raw SVG markup from application authors.",
        "Prefer decorative=True beside visible text; otherwise supply a title that names the meaning.",
        "Do not use Icon as a button—use IconButton for actionable controls.",
    ),
    ComponentDoc(
        "Button",
        "controls",
        "Trigger an in-page or server command with a native button.",
        "Button(label, *, type='button', disabled=False, variant='primary', size=None, appearance=None, emphasis=None, width=None, leading_icon=None, id=None, class_=None, attrs=None)",
        "Button('Archive project', type='button', variant='danger', size='sm', width='full')",
        (
            p("label", "str", "Visible command label."),
            p("type", "button | submit | reset", "Native button behavior."),
            p("disabled", "bool", "Prevent activation."),
            p("variant", "primary | secondary | danger", "Finite semantic styling variant."),
            p("size", "sm | md | lg | None", "Shared control size marker."),
            p("appearance", "solid | outline | soft | ghost | plain | raised | None", "Treatment independent of meaning."),
            p("emphasis", "primary | secondary | danger | neutral | None", "Semantic meaning independent of treatment."),
            p("width", "content | field | full | None", "Shared width intent."),
            p("leading_icon", "str | None", "Optional registered icon name."),
            p("attrs", "Mapping[str, HtmlAttrValue] | None", "Validated global, ARIA, data, approved HTMX, and popover/dialog-trigger attributes."),
        ),
        "Button retains native keyboard activation and form behavior and maps the selected variant to stable theme markers. In 0.59, `size`, `appearance`, `emphasis`, and `width` share the presentation vocabulary, while `attrs=` provides a validated seam for integration attributes. Use a higher-level action binding when the command calls the server.",
        "Use a verb that states the result. Disabled controls need nearby explanation when the reason is not obvious.",
        "Use Link or LinkButton for navigation; a button should perform an action. `attrs=` does not allow `style`, `on*`, `hx-on*`, component-owned `type`/`disabled`/`id`/`class`, malformed ARIA/data names, or non-allowlisted HTMX attributes.",
        demo="button",
    ),
    ComponentDoc(
        "LinkButton",
        "controls",
        "Navigate with an anchor styled as a prominent button.",
        "LinkButton(label, href, *, size=None, width=None, appearance=None, emphasis=None, id=None, class_=None, attrs=None)",
        "LinkButton('Create account', '/signup', size='sm', width='full')",
        (
            p("label", "str", "Visible navigation label."),
            p("href", "SafeUrl | str", "Validated destination."),
            p("size", "sm | md | lg | None", "Shared control size marker."),
            p("width", "content | field | full | None", "Shared width intent."),
            p("appearance", "solid | outline | soft | ghost | plain | raised | None", "Treatment independent of meaning."),
            p("emphasis", "primary | secondary | danger | neutral | None", "Semantic meaning independent of treatment."),
            p("attrs", "Mapping[str, HtmlAttrValue] | None", "Validated global, ARIA, data, approved HTMX, and popover/dialog-trigger attributes."),
        ),
        "Despite its appearance, LinkButton is an anchor and preserves open-in-new-tab, copy-link, and no-JavaScript navigation behavior. Its 0.59 `size`, `width`, `appearance`, `emphasis`, and `attrs=` contract is aligned with `Button`.",
        "The label should describe the destination and focus styling must remain visible in the chosen theme.",
        "Never use LinkButton to submit a form or mutate data. Its `attrs=` seam remains validated and cannot override the owned destination or structural attributes.",
    ),
    ComponentDoc(
        "IconButton",
        "controls",
        "Create a compact native button with a required accessible label.",
        "IconButton(label, *, icon, type='button', disabled=False)",
        "IconButton('Delete report', icon='⌫')",
        (
            p("label", "str", "Required accessible name."),
            p("icon", "str", "Escaped visible icon or symbol, hidden from assistive technology."),
            p("type", "button | submit | reset", "Native behavior."),
            p("disabled", "bool", "Prevent activation."),
        ),
        "The icon string is rendered inside an aria-hidden span while `label` supplies the button's accessible name. Both values are escaped; this component does not resolve registered SVG names automatically.",
        "Make the hit target large enough and keep a tooltip supplementary—the label must exist without hover.",
        "Do not pass SVG markup as the icon string; use the reviewed icon registry in a custom control when a trusted SVG is required.",
    ),
    ComponentDoc(
        "Form",
        "forms",
        "Compose a native GET or POST form with validated action URLs and optional HTMX attributes.",
        "Form(*nodes, children=None, action=None, method='post', hx=None, **native_or_hx_attrs)",
        "Form(CsrfField(), FormField(name='email', label='Email', control=TextInput(name='email', type='email')), SubmitButton('Subscribe'), action='/subscribe')",
        (
            p("nodes", "NodeLike", "Positional labels, fields, errors, and controls."),
            p(
                "children",
                "NodeLike | sequence | None",
                "Keyword child list; combines with positional nodes.",
            ),
            p("action", "SafeUrl | str | None", "Validated form endpoint."),
            p("method", "'get' | 'post'", "Native submission method."),
            p("hx", "Hx | None", "Validated first-class HTMX options (FORM-022)."),
            p("**attrs", "Any", "Validated native or HTMX form attributes."),
        ),
        "Form is progressively enhanced: ordinary browser submission remains the baseline, while `hx-post`, targets, swaps, sync, and indicators can be added for fragment updates.",
        "Every control needs a label, errors must be associated with controls, and successful submission should produce a perceivable status.",
        "Server-side validation and CSRF checks remain mandatory even when the browser reports validity.",
        server="On submit",
        demo="form",
    ),
    ComponentDoc(
        "Hx",
        "forms",
        "First-class HTMX attribute bundle for Form (validated selectors and swap).",
        "Hx(*, target=None, swap='outerHTML', select=None, indicator=None, trigger=None, include=None, validate=None, busy=None, ...)",
        "Form(..., hx=Hx(target='#region', swap='outerHTML', indicator='#busy', busy='region'))",
        (
            p("target", "str | None", "hx-target selector (must pass safe_css_selector)."),
            p("swap", "str", "hx-swap value (must pass safe_hx_swap)."),
            p("select", "str | None", "hx-select selector."),
            p("indicator", "str | None", "hx-indicator selector; with `busy`, a simple #id also drives Hedron aria-busy indicator."),
            p("trigger", "str | None", "`hx-trigger`."),
            p("include", "str | None", "`hx-include`."),
            p("validate", "str | None", '`"native"` compiles `hx-validate="true"`.'),
            p("busy", "'region' | 'document' | None", "Opt-in Hedron busy host (`data-hedron-busy`); unmarked requests stay idle."),
            p("vals` / `headers", "str | None", "JSON only; `js:` expressions are rejected."),
        ),
        "Prefer `hx=Hx(...)` over raw `hx-*` kwargs so unsafe selectors cannot slip through. `busy=` is opt-in generic HTMX busy (#506); it does not mark `document.body` for unmarked requests.",
        "Selector validation is the security boundary; do not bypass with stringly kwargs.",
        "Raw kwargs that survive after Hx merge are still validated.",
        server="No",
        demo="static",
    ),
    ComponentDoc(
        "SwapReveal",
        "forms",
        "Opt-in HTMX after-swap reveal wrapper that respects prefers-reduced-motion.",
        "SwapReveal(*nodes, children=None, reduced_motion=True)",
        "SwapReveal(Text('Updated region'))",
        (
            p("nodes", "NodeLike", "Content revealed after an HTMX swap."),
            p("reduced_motion", "bool", "Honor prefers-reduced-motion (default True)."),
        ),
        "SwapReveal wraps a swapped region. First paint includes `is-revealed` so content is visible; Hedron UI replays the reveal class on `htmx:afterSwap` unless reduced motion is requested.",
        "Keep the wrapper around the swapped region so keyboard focus restoration stays in the same landmark.",
        "Do not use animation as the only status cue; pair with BusyRegion or aria-busy.",
        server="No",
        demo="static",
    ),
    ComponentDoc(
        "BusyRegion",
        "forms",
        "Generic HTMX busy host for region or document aria-busy and an optional indicator.",
        "BusyRegion(*nodes, children=None, scope='region', indicator=None)",
        "BusyRegion(Text('Results'), scope='region', indicator='#busy')",
        (
            p("nodes", "NodeLike", "Region content that becomes busy during HTMX requests."),
            p(
                "scope",
                "'region' | 'document'",
                "Whether aria-busy applies to the region or document.",
            ),
            p("indicator", "str | None", "Optional #id selector for a busy indicator element."),
        ),
        "BusyRegion and `Hx(busy=...)` mark opt-in HTMX busy hosts. Hedron UI sets aria-busy only on those hosts (document scope uses the document element), never on every request's body.",
        "Keep a visible or text status for busy; do not rely on color or motion alone.",
        "Indicator selectors must be simple #id tokens.",
        server="No",
        demo="static",
    ),
    ComponentDoc(
        "CsrfField",
        "forms",
        "Hidden CSRF input wired to the active strategy or an explicit token.",
        "CsrfField(*, name=None, token=None)",
        "CsrfField(token=csrf_token_for_request(request, policy))",
        (
            p(
                "name",
                "str | None",
                "Form field name; defaults to the strategy / RenderContext field.",
            ),
            p(
                "token",
                "str | None",
                "Token value; when omitted, uses RenderContext.csrf_token on FastAPI pages.",
            ),
        ),
        "Use inside Form for POST/HTMX mutations. Prefer explicit token= in portable/offline renders. Not for login CSRF — use LoginCsrfField.",
        "The field is aria-hidden by nature as a hidden input; pair with visible validation feedback on failure.",
        "Never log or display the token value in diagnostics.",
        server="On submit",
        demo="static",
    ),
    ComponentDoc(
        "LoginCsrfField",
        "forms",
        "Hidden input for pre-auth login CSRF (issue_login_csrf / validate_login_csrf).",
        "LoginCsrfField(*, token=None, session=None, name=None)",
        "LoginCsrfField(session=request.session)",
        (
            p("token", "str | None", "Explicit login CSRF token."),
            p("session", "MutableMapping | None", "Optional session store for issue_login_csrf."),
            p("name", "str | None", "Field name; defaults to hedron_login_csrf."),
        ),
        "Use on login forms only. Plain CsrfField embeds the post-auth strategy token and will not validate against the login CSRF store.",
        "Pair with validate_login_csrf on POST.",
        "Do not reuse login tokens after authentication succeeds.",
        server="On submit",
        demo="static",
    ),
    ComponentDoc(
        "FormField",
        "forms",
        "Bind a label, help text, required state, and field error to one control.",
        "FormField(*, name, label, control, id=None, help=None, required=False, error=None)",
        "FormField(name='email', label='Email address', control=TextInput('email', type='email'), help='We only use this for receipts.', required=True)",
        (
            p("name", "str", "Stable field key used to derive IDs."),
            p("label", "str", "Visible label."),
            p("control", "NodeLike", "Required control slot."),
            p(
                "id",
                "str | None",
                "Optional explicit control ID; otherwise a collision-free request-local ID is generated.",
            ),
            p("help", "str | None", "Associated instructions."),
            p("required", "bool", "Required state propagated to compatible controls."),
            p("error", "str | None", "Associated inline error."),
        ),
        "The component copies compatible controls before binding IDs and ARIA attributes, so shared component instances are not mutated. The bound component remains in the normal renderer tree and therefore keeps validation, identity tracking, diagnostics, and nesting behavior. Help and error nodes receive collision-free IDs and are connected with `aria-describedby`; pass `id=` when tests or external markup require a fixed value.",
        "Write errors as actionable corrections and keep instructions available before an error occurs.",
        "Use the same `name` on the field and its control; avoid hand-authoring conflicting IDs.",
    ),
    ComponentDoc(
        "Label",
        "forms",
        "Associate visible text with a form control ID.",
        "Label(text, *, for_=None)",
        "Label('Search projects', for_='project-search')",
        (
            p("text", "str", "Visible label."),
            p("for_", "str | None", "Target control ID; renders as `for`."),
        ),
        "`for_` uses the Python-safe spelling but serializes to the native `for` attribute. Prefer FormField when you also need help, required, or error binding.",
        "Labels should state what information to enter, not merely repeat a placeholder.",
        "A placeholder is not a replacement for Label because it disappears during entry.",
    ),
    ComponentDoc(
        "TextInput",
        "forms",
        "Collect a single line of typed text using a constrained input type.",
        "TextInput(name, *, id=None, value='', placeholder=None, required=False, type='text', autocomplete=None, disabled=False)",
        "TextInput('email', type='email', autocomplete='email', required=True)",
        (
            p("name", "str", "Submitted field name."),
            p("id", "str | None", "Control ID; defaults from name."),
            p("value", "str", "Current value for re-rendering."),
            p("placeholder", "str | None", "Optional hint."),
            p("required", "bool", "Native required constraint."),
            p(
                "type",
                "text | email | password | search | tel | url",
                "Constrained browser input mode.",
            ),
            p("autocomplete", "str | None", "Browser autofill token."),
            p("disabled", "bool", "Disable and omit from submission."),
        ),
        "TextInput uses native constraints and preserves a supplied value during validation re-renders. The finite type set avoids accidentally exposing unsafe or poorly supported input modes. `type='password'` renders an accessible Show/Hide control (`data-hedron-password-toggle`) with no app-authored JavaScript.",
        "Provide a Label or FormField and use an accurate autocomplete token to help keyboard and assistive-technology users.",
        "Never echo passwords back through `value`, and remember disabled controls are not submitted.",
    ),
    ComponentDoc(
        "TextArea",
        "forms",
        "Collect multi-line plain text.",
        "TextArea(name, *, id=None, value='', rows=4, required=False, placeholder=None)",
        "TextArea('notes', rows=6, placeholder='Add deployment context…')",
        (
            p("name", "str", "Submitted field name."),
            p("id", "str | None", "Control ID."),
            p("value", "str", "Text between the textarea tags."),
            p("rows", "int", "Initial visible row count."),
            p("required", "bool", "Native required constraint."),
            p("placeholder", "str | None", "Optional example or hint."),
        ),
        "The value is rendered as escaped text content, not as an HTML value attribute. Browsers retain native selection, resizing, and keyboard behavior.",
        "Use a visible label and explain format or length expectations before the control.",
        "Do not accept rich HTML through TextArea without a separate sanitization and trust pipeline.",
    ),
    ComponentDoc(
        "Select",
        "forms",
        "Choose one value from server-defined label/value options.",
        "Select(name, options, *, id=None, required=False, value=None, depends_on=None, source=None)",
        "Select('region', [('iad', 'US East'), ('fra', 'Europe')], value='iad')",
        (
            p("name", "str", "Submitted field name."),
            p("options", "Sequence[tuple[str, str]]", "Value/label pairs."),
            p("id", "str | None", "Control ID."),
            p("required", "bool", "Native required constraint."),
            p("value", "str | None", "Selected option value."),
            p(
                "depends_on",
                "str | None",
                "Parent field name; compiles `hx-trigger=\"change from:#field-{dom_id_part(name)}\"`.",
            ),
            p("source", "str | None", "Child `hx-get` fragment that synthesizes options."),
        ),
        "Options are explicit value/label pairs and the selected value is matched server-side during rendering. The result is a native single-select.",
        "Use meaningful option labels and include a non-value prompt option when no default is appropriate.",
        "Validate the submitted value against the authoritative server-side option set.",
    ),
    ComponentDoc(
        "Checkbox",
        "forms",
        "Collect one boolean choice with its visible label.",
        "Checkbox(name, label, *, id=None, checked=False, required=False)",
        "Checkbox('terms', 'I agree to the service terms', required=True)",
        (
            p("name", "str", "Submitted field name."),
            p("label", "str", "Visible label next to the box."),
            p("id", "str | None", "Control ID."),
            p("checked", "bool", "Current checked state."),
            p("required", "bool", "Require the box to be checked."),
        ),
        "Checkbox emits the input and its associated label in a wrapper. Unchecked HTML checkboxes submit no value, so the server model must define the false/default behavior.",
        "Use positive, unambiguous wording that makes the checked state clear.",
        "Do not use a single checkbox for mutually exclusive choices; use RadioGroup.",
    ),
    ComponentDoc(
        "RadioGroup",
        "forms",
        "Choose exactly one option from a labelled set.",
        "RadioGroup(name, legend, options, *, id=None, value=None, required=False)",
        "RadioGroup('plan', 'Billing plan', [('free', 'Free'), ('pro', 'Pro')], value='free')",
        (
            p("name", "str", "Shared submitted field name."),
            p("legend", "str", "Group label."),
            p("options", "Sequence[tuple[str, str]]", "Value/label pairs."),
            p(
                "id",
                "str | None",
                "Optional option-ID prefix; generated collision-free by default.",
            ),
            p("value", "str | None", "Selected option."),
            p("required", "bool", "Require one selection."),
        ),
        "A native fieldset and legend name the group; every option gets a collision-free ID, shared name, value, and associated label. Pass `id=` only when outside markup must use a predictable prefix.",
        "Keep option labels parallel and make the legend a complete question or category.",
        "Use Select when the option set is long or screen space is constrained.",
    ),
    ComponentDoc(
        "SubmitButton",
        "forms",
        "Submit the nearest form with consistent primary-action styling.",
        "SubmitButton(label='Submit', *, disabled=False)",
        "SubmitButton('Save profile')",
        (p("label", "str", "Visible submit action."), p("disabled", "bool", "Prevent submission.")),
        "The component fixes `type=submit`, avoiding the ambiguity of a generic button in a form, and applies the primary button class.",
        "Use a specific verb and expose pending state without replacing the accessible name with an unexplained spinner.",
        "Do not disable the only submit path permanently after an HTMX error.",
    ),
    ComponentDoc(
        "FormErrors",
        "forms",
        "Summarize one or more form-level validation errors.",
        "FormErrors(errors)",
        "FormErrors(['Email is required.', 'Choose a billing plan.'])",
        (p("errors", "Sequence[str]", "Ordered human-readable error messages."),),
        "An empty sequence renders nothing. Otherwise errors become a list inside an alert region so a failed response is announced.",
        "Put the summary before the fields and also attach each field-specific error with FormField.",
        "Do not include raw exception messages or sensitive submitted values.",
    ),
    ComponentDoc(
        "AutoForm",
        "forms",
        "Generate a labelled form from a typed FormModel and optionally submit it through HTMX.",
        "AutoForm(model, *, action, method='post', csrf_token=None, values=None, errors=(), submit_label='Submit', target=None)",
        "AutoForm(InviteMember, action='/invite', csrf_token=csrf_token, submit_label='Send invite')",
        (
            p("model", "type[FormModel] | FormModel", "Field schema or populated instance."),
            p("action", "SafeUrl | str", "Validated endpoint."),
            p("method", "str", "GET or POST behavior."),
            p(
                "csrf_token",
                "str | None",
                "Hidden CSRF value from `csrf_token_for_request`; required for POST.",
            ),
            p("values", "Mapping", "Values restored after validation."),
            p("errors", "Sequence[str]", "Form-level errors."),
            p("submit_label", "str", "Primary action label."),
            p(
                "target",
                "safe CSS selector | None",
                "HTMX response target (prefer explicit Form composition when using hx-target).",
            ),
        ),
        "AutoForm derives field labels and required state from model metadata, adds error and CSRF nodes, and uses normal form submission as its baseline. Obtain `csrf_token` with `csrf_token_for_request(request, policy)` after a safe GET. For HTMX-targeted POSTs, prefer the explicit Form loop in the [forms and actions guide](../guides/forms-and-actions.md).",
        "Review generated labels and add model titles that make domain-specific fields understandable.",
        "Generation does not replace authorization, CSRF validation, or server-side model validation. Do not leave `csrf_token` undefined.",
        server="On submit",
        demo="auto-form",
    ),
    ComponentDoc(
        "RefreshButton",
        "interaction",
        "Refresh a target component through a typed reference or safe URL.",
        "RefreshButton(label='Refresh', *, ref=None, href=None, target=None, swap='outerHTML')",
        "RefreshButton('Refresh status', href='/status', target='#status-card', swap='innerHTML')",
        (
            p("label", "str", "Visible command."),
            p("ref", "ComponentRef | None", "Preferred typed route reference."),
            p("href", "str | None", "Fallback GET URL."),
            p("target", "safe CSS selector | None", "Element to update."),
            p("swap", "str", "HTMX swap strategy."),
        ),
        "The rendered native button receives `hx-get`, target, and swap metadata. A ComponentRef also carries its method and typed query parameters. The docs demo intercepts the request and replaces the target locally.",
        "Announce refreshed content through a status or live region and keep keyboard focus stable unless the task changes.",
        "Do not accept user-controlled target selectors or refresh destructive endpoints with GET.",
        server="On activation",
        demo="refresh",
    ),
    ComponentDoc(
        "Lazy",
        "interaction",
        "Load a component fragment when its placeholder enters the document.",
        "Lazy(*, ref, placeholder=None, target_id=None, error=None)",
        "Lazy(ref=ComponentRef('activity-feed'), placeholder=Skeleton(lines=3), target_id='activity-feed')",
        (
            p("ref", "ComponentRef", "Typed fragment endpoint."),
            p("placeholder", "NodeLike | None", "Initial content; defaults to Loading."),
            p(
                "target_id",
                "str | None",
                "Explicit host ID; generated collision-free by default.",
            ),
            p(
                "error",
                "NodeLike | None",
                "Error template kept outside the inner `#…-body` swap target.",
            ),
        ),
        "Lazy emits a load-triggered HTMX request that swaps into an inner `#…-body` wrapper so a `template[data-hedron-error-template]` survives a successful load. `hedron-ui.mjs` (core and FastAPI copies, kept byte-identical) rematerializes the template on `htmx:responseError` / `htmx:sendError`.",
        "Choose a placeholder that reserves approximately the final space and provide meaningful loading text for material waits.",
        "Do not lazy-load content needed to understand or operate the initial page without a robust failure state.",
        server="Immediately after load",
        demo="lazy",
    ),
    ComponentDoc(
        "Poll",
        "interaction",
        "Refresh a fragment at a bounded interval while it remains in the DOM.",
        "Poll(*, ref, interval_ms=5000, target_id=None, content=None)",
        "Poll(ref=ComponentRef('job-status', job_id=job.id), interval_ms=2000, content=Status('Queued'))",
        (
            p("ref", "ComponentRef", "Typed polling endpoint."),
            p("interval_ms", "int", "Interval, clamped to at least 250 ms."),
            p(
                "target_id",
                "str | None",
                "Explicit self-target ID; generated collision-free by default.",
            ),
            p("content", "NodeLike | None", "Initial content."),
        ),
        "HTMX's `every Nms` trigger refreshes the component into its collision-free self-target. Repeated instances can share one ComponentRef safely. Stop polling by returning replacement markup without the polling attributes once the terminal state is reached.",
        "Announce only meaningful state transitions; announcing every timer tick overwhelms screen-reader users.",
        "Use conservative intervals, private caching where appropriate, and a terminal response that stops server load.",
        server="On every interval",
        demo="poll",
    ),
    ComponentDoc(
        "InfiniteScroll",
        "interaction",
        "Append the next fragment when a pagination sentinel is revealed.",
        "InfiniteScroll(*, ref, target, swap='beforeend')",
        "InfiniteScroll(ref=ComponentRef('next-events', page=2), target='#event-list')",
        (
            p("ref", "ComponentRef", "Typed next-page endpoint."),
            p("target", "safe CSS selector", "Collection receiving appended nodes."),
            p("swap", "str", "Usually `beforeend`."),
        ),
        "The sentinel uses HTMX's revealed trigger and appends to the selected collection. The response should contain new records plus the next sentinel, or omit the sentinel when no pages remain.",
        "Provide a visible Load more fallback and announce how many items were added without moving focus.",
        "Do not create an endless keyboard or screen-reader experience with no way to reach following page content.",
        server="When revealed",
        demo="infinite",
    ),
    ComponentDoc(
        "Pagination",
        "interaction",
        "Render crawlable page links that optionally swap a target through HTMX.",
        "Pagination(*, page, page_size, total, base_path, target=None)",
        "Pagination(page=2, page_size=25, total=93, base_path='/audit', target='#audit-table')",
        (
            p("page", "int", "Current one-based page."),
            p("page_size", "int", "Rows per page."),
            p("total", "int", "Total result count."),
            p("base_path", "str", "Safe base URL, with or without query parameters."),
            p("target", "safe CSS selector | None", "Optional HTMX target."),
        ),
        "Every page is a real safe anchor, so navigation works without HTMX. With a target, each link adds a GET request and innerHTML swap. Current-page context is included in the accessible label.",
        "Preserve focus and announce the new result range after a fragment swap.",
        "The server remains authoritative for out-of-range pages and must preserve filters in generated URLs.",
        server="On navigation",
        demo="pagination",
    ),
    ComponentDoc(
        "Loading",
        "interaction",
        "Show a polite busy status while a request or deferred component is pending.",
        "Loading(message='Loading…')",
        "Loading('Loading account activity…')",
        (p("message", "str", "Specific progress message."),),
        "Loading emits a status region with polite live and busy semantics. It is frequently used as Lazy or Poll content and as an HTMX indicator.",
        "Name the operation when several requests could be active; remove or replace the status when work completes.",
        "Do not use Loading for indeterminate work that has failed—render ErrorState.",
    ),
    ComponentDoc(
        "ErrorState",
        "interaction",
        "Present a recoverable request failure and optional HTMX retry.",
        "ErrorState(message, *, retry_href=None, retry_label='Retry', target=None)",
        "ErrorState('Activity could not be loaded.', retry_href='/activity', target='#activity')",
        (
            p("message", "str", "Human-readable failure."),
            p("retry_href", "str | None", "Safe GET retry endpoint."),
            p("retry_label", "str", "Retry command."),
            p("target", "safe CSS selector | None", "Replacement target."),
        ),
        "The error message uses alert semantics. When a retry URL is provided, the button issues a GET and replaces the target's outer HTML, allowing the server to restore the complete component state.",
        "Explain what failed, preserve user input, and make the next action explicit.",
        "Do not reveal internal exceptions, stack traces, identifiers, or secrets in the message.",
        server="On retry",
        demo="error",
    ),
    ComponentDoc(
        "Dialog",
        "interaction",
        "Present focused content in a native dialog with an explicit title and close path.",
        "Dialog(title, *nodes, children=None, open=False, modal=True, id=None, element_id=None)",
        "Dialog('Delete report', Text('This action cannot be undone.'), id='delete-report')",
        (
            p("title", "str", "Required dialog heading text."),
            p("nodes", "NodeLike", "Positional dialog body content."),
            p(
                "children",
                "NodeLike | sequence | None",
                "Keyword body content; combines with positional nodes.",
            ),
            p("open", "bool", "Render the native open attribute initially."),
            p("modal", "bool", "Browser-module intent exposed as data-modal."),
            p("id", "str | None", "Stable ID for a trigger and focus restoration."),
            p("element_id", "str | None", "Compatibility alias for id."),
        ),
        "Dialog renders a native `<dialog>` with a level-two title, body region, built-in Close form using the browser's dialog submission method, and an optional actions slot. A button whose `data-hedron-dialog-open` value is the dialog's `#id` opens it through the shipped browser module; modal dialogs use `showModal()`, while `modal=False` uses `show()`. Already-open modal dialogs are upgraded to `showModal()` on boot and after HTMX swaps. The component never treats confirmation as authorization.",
        "Open it from a clearly labelled trigger, place initial focus deliberately, support Escape and the Close control, and restore focus to the trigger when it closes.",
        "The `open` attribute alone does not create modal focus trapping or background inertness; use the supported browser module to call `showModal()`.",
        demo="dialog",
    ),
    ComponentDoc(
        "ChatMessage",
        "interaction",
        "Render one typed, escaped item in an application-owned chat transcript.",
        "ChatMessage(content, *, role='assistant', message_id=None, status=None)",
        "ChatMessage('Your deployment is ready.', role='assistant', message_id='message-42', status='Delivered')",
        (
            p("content", "str", "Escaped message text."),
            p(
                "role",
                "user | assistant | system | tool | status",
                "Typed speaker or message role.",
            ),
            p("message_id", "str | None", "Stable transcript item ID."),
            p("status", "str | None", "Optional polite delivery or streaming status."),
        ),
        "ChatMessage emits an article with role-specific classes and data metadata. A `status` message role becomes a polite live region; the separate status field also renders politely. History, ordering, retention, model-provider state, and streaming boundaries remain application-owned.",
        "Label the transcript itself, preserve meaningful DOM order, identify speakers with text rather than color alone, and avoid announcing the entire transcript when one status changes.",
        "Do not render secrets, hidden model instructions, tool credentials, or unbounded token streams as message content.",
        demo="chat-message",
    ),
    ComponentDoc(
        "ChatInput",
        "interaction",
        "Submit an explicit chat message and optionally an attachment to a typed HTMX target.",
        "ChatInput(*, ref=None, action=None, target=None, swap='beforeend', placeholder='Message', submit_label='Send', name='message', include_attachments=False)",
        "ChatInput(action='/chat', target='#transcript', placeholder='Ask the assistant', submit_label='Send')",
        (
            p("ref", "ComponentRef | None", "Preferred typed POST endpoint."),
            p("action", "str | None", "Fallback HTMX POST URL."),
            p("target", "safe CSS selector | None", "Transcript receiving the response."),
            p("swap", "str", "HTMX swap strategy; defaults to beforeend."),
            p("placeholder", "str", "Textarea hint."),
            p("submit_label", "str", "Visible send action."),
            p("name", "str", "Submitted message field name."),
            p("include_attachments", "bool", "Add a labelled file input."),
        ),
        "ChatInput renders a labelled, required textarea and submit button in a POST form. A typed ComponentRef or action supplies the HTMX request, the target selector is validated, and responses normally append to the transcript. The server owns authentication, CSRF, rate limits, attachment validation, persistence, and bounded streaming.",
        "Keep the textarea label available, announce sending and failure states without repeating the transcript, and preserve the draft when a request fails.",
        "Do not enable attachments without server-side filename, MIME, size, malware, authorization, storage, and retention controls.",
        server="On submit",
        demo="chat-input",
    ),
    ComponentDoc(
        "Auto",
        "data",
        "Choose an inspectable built-in renderer for a Python value.",
        "Auto(value=None, *, as_=None)",
        "Auto({'region': 'iad', 'healthy': True})",
        (
            p("value", "Any", "Value to inspect and render."),
            p("as_", "str | None", "Explicit renderer override."),
        ),
        "Auto applies bounded data intelligence and records why a renderer was selected. Mappings become description lists, sequences can become lists or tables, and explicit `as_` overrides ambiguity.",
        "Inspect generated hierarchy and table labeling; automatic structure cannot infer every domain meaning.",
        "Do not pass unbounded, secret-bearing, or adversarial objects without limits and redaction.",
        demo="auto",
    ),
    ComponentDoc(
        "DataTable",
        "data",
        "Render typed or pre-fetched rows as an accessible bounded data table.",
        "DataTable(rows=None, *, row_model=None, columns=None, page=None, query=None, caption=None, empty_message='No rows', page_size=25, allow_download=False)",
        "DataTable(rows, row_model=EmployeeRow, caption='Employees', page_size=25)",
        (
            p("rows", "Any", "Materialized mappings or model rows."),
            p("row_model", "type[Model] | None", "Typed column source."),
            p("columns", "Sequence[Column] | None", "Explicit column configuration."),
            p(
                "page",
                "DataPage | None",
                "Pre-fetched bounded page with total and version metadata.",
            ),
            p("query", "DataQuery | None", "Query metadata associated with the rows."),
            p("caption", "str | None", "Accessible table name."),
            p("empty_message", "str", "Text spanning the empty table body."),
            p("page_size", "int", "Page-size metadata."),
            p("allow_download", "bool", "Expose download intent to the owning application."),
        ),
        "DataTable normalizes mappings and models, resolves visible columns, redacts protected values, emits native table semantics, and exposes a CSV helper that omits hidden and secret columns. It does not fetch a source itself; fetch remote data first and pass a bounded DataPage.",
        "Use a precise caption, human column labels, and text equivalents for status or icon cells.",
        "Do not render an unbounded query or assume `allow_download` creates an authorized download route.",
        package="hedron[data]",
        demo="data-table",
    ),
    ComponentDoc(
        "ResourceList",
        "data",
        "List resources with first-party density and presentation tokens.",
        "ResourceList(*rows, *, density=None, id=None, class_=None)",
        "ResourceList(ResourceRow('Orders', description='Open work', href='/orders'), density='compact')",
        (
            p("rows", "ResourceRow | NodeLike", "Resource rows or compatible children."),
            p("density", "comfortable | compact | None", "Optional density token."),
        ),
        "ResourceList is the zero-application-CSS list surface for navigable collections.",
        "Prefer ResourceRow children so title/description/actions stay structured.",
        "Do not nest a full interactive form inside every row.",
    ),
    ComponentDoc(
        "ResourceRow",
        "data",
        "One resource entry with optional link, meta, and actions.",
        "ResourceRow(title, *, description=None, href=None, actions=None, meta=None, density=None)",
        "ResourceRow('North warehouse', description='Ready', href='/sites/north')",
        (
            p("title", "str", "Primary resource label."),
            p("description", "str | None", "Supporting text."),
            p("href", "SafeUrl | str | None", "Primary navigation target."),
            p("actions", "NodeLike | None", "Trailing action slot when not using href."),
            p("meta", "NodeLike | None", "Secondary metadata slot."),
        ),
        "ResourceRow keeps title/description structured and avoids nested interactive targets.",
        "Use either a primary href or an actions slot—not both competing click targets.",
        "Do not put a button inside a row that is already a link.",
    ),
    ComponentDoc(
        "Avatar",
        "content",
        "Person or entity avatar with image or initials fallback.",
        "Avatar(name, *, src=None, size=None, appearance=None, shape='circle')",
        "Avatar('Ada Lovelace', size='md')",
        (
            p("name", "str", "Accessible name and initials source."),
            p("src", "SafeUrl | str | None", "Optional image URL."),
            p("size", "sm | md | lg | None", "Named size token."),
            p("appearance", "plain | raised | None", "Optional appearance token."),
            p("shape", "circle | rounded | square", "Avatar shape token."),
        ),
        "Avatar falls back to initials when no image is provided.",
        "Always supply a real name so the accessible label and initials are meaningful.",
        "Do not use decorative-only avatars without a name.",
    ),
    ComponentDoc(
        "Identity",
        "content",
        "Compose avatar plus primary/secondary identity text.",
        "Identity(name, *, detail=None, src=None, size=None, appearance=None)",
        "Identity('Ada Lovelace', detail='Admin', size='md')",
        (
            p("name", "str", "Primary identity label."),
            p("detail", "str | None", "Secondary line such as role or email."),
            p("src", "SafeUrl | str | None", "Optional avatar image."),
            p("size / appearance", "token | None", "Presentation tokens shared with Avatar."),
        ),
        "Identity is the typed person/entity strip used by chrome and resource rows. The default theme keeps the name and detail in a constrained two-line text stack, so long names do not concatenate with the secondary detail or push surrounding chrome out of bounds.",
        "Keep detail text supplementary; the name remains primary.",
        "Do not nest a second interactive avatar link inside Identity.",
    ),
    ComponentDoc(
        "DataEditor",
        "data",
        "Edit bounded typed rows and submit explicit change sets.",
        "DataEditor(rows=None, *, key='editor', row_model=None, columns=None, key_field='id', on_save=None, source=None, page=None, save_mode='batch', page_size=25, caption=None, save_endpoint=None, allow_deletes=True)",
        "DataEditor(rows, key='allocation-editor', row_model=EmployeeRow, on_save=save_changes, key_field='id', allow_deletes=False)",
        (
            p("rows", "Any", "Materialized editable rows."),
            p("key", "str", "Stable browser editor identity."),
            p("row_model / columns", "schema inputs", "Field types and edit policy."),
            p("key_field", "str", "Stable row identity field."),
            p("on_save", "callable | None", "Validated change-set handler."),
            p("source / page", "data inputs", "Sync source or explicit bounded page."),
            p("save_mode", "SaveMode", "Batch or supported save behavior."),
            p("page_size", "int", "Source fetch bound."),
            p("caption", "str | None", "Accessible editor/table name."),
            p("save_endpoint", "str | None", "Browser module submission endpoint."),
            p("allow_deletes", "bool", "Permit delete change sets; defaults to true."),
        ),
        "The editor tracks updates, additions, and deletions as a typed DataChanges payload, filters changes against writable-field policy, and applies them through a callback or data source. The browser asset improves editing, but server-side policy remains authoritative.",
        "Maintain keyboard editing, visible focus, field-level errors, and a clear saved or conflicted status.",
        "Set `allow_deletes=False` unless deletion is intentional, and never trust client change sets, hidden fields, or optimistic versions without server validation.",
        package="hedron[data]",
        server="On save",
        demo="data-editor",
    ),
    ComponentDoc(
        "Metric",
        "utilities",
        "Display a labelled value and optional directional change.",
        "Metric(label, value, *, delta=None, delta_tone='neutral')",
        "Metric('Monthly revenue', '$84,200', delta='+8.4%', delta_tone='up')",
        (
            p("label", "str", "Metric name."),
            p("value", "Any", "Current value converted to text."),
            p("delta", "Any | None", "Optional change."),
            p("delta_tone", "up | down | neutral", "Domain-aware direction token."),
        ),
        "Metric uses a description list so label, value, and delta remain related in non-visual reading. Tone is exposed as data for theming.",
        "Include a time window, unit, and whether up/down is good when context does not make that obvious.",
        "Never rely on green/red or arrows alone to explain the delta.",
    ),
    ComponentDoc(
        "FileUpload",
        "utilities",
        "Choose one or more local files with advisory browser constraints.",
        "FileUpload(*, name='file', accept=None, maximum_size=5_000_000, multiple=False, label='Upload file')",
        "FileUpload(name='evidence', accept='.pdf,image/*', maximum_size=10_000_000, label='Upload evidence')",
        (
            p("name", "str", "Multipart field name."),
            p("accept", "str | None", "Browser file-type hint."),
            p("maximum_size", "int", "Advisory size data attribute."),
            p("multiple", "bool", "Allow multiple selection."),
            p("label", "str", "Accessible and visible control label."),
        ),
        "The component renders a native file input and exposes the maximum size for progressive client feedback. The browser's accepted types and size hint are not security controls.",
        "Tell users accepted formats and limits before selection, and announce rejected files without clearing valid choices unnecessarily.",
        "Validate filename, MIME/content, size, count, authorization, and storage location on the server.",
        server="On enclosing form submit",
        demo="file",
    ),
    ComponentDoc(
        "DownloadButton",
        "utilities",
        "Download an authorized same-origin resource with a safe filename.",
        "DownloadButton(*, href=None, filename, label='Download', source=None)",
        "DownloadButton(href='/exports/report.csv', filename='report.csv', label='Download CSV')",
        (
            p("href / source", "SafeUrl | str", "Required same-origin download endpoint."),
            p("filename", "str", "Validated suggested basename."),
            p("label", "str", "Visible action."),
        ),
        "DownloadButton is a same-origin anchor with `download` and button styling. Pair it with `safe_download_response`, authorization, private no-store caching, and a validated basename on the server.",
        "Include file type and, when known, size in nearby text so users understand the result.",
        "A download attribute does not authorize access; the route must check permission on every request.",
        server="On navigation",
        demo="download",
    ),
    ComponentDoc(
        "CodeViewer",
        "utilities",
        "Inspect bounded, escaped source text with optional language metadata.",
        "CodeViewer(code, *, language=None, max_chars=100_000)",
        "CodeViewer(config_text, language='toml', max_chars=20_000)",
        (
            p("code", "str", "Source text."),
            p("language", "str | None", "Language metadata."),
            p("max_chars", "int", "Hard display bound."),
        ),
        "CodeViewer truncates oversized content before rendering it in pre/code elements. It is an inspection surface, not an editor or executable sandbox.",
        "Provide context for what the code represents and keep horizontal scrolling keyboard-accessible.",
        "Redact secrets before construction; truncation is not redaction.",
    ),
    ComponentDoc(
        "JSONViewer",
        "utilities",
        "Pretty-print bounded JSON-like data with recursive secret redaction.",
        "JSONViewer(value, *, max_chars=100_000)",
        "JSONViewer({'job': 42, 'status': 'complete', 'token': 'redacted automatically'})",
        (p("value", "Any", "JSON-like value."), p("max_chars", "int", "Hard text bound.")),
        "JSONViewer recursively redacts Secret instances and keys containing common secret, password, or token terms, limits list breadth and recursion depth, formats with indentation, and truncates final text.",
        "Introduce complex payloads and avoid forcing users to navigate huge trees in the primary task flow.",
        "Key-name redaction is defense in depth, not a complete data-loss-prevention system.",
    ),
    ComponentDoc(
        "Progress",
        "utilities",
        "Show determinate completion with a native progress element.",
        "Progress(value, *, maximum=100, label=None)",
        "Progress(68, maximum=100, label='Import progress')",
        (
            p("value", "float", "Current progress."),
            p("maximum", "float", "Completion value."),
            p("label", "str | None", "Accessible name."),
        ),
        "The browser calculates completion from value and maximum and exposes native progress semantics. Render a separate numeric Text value when precise percentage matters visually.",
        "Always provide a label unless nearby labelled context names the progress element.",
        "Use Loading or Status for indeterminate work; do not fake determinate values.",
    ),
    ComponentDoc(
        "Status",
        "utilities",
        "Announce a concise operation state with a semantic tone.",
        "Status(message, *, tone='info', live=True)",
        "Status('Import complete: 84 records added.', tone='success')",
        (
            p("message", "str", "Status text."),
            p("tone", "info | success | warning | danger", "Visual token."),
            p("live", "bool", "Enable polite live-region behavior."),
        ),
        "Status is intended for updates such as saved, queued, or completed. With live behavior enabled, an update inserted after page load is announced politely.",
        "Keep the live region mounted when possible and update its text; do not flood it with rapid, low-value changes.",
        "Use Alert/ErrorState for urgent failures that require action.",
    ),
    ComponentDoc(
        "Toast",
        "utilities",
        "Render a polite, transient-looking status message.",
        "Toast(message, *, tone='info', ttl_ms=4000)",
        "Toast('API key copied.', tone='success')",
        (
            p("message", "str", "Escaped toast text."),
            p("tone", "info | success | warning | danger", "Visual token."),
            p("ttl_ms", "int | None", "Auto-dismiss delay in milliseconds; danger defaults to none."),
        ),
        "Toast emits a polite status region with a tone class and optional TTL. Pair with ToastHost at frozen `#hedron-toast`. Danger toasts stay until dismissed unless `ttl_ms` is set; they render a Dismiss control (`data-hedron-toast-dismiss`) handled by `hedron-ui.mjs`.",
        "If application JavaScript removes the toast, allow enough reading time, pause any timer on hover or focus, and preserve critical messages elsewhere.",
        "Never auto-dismiss errors that require a user decision, and do not expect a `dismissible` constructor option.",
        demo="toast",
    ),
    ComponentDoc(
        "ToastHost",
        "utilities",
        "Frozen out-of-band toast sink at `#hedron-toast`.",
        "ToastHost()",
        "ToastHost()",
        (),
        "ToastHost mounts the reserved `#hedron-toast` live region. Queue, TTL, and danger dismiss live in both `hedron-ui.mjs` copies (`hedron-core` static and `hedron/static`); authors do not write `hx-on` listeners.",
        "Keep one ToastHost in the document shell so OOB toasts survive panel swaps.",
        "Do not invent a second toast host id or attach `hx-on` handlers for queueing.",
    ),
    ComponentDoc(
        "ScrollRegion",
        "layout",
        "Bound a semantic list, log, or arbitrary child region without changing its children.",
        "ScrollRegion(*nodes, children=None, axis='block', size='md', affordance='auto', label=None, id=None, class_=None, mark=None)",
        "ScrollRegion(Text('Recent events'), axis='block', size='md', label='Recent events')",
        (),
        "ScrollRegion owns bounded overflow markers while preserving the child tree and its semantics. Use `label=` when the region needs an accessible name.",
        "Use a meaningful label for multiple scrollable regions and keep keyboard focus on the actual interactive children.",
        "Do not use ScrollRegion to hide required content in print or to replace semantic list/table elements.",
    ),
    ComponentDoc(
        "ThemePicker",
        "theme",
        "Render an accessible no-JavaScript form for an allowlisted theme and color-mode preference.",
        "ThemePicker(*, themes=('default', 'aurora'), color_modes=('system', 'light', 'dark'), selected=None, action='/preferences/theme', csrf_token=None)",
        "ThemePicker(selected=ThemePreference(theme='aurora', color_mode='dark'))",
        (),
        "ThemePicker emits a native POST form. The application owns persistence and authorization; optional client boot helpers are bounded and do not replace the server-rendered selection.",
        "Keep the labels, native submit path, and selected server state available when JavaScript is disabled.",
        "Do not pass unregistered theme names, remote actions, CSS, or identity-bearing preference values into the picker.",
    ),
    ComponentDoc(
        "Expander",
        "utilities",
        "Reveal optional content with native details/summary behavior.",
        "Expander(title, *nodes, children=None, open=False, id=None, class_=None)",
        "Expander('Advanced settings', Text('Configure retry and timeout behavior.'))",
        (
            p("title", "str", "Visible summary label."),
            p("nodes", "NodeLike", "Positional disclosure content."),
            p(
                "children",
                "NodeLike | sequence | None",
                "Keyword disclosure content; combines with positional nodes.",
            ),
            p("open", "bool", "Initial expanded state."),
            p("id", "str | None", "Stable ID for links, tests, or replacement."),
            p("class_", "str | None", "Application class appended to `hedron-expander`."),
        ),
        "The native details element supplies keyboard and disclosure state without custom JavaScript. Content remains in the document and participates in search.",
        "Use a summary that describes the hidden content, not a generic “More”.",
        "Do not hide required fields or primary instructions in a collapsed expander.",
    ),
    ComponentDoc(
        "Tabs",
        "utilities",
        "Render a small ARIA tablist with one initially active labelled panel and optional responsive appearance tokens.",
        "Tabs(*items, panels=None, active=None, appearance=None, density=None, responsive=None, id=None, class_=None)",
        "Tabs(('Overview', Text('Current health')), ('History', Table(['Run'], [['Today']])), active='Overview')",
        (
            p("items", "tuple[str, NodeLike]", "Positional tab label and panel-content pairs."),
            p(
                "panels",
                "sequence[tuple[str, NodeLike]] | None",
                "Keyword alternative for a generated panel list.",
            ),
            p("active", "str | None", "Active panel label; defaults to the first label."),
            p("appearance", "contained | underline | pills | None", "Optional visual treatment."),
            p("density", "compact | comfortable | spacious | None", "Optional tab hit-area density."),
            p("responsive", "scroll | stretch | compact | None", "Narrow-width behavior; `scroll` preserves all tabs."),
            p(
                "id",
                "str | None",
                "Optional tab-set ID prefix; a collision-free request-local prefix is generated by default.",
            ),
            p("class_", "str | None", "Application class appended to `hedron-tabs`."),
        ),
        "Tabs validates unique labels and the requested active label, then emits tab buttons with selected state, collision-free control relationships, roving-tabindex values, and corresponding tabpanels. Multiple and nested tab sets can therefore share a page safely. Phase 0.61 adds finite appearance, density, and responsive markers; `responsive='scroll'` preserves all labels when they do not fit. Switching panels requires a browser enhancement; the docs JavaScript demonstrates click plus Left/Right/Home/End keyboard behavior.",
        "Ship equivalent click and arrow-key behavior in the application browser module, and retain correct focus and selected state after server swaps.",
        "Do not repeat panel labels or use `selected=`; pass pairs positionally (or with `panels=`) and select by label with `active=`.",
        demo="tabs",
    ),
    ComponentDoc(
        "Sidebar",
        "utilities",
        "Render complementary page content with an accessible label.",
        "Sidebar(*nodes, children=None, label='Sidebar', id=None, class_=None)",
        "Sidebar(Nav(Link('Overview', '/'), Link('Settings', '/settings')), label='Workspace')",
        (
            p("nodes", "NodeLike", "Positional complementary content."),
            p(
                "children",
                "NodeLike | sequence | None",
                "Keyword content; combines with positional nodes.",
            ),
            p("label", "str", "Accessible region name."),
            p("id", "str | None", "Stable DOM target for the sidebar."),
            p("class_", "str | None", "Application class appended to `hedron-sidebar`."),
        ),
        "Sidebar emits an aside landmark with its label, while positioning and responsive behavior belong to the surrounding Grid and theme.",
        "Use a distinct label when more than one aside exists and keep essential mobile actions available when the visual sidebar collapses.",
        "Sidebar does not create an application shell by itself; compose it explicitly with Main.",
    ),
    ComponentDoc(
        "ColorModeToggle",
        "theme",
        "Let users choose light, dark, or system color preference.",
        "ColorModeToggle(*, preference=ColorMode.SYSTEM, label='Color mode', id=None, action=None, csrf_token=None)",
        "ColorModeToggle(preference=ColorMode.SYSTEM, action='/preferences/color', csrf_token=csrf_token)",
        (
            p("preference", "ColorMode | str", "Current light/dark/system selection."),
            p("label", "str", "Control label."),
            p("id", "str | None", "Optional select ID; generated collision-free by default."),
            p("action", "str | None", "Persistence endpoint."),
            p("csrf_token", "str | None", "CSRF value for POST persistence."),
        ),
        "The component renders a labelled native select and Apply button with a collision-free relationship, so more than one settings surface can contain a toggle safely. The server can persist a cookie or session preference, while `color_mode_script()` resolves system preference early enough to avoid a flash.",
        "Every theme must meet contrast and focus requirements in all three modes; system mode must respond to user-agent preference.",
        "Treat persistence as a state-changing POST and validate CSRF; do not hide the control based on JavaScript availability.",
        server="On Apply",
        demo="color-mode",
    ),
    ComponentDoc(
        "Chart",
        "charts",
        "Render a validated ChartSpec through the first-party hedron-chart host.",
        "Chart(spec=None, *, class_=None, **kwargs)",
        "Chart(spec)",
        (
            p(
                "spec",
                "ChartSpec | Mapping[str, Any] | None",
                "Schema-versioned chart specification; rendering without one raises `ValueError`.",
            ),
            p("class_", "str | None", "Optional class on the `hedron-chart` host."),
            p("kwargs", "object", "Forwarded to `ChartProps`; unknown keys are rejected."),
        ),
        "Chart validates and compiles the specification into a deterministic ChartPlan, emits a semantic figure/summary/table fallback, and serializes the plan into the local `hedron-chart` custom element for progressive SVG or Canvas enhancement.",
        "Provide a useful title and description in `spec.accessibility`; keep the generated summary and table fallback unless an equivalent accessible path is supplied.",
        "Do not pass vendor Plotly/Vega dictionaries as ChartSpec or treat chart selection events as authorization.",
        package="hedron[charts]",
        demo="line-chart",
    ),
    ComponentDoc(
        "LineChart",
        "charts",
        "Plot one x/y series from row mappings with an accessible fallback.",
        "LineChart(data, *, x, y, title, description=None, alt=None, waiver=None, limits=None)",
        "LineChart(rows, x='month', y='revenue', title='Monthly revenue', description='Revenue rose from January through June.')",
        (
            p("data", "Sequence[Mapping]", "Bounded rows."),
            p("x / y", "str", "Source field names."),
            p("title", "str", "Required chart title."),
            p("description / alt", "str | None", "Text equivalents."),
            p("waiver", "str | None", "Reviewed accessibility exception."),
            p("limits", "VisualizationLimits | None", "Complexity bounds."),
        ),
        "LineChart converts the beginner call to ChartSpec, compiles a deterministic ChartPlan, emits the semantic fallback, and uses the first-party hedron-chart host. It does not select Matplotlib implicitly. Numeric and categorical x values are accepted.",
        "Supply a conclusion-oriented description and keep the tabular fallback available to users who cannot perceive the plot.",
        "Bound data and never insert raw labels into active SVG or bypass the accessibility contract.",
        package="hedron[charts]",
        demo="line-chart",
    ),
    ComponentDoc(
        "AreaChart",
        "charts",
        "Plot a filled x/y area series from row mappings with an accessible fallback.",
        "AreaChart(data, *, x, y, title, description=None, alt=None, waiver=None, limits=None)",
        "AreaChart(rows, x='month', y='revenue', title='Monthly revenue', description='Revenue rose from January through June.')",
        (
            p("data", "Sequence[Mapping]", "Bounded rows."),
            p("x / y", "str", "Source field names."),
            p("title", "str", "Required chart title."),
            p("description / alt", "str | None", "Text equivalents."),
            p("waiver", "str | None", "Reviewed accessibility exception."),
            p("limits", "VisualizationLimits | None", "Complexity bounds."),
        ),
        "AreaChart converts the beginner call to ChartSpec and renders it through the first-party hedron-chart host with a reviewed SVG fallback and redacted table. It does not select Matplotlib implicitly.",
        "Supply a conclusion-oriented description and keep the tabular fallback available to users who cannot perceive the plot.",
        "Bound data and never insert raw labels into active SVG or bypass the accessibility contract.",
        package="hedron[charts]",
        demo="line-chart",
    ),
    ComponentDoc(
        "BarChart",
        "charts",
        "Plot categorical bars from row mappings with an accessible fallback.",
        "BarChart(data, *, x, y, title, description=None, alt=None, waiver=None, limits=None)",
        "BarChart(rows, x='region', y='requests', title='Requests by region', description='US East handles the largest share.')",
        (
            p("data", "Sequence[Mapping]", "Bounded rows."),
            p("x / y", "str", "Source field names."),
            p("title", "str", "Required chart title."),
            p("description / alt", "str | None", "Text equivalents."),
            p("waiver", "str | None", "Reviewed accessibility exception."),
            p("limits", "VisualizationLimits | None", "Complexity bounds."),
        ),
        "BarChart converts the beginner call to ChartSpec and renders it through the first-party hedron-chart host with a reviewed SVG fallback and redacted table. It does not select Matplotlib implicitly.",
        "Supply a conclusion-oriented description and keep the tabular fallback available to users who cannot perceive the plot.",
        "Bound data and never insert raw labels into active SVG or bypass the accessibility contract.",
        package="hedron[charts]",
        demo="bar-chart",
    ),
    ComponentDoc(
        "ScatterChart",
        "charts",
        "Plot an x/y scatter series from row mappings with an accessible fallback.",
        "ScatterChart(data, *, x, y, title, description=None, alt=None, waiver=None, limits=None)",
        "ScatterChart(rows, x='latency', y='errors', title='Latency vs errors', description='Higher latency correlates with elevated error rates.')",
        (
            p("data", "Sequence[Mapping]", "Bounded rows."),
            p("x / y", "str", "Source field names."),
            p("title", "str", "Required chart title."),
            p("description / alt", "str | None", "Text equivalents."),
            p("waiver", "str | None", "Reviewed accessibility exception."),
            p("limits", "VisualizationLimits | None", "Complexity bounds."),
        ),
        "ScatterChart converts the beginner call to a point-mark ChartSpec and renders it through the first-party hedron-chart host with a reviewed SVG fallback and redacted table. It does not select Matplotlib implicitly.",
        "Supply a conclusion-oriented description and keep the tabular fallback available to users who cannot perceive the plot.",
        "Bound data and never insert raw labels into active SVG or bypass the accessibility contract.",
        package="hedron[charts]",
        demo="scatter-chart",
    ),
    ComponentDoc(
        "MatplotlibChart",
        "charts",
        "Render a Matplotlib figure as reviewed static SVG or image output.",
        "MatplotlibChart(figure, *, title=None, description=None, alt=None, waiver=None, fmt='svg')",
        "MatplotlibChart(fig, title='Latency distribution', description='Most requests complete below 200 ms.')",
        (
            p("figure", "Matplotlib Figure", "Completed figure."),
            p("title / description / alt", "str | None", "Accessible metadata."),
            p("waiver", "str | None", "Reviewed exception."),
            p("fmt", "str", "Static output format."),
        ),
        "The adapter compiles the figure server-side and renders inert output, avoiding a browser plotting runtime. SVG passes active-content rejection and output limits.",
        "Do not rely only on labels embedded in a dense plot; provide a description and data summary.",
        "Close figures after use in long-running processes and bound image dimensions and complexity.",
        package="hedron-charts[matplotlib]",
        demo="bar-chart",
    ),
    ComponentDoc(
        "PlotlyChart",
        "charts",
        "Render a Plotly figure through Hedron's bounded adapter pipeline.",
        "PlotlyChart(figure, *, title=None, description=None, alt=None, waiver=None)",
        "PlotlyChart(fig, title='Requests by region', description='US East handles the largest share.')",
        (
            p("figure", "Plotly figure", "Figure specification."),
            p("title / description / alt", "str | None", "Accessible metadata."),
            p("waiver", "str | None", "Reviewed exception."),
        ),
        "The adapter compiles the figure into the supported static or browser representation, enforces visualization limits, and attaches accessible metadata and fallback content.",
        "Make hover-only values available through labels or a table and ensure keyboard users can reach any enabled controls.",
        "Do not pass untrusted custom HTML, JavaScript callbacks, or unbounded traces.",
        package="hedron-charts[plotly]",
        demo="donut-chart",
    ),
    ComponentDoc(
        "AltairChart",
        "charts",
        "Render an Altair chart through the declarative visualization adapter.",
        "AltairChart(chart, *, title=None, description=None, alt=None, waiver=None)",
        "AltairChart(chart, title='Deployments per week', description='Deployments peaked in week four.')",
        (
            p("chart", "Altair Chart", "Declarative chart object."),
            p("title / description / alt", "str | None", "Accessible metadata."),
            p("waiver", "str | None", "Reviewed exception."),
        ),
        "The server compiles the chart specification under output and accessibility limits. Hedron owns the embedding contract instead of accepting arbitrary active markup.",
        "Use encodings that remain distinguishable without color and provide a narrative or table alternative.",
        "Validate data volume and avoid specifications that fetch remote resources in the browser.",
        package="hedron-charts[altair]",
        demo="scatter-chart",
    ),
    ComponentDoc(
        "ActionDock",
        "layout",
        "Sticky action dock for primary controls.",
        "ActionDock(*children, position='bottom')",
        "ActionDock(Button('Save'))",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "Audio",
        "content",
        "Accessible HTML audio player with SafeUrl source.",
        "Audio(src, controls=True, autoplay=False)",
        "Audio('/media/clip.mp3')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "BottomDock",
        "layout",
        "Bottom sticky dock alias for chat or actions.",
        "BottomDock(*children)",
        "BottomDock(Text('Composer'))",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "CameraCapture",
        "forms",
        "Camera capture file input (capture=environment).",
        "CameraCapture(name='photo')",
        "CameraCapture(name='photo')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "Carousel",
        "surfaces",
        "No-JS carousel as an ordered slide list with controls.",
        "Carousel(slides, label='Gallery')",
        "Carousel([Text('One'), Text('Two')])",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "ChipInput",
        "forms",
        "Free-text chip/tag multivalue input.",
        "ChipInput(name, values=())",
        "ChipInput('tags', values=('a',))",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "CircularProgress",
        "utilities",
        "Circular determinate/indeterminate progress with status text.",
        "CircularProgress(value=50, maximum=100)",
        "CircularProgress(value=50)",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "ClipboardCopy",
        "controls",
        "Copy-to-clipboard control (write-only; no clipboard read).",
        "ClipboardCopy(text, label='Copy')",
        "ClipboardCopy('secret-token')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "ColorInput",
        "forms",
        "Native color picker input.",
        "ColorInput(name, value='#000000')",
        "ColorInput('accent', value='#336699')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "ConfirmButton",
        "controls",
        "Button with explicit confirmation prompt (not authorization).",
        "ConfirmButton(label, confirm='Are you sure?')",
        "ConfirmButton('Delete', confirm='Delete item?')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "ContextMenu",
        "surfaces",
        "Context menu with required overflow-button alternative.",
        "ContextMenu(label, *actions)",
        "ContextMenu('Row', LinkButton('Edit', '/edit'))",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "DateInput",
        "forms",
        "Native date input.",
        "DateInput(name, value='')",
        "DateInput('when', value='2026-08-05')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "DateTimeInput",
        "forms",
        "Native datetime-local input.",
        "DateTimeInput(name)",
        "DateTimeInput('starts')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "DirectoryUpload",
        "forms",
        "Directory upload input with server-side validation helper.",
        "DirectoryUpload(name='files')",
        "DirectoryUpload(name='bundle')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "PredictionLabel",
        "content",
        "Ranked prediction labels with class identity and an accessible table encoding.",
        "PredictionLabel(scores, *, title='Predictions', threshold=None, class_=None, mark=None)",
        "PredictionLabel([{'class_id': 'cat', 'score': 0.9, 'calibrated': True}])",
        (
            p(
                "scores",
                "Sequence[PredictionScore | Mapping]",
                "Ranked class scores with optional precision/calibration.",
            ),
            p("title", "str", "Accessible table caption."),
            p("threshold", "float | None", "Optional decision threshold shown in the caption."),
            p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),
        ),
        "Phase 0.18 model-demo presentation. Retain class identity and non-color encodings for ranked scores.",
        "Expose an HTML table (or equivalent) so screen-reader users can read class, score, and calibration without relying on color alone.",
        "Do not treat PredictionLabel as ground truth; pair with PredictionFeedback for governed evaluation capture.",
    ),
    ComponentDoc(
        "ParameterViewer",
        "content",
        "Schema-oriented parameter documentation with secret redaction.",
        "ParameterViewer(parameters, *, title='Parameters', secret_keys=(), class_=None, mark=None)",
        "ParameterViewer({'lr': 0.01, 'api_token': 'x'}, secret_keys=('api_token',))",
        (
            p(
                "parameters",
                "Mapping[str, Any]",
                "Parameter map rendered as definition list entries.",
            ),
            p("secret_keys", "Sequence[str]", "Keys whose values are replaced with [redacted]."),
            p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),
        ),
        "Phase 0.18 model-demo presentation. Redact secrets before rendering.",
        "Use readable key labels; redacted values must not leak secrets into markup.",
        "Never log or cache raw secret_keys values in examples or recorders.",
    ),
    ComponentDoc(
        "Dialogue",
        "content",
        "Multi-speaker transcript with accessible speaker labels and timing metadata.",
        "Dialogue(turns, *, title='Dialogue', class_=None, mark=None)",
        "Dialogue([{'speaker': 'A', 'text': 'Hello', 'start_ms': 0, 'end_ms': 500}])",
        (
            p(
                "turns",
                "Sequence[DialogueTurn | Mapping]",
                "Ordered speaker turns with optional timing/tags.",
            ),
            p("title", "str", "Section label."),
            p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),
        ),
        "Phase 0.18 model-demo presentation. Speaker identity must not rely on color alone.",
        "Each turn exposes an accessible speaker label; timing/tags are text metadata.",
        "Do not use Dialogue as a chat input widget; pair with ChatMessage/ChatInput for interactive chat.",
    ),
    ComponentDoc(
        "Gallery",
        "content",
        "Responsive image/video gallery with optional lightbox mode.",
        "Gallery(items, lightbox=False)",
        "Gallery([])",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "GeoJSONLayer",
        "content",
        "Sanitized GeoJSON layer for Map (or standalone alternative list).",
        "GeoJSONLayer(data, max_features=500)",
        "GeoJSONLayer({'type':'FeatureCollection','features':[]})",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "GeolocationButton",
        "forms",
        "Spoofable geolocation form fields with progressive enhancement.",
        "GeolocationButton(label='Share location')",
        "GeolocationButton()",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "GeolocationHint",
        "content",
        "Static reminder that geolocation is spoofable.",
        "GeolocationHint()",
        "GeolocationHint()",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "Help",
        "surfaces",
        "Accessible help text associated with a control.",
        "Help(text, for_id=None)",
        "Help('Use YYYY-MM-DD')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "HelpInspector",
        "utilities",
        "Bounded details/summary object or help inspector.",
        "HelpInspector(title, body)",
        "HelpInspector('Props', Text('...'))",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "IFrame",
        "content",
        "Policy-bounded sandboxed iframe with SafeUrl source.",
        "IFrame(src, title, allow_remote=False)",
        "IFrame('/embed', title='Embed')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "Logo",
        "content",
        "Application logo image with required alt text.",
        "Logo(src, alt='App')",
        "Logo('/logo.svg', alt='Hedron')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "Map",
        "content",
        "Policy-bounded map with required table alternative.",
        "Map(center=(0,0), zoom=2, markers=())",
        "Map(center=(37.77,-122.42), zoom=10, markers=())",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "Math",
        "content",
        "Escaped LaTeX/math presentation (enhancement optional).",
        "Math(latex, display=False)",
        "Math(r'e^{i\\pi}+1=0', display=True)",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "MenuButton",
        "controls",
        "Button that reveals a menu of actions.",
        "MenuButton(label, *items)",
        "MenuButton('More', LinkButton('One', '/one'))",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "MicrophoneCapture",
        "forms",
        "Microphone capture file input (capture=user).",
        "MicrophoneCapture(name='audio')",
        "MicrophoneCapture(name='clip')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "MultiSelect",
        "forms",
        "Native multi-select control.",
        "MultiSelect(name, options, values=())",
        "MultiSelect('roles', options=(('a','A'),))",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "NumberInput",
        "forms",
        "Native number input.",
        "NumberInput(name, value=None)",
        "NumberInput('qty', value=1)",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "PageIcon",
        "content",
        "Favicon / page icon helper link or image.",
        "PageIcon(href)",
        "PageIcon('/favicon.ico')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "PdfViewer",
        "content",
        "PDF embed/object viewer with SafeUrl source.",
        "PdfViewer(src, title='PDF')",
        "PdfViewer('/doc.pdf', title='Report')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "Pills",
        "forms",
        "Pill-styled segmented choice group.",
        "Pills(name, options, value=None)",
        "Pills('tone', options=(('a','A'),))",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "Popover",
        "surfaces",
        "Native popover or details/summary disclosure.",
        "Popover(*nodes, children=None, label='Open', mode='popover', placement='block-end', collision='flip', id=None, class_=None, mark=None)",
        "Popover(Text('Details'), label='Info', placement='inline-end', collision='shift')",
        (
            p("nodes", "NodeLike", "Popover body content."),
            p("children", "NodeLike | sequence | None", "Keyword alternative for generated or declarative child lists."),
            p("label", "str", "Accessible label text shown to users. Default: `'Open'`."),
            p("mode", "Literal['popover', 'details']", "Presentation mode for the disclosure surface. Default: `'popover'`."),
            p("placement", "Literal['block-start', 'block-end', 'inline-start', 'inline-end', 'center']", "Logical placement. Default: `'block-end'`."),
            p("collision", "Literal['flip', 'shift', 'static']", "Finite collision fallback. Default: `'flip'`."),
            p("id", "str | None", "Optional DOM `id`. Default: `None`."),
            p("class_", "str | None", "Optional CSS class string. Default: `None`."),
            p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),
        ),
        "Phase 0.15 surface with the 0.59 logical placement and collision contract. Prefer native HTML semantics and ordinary HTTP actions. `placement` is expressed in logical block/inline terms so RTL and writing-mode layouts do not need physical left/right assumptions. `collision` selects the finite fallback strategy: `flip`, `shift`, or `static`.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not require anchor-positioning support; the static/native placement path remains the contract.",
    ),
    ComponentDoc(
        "RangeInput",
        "forms",
        "Native range slider input.",
        "RangeInput(name, min=0, max=100)",
        "RangeInput('vol', value=50)",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "RatingInput",
        "forms",
        "Accessible 1..n rating radios.",
        "RatingInput(name, maximum=5)",
        "RatingInput('score', maximum=5)",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "SegmentedControl",
        "forms",
        "Segmented radio control group.",
        "SegmentedControl(name, options, value=None)",
        "SegmentedControl('mode', options=(('a','A'),))",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "SelectSlider",
        "forms",
        "Range input with optional datalist marks.",
        "SelectSlider(name, options)",
        "SelectSlider('size', options=(('s','S'),('l','L')))",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "Spacer",
        "layout",
        "Semantic spacing primitive.",
        "Spacer(size='1rem')",
        "Spacer(size='2rem')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "TimeInput",
        "forms",
        "Native time input.",
        "TimeInput(name)",
        "TimeInput('at')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "Timeline",
        "surfaces",
        "Semantic ordered timeline of events.",
        "Timeline()",
        "Timeline().entry('Now', 'Shipped', Text('0.15'))",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "ToggleSwitch",
        "forms",
        "Switch-styled checkbox control.",
        "ToggleSwitch(name, checked=False)",
        "ToggleSwitch('notify', checked=True)",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "Tooltip",
        "surfaces",
        "Accessible tooltip / title help.",
        "Tooltip(text, *children)",
        "Tooltip('More info', Text('Hover'))",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "Video",
        "content",
        "Accessible HTML video player with SafeUrl source.",
        "Video(src, controls=True)",
        "Video('/media/clip.mp4')",
        (p("mark", "str | None", "Optional stable test mark (`data-hedron-mark`)."),),
        "Phase 0.15 surface. Prefer native HTML semantics and ordinary HTTP actions.",
        "Keyboard and screen-reader operable; no-JS fallback required where interactive.",
        "Do not treat client-only hints (geolocation, browser storage) as authorization.",
    ),
    ComponentDoc(
        "AmbientBackdrop",
        "surfaces",
        "Finite decorative backdrop that remains inert and outside content semantics.",
        "AmbientBackdrop(*nodes, pattern='radial', tone='accent', intensity='subtle', id=None, class_=None, mark=None)",
        "AmbientBackdrop(Container(Text('Dashboard'), max_width='lg'), pattern='mesh', tone='accent')",
        (
            p("nodes / children", "NodeLike", "Semantic page or surface content above the decoration."),
            p("pattern", "radial | dots | grid | mesh", "Finite deterministic decoration preset."),
            p("tone", "accent | muted | neutral", "Theme-owned decoration tone."),
            p("intensity", "subtle | soft", "Bounded contrast treatment."),
        ),
        "AmbientBackdrop emits an aria-hidden decoration layer with pointer-events disabled, so child content remains in document order. Print, forced-colors, and reduced-transparency styles hide the decoration.",
        "Keep meaningful headings, status, and focusable controls in the child content; the backdrop is never the source of contrast or information.",
        "Do not pass arbitrary gradients, CSS strings, or interactive content as decoration.",
    ),
    ComponentDoc(
        "AsyncRegion",
        "interaction",
        "Server-authored lifecycle boundary with ordinary fragment or page fallback.",
        "AsyncRegion(*nodes, state='idle', initial=None, pending=None, empty=None, success=None, error=None, timeout=None, cancelled=None, stale=None, retry=None, conflict=None, fallback='fragment', label=None)",
        "AsyncRegion(Text('Report ready'), state='success', pending=Text('Loading report…'), error=Text('Try again'))",
        (
            p("state", "idle | pending | empty | success | error | timeout | cancelled | stale | conflict", "Closed server-authored presentation state."),
            p("state slots", "NodeLike | None", "Optional initial, pending, empty, success, error, timeout, cancelled, stale, retry, and conflict content."),
            p("fallback", "fragment | page", "Ordinary enhancement-free response boundary."),
            p("label", "str | None", "Accessible label for the region and polite live status."),
        ),
        "AsyncRegion selects one state slot while rendering ordinary semantic HTML. It does not suspend Python, require hydration, or create a browser state store.",
        "Pending state exposes aria-busy; provide visible status text and keep recovery controls keyboard accessible.",
        "Do not use client state as authorization or omit an ordinary full-fragment/full-page fallback.",
    ),
    ComponentDoc(
        "NavGroup",
        "layout",
        "Standalone labelled navigation group shared by AppShell and fragment responses.",
        "NavGroup(label=None, *items, children=None, id=None, class_=None, mark=None)",
        "NavGroup('Workspace', NavLink('Overview', '/'), NavLink('Reports', '/reports'))",
        (
            p("label", "str | None", "Visible and accessible group label; omit when the surrounding nav owns the name."),
            p("items / children", "NodeLike", "Links or other already-authorized navigation items."),
        ),
        "A labelled NavGroup emits role=group, aria-label, a visible group label, and stable CSS/data hooks. AppShell nav_groups lowers through the same component.",
        "Keep the surrounding nav landmark labelled and preserve each item’s native focus and link behavior.",
        "Do not use NavGroup to bypass route authorization or nest competing nav landmarks.",
    ),
)


def demo_html(spec: ComponentDoc) -> str:
    name = spec.name
    kind = spec.demo
    sim_by_kind = {
        "refresh": "component-refresh",
        "lazy": "component-lazy",
        "poll": "component-poll",
        "infinite": "component-infinite",
        "pagination": "component-pagination",
        "error": "component-error",
        "form": "component-form",
        "auto-form": "component-auto-form",
        "toast": "component-toast",
        "fragment": "component-fragment",
    }
    sim_by_name = {
        "AppShell": "component-app-shell",
        "MainPanel": "component-main-panel",
        "NavLink": "component-nav-link",
        "HtmxLink": "component-htmx-link",
        "OobHost": "component-oob-host",
        "AttrHost": "component-attr-host",
        "Loading": "component-loading",
        "FormErrors": "component-form-errors",
        "Skeleton": "component-skeleton",
        "ConfirmButton": "component-confirm",
    }
    sim_name = sim_by_kind.get(kind) or sim_by_name.get(name)
    if sim_name is not None:
        return f"__HEDRON_SIM_TABS__:{sim_name}"
    if kind == "button":
        body = '<button class="hdc-button hdc-primary" type="button" data-hdc-action="count">Archive project <span data-hdc-count>0</span></button><p role="status" data-hdc-status>Ready.</p>'
    elif kind == "dialog":
        body = '<div class="hdc-dialog-launch"><span class="hdc-file-icon" aria-hidden="true">R</span><span><strong>Quarterly report</strong><small>Updated 2 minutes ago</small></span><button class="hdc-button" type="button" data-hdc-action="open-dialog">Delete…</button></div><dialog class="hdc-dialog" data-hdc-dialog aria-labelledby="hdc-dialog-title"><header><h2 id="hdc-dialog-title">Delete report?</h2><form method="dialog"><button type="submit" class="hdc-dialog-close" aria-label="Close dialog">×</button></form></header><p>This removes the saved report. The source data is unchanged.</p><footer><button class="hdc-button" type="button" data-hdc-action="close-dialog">Cancel</button><button class="hdc-button hdc-primary" type="button" data-hdc-action="close-dialog">Delete report</button></footer></dialog><p class="hdc-muted" role="status" data-hdc-status>Dialog closed.</p>'
    elif kind == "chat-input":
        body = '<section class="hdc-chat" aria-label="Deployment copilot conversation"><header class="hdc-chat-header"><span class="hdc-chat-avatar" aria-hidden="true">H</span><span><strong>Deployment copilot</strong><small><i aria-hidden="true"></i>Online · simulated assistant</small></span></header><div class="hdc-transcript" id="demo-transcript" role="log" aria-live="polite" data-hdc-transcript><span class="hdc-chat-day">Today</span><article class="hdc-chat-message hdc-chat-assistant"><span class="hdc-chat-avatar" aria-hidden="true">H</span><div><strong>Hedron</strong><p>Your production deployment is ready. Want me to summarize the six completed checks?</p><time datetime="14:32">2:32 PM</time></div></article></div><div class="hdc-chat-prompts" aria-label="Suggested prompts"><span>Try asking</span><button type="button" data-hdc-prompt="Summarize the deployment checks">Summarize checks</button><button type="button" data-hdc-prompt="Show me the rollout risks">Review rollout risks</button></div><form class="hdc-chat-form" data-hdc-chat-form><label class="hdc-visually-hidden" for="hdc-chat-message">Message</label><div class="hdc-chat-composer"><textarea id="hdc-chat-message" name="message" rows="1" required placeholder="Ask about this deployment…"></textarea><div><span class="hdc-chat-hint">Enter to send · Shift+Enter for a new line</span><button class="hdc-chat-send" type="submit"><span>Send</span><svg viewBox="0 0 20 20" aria-hidden="true"><path d="m3 3 14 7-14 7 2.3-6L12 10 5.3 9 3 3Z"/></svg></button></div></div></form><p class="hdc-chat-status" role="status" data-hdc-status>Ready to send.</p></section>'
    elif kind == "file":
        body = '<label class="hdc-file"><span class="hdc-file-icon" aria-hidden="true">↑</span><strong>Upload evidence</strong><small>PDF, PNG, or JPG · up to 10 MB</small><input type="file" accept=".pdf,image/*" data-hdc-file></label><p class="hdc-muted" role="status" data-hdc-status>No file selected.</p>'
    elif kind == "download":
        body = '<div class="hdc-download"><span class="hdc-file-icon" aria-hidden="true">↓</span><span><strong>Service health export</strong><small>service-health.csv · 27 bytes</small></span><a class="hdc-button hdc-primary" href="data:text/csv;charset=utf-8,service%2Cstatus%0Aapi%2Chealthy" download="service-health.csv">Download CSV</a></div>'
    elif kind == "tabs":
        body = '<div class="hdc-tabs" data-hdc-tabs><div role="tablist" aria-label="Account details"><button role="tab" aria-selected="true" data-hdc-tab="overview">Overview</button><button role="tab" aria-selected="false" tabindex="-1" data-hdc-tab="history">History</button></div><section role="tabpanel" data-hdc-panel="overview">Current plan: Pro</section><section role="tabpanel" data-hdc-panel="history" hidden>Upgraded on July 12</section></div>'
    elif kind == "color-mode":
        body = '<form class="hdc-form hdc-theme-control" data-hdc-theme-form><label>Color mode<select data-hdc-theme><option>Light</option><option>Dark</option><option>System</option></select></label><button class="hdc-button" type="submit">Apply</button></form><div class="hdc-theme-swatch" data-hdc-theme-swatch>Preview surface</div><p role="status" data-hdc-status>Light preview selected.</p>'
    elif kind == "data-table":
        body = '<div class="hdc-table-toolbar"><span><strong>Team directory</strong><small>Current workspace members</small></span><label class="hdc-filter">Filter employees<input type="search" placeholder="Search by name or team" data-hdc-filter></label></div><table class="hdc-table"><caption class="hdc-visually-hidden">Employees</caption><thead><tr><th>Name</th><th>Team</th><th>Status</th></tr></thead><tbody data-hdc-rows><tr><td><strong>Ada</strong></td><td>Platform</td><td><span class="hdc-badge hdc-success">Active</span></td></tr><tr><td><strong>Grace</strong></td><td>Compiler</td><td><span class="hdc-badge hdc-success">Active</span></td></tr><tr><td><strong>Alan</strong></td><td>Research</td><td><span class="hdc-badge hdc-warning">Leave</span></td></tr></tbody></table><p class="hdc-muted" role="status" data-hdc-status>Showing 3 employees.</p>'
    elif kind == "data-editor":
        body = '<table class="hdc-editor"><caption>Editable allocation</caption><thead><tr><th>Name</th><th>Allocation</th></tr></thead><tbody><tr><td>Ada</td><td><input type="number" min="0" max="100" value="80" aria-label="Ada allocation" data-hdc-dirty></td></tr><tr><td>Grace</td><td><input type="number" min="0" max="100" value="60" aria-label="Grace allocation" data-hdc-dirty></td></tr></tbody></table><button class="hdc-button hdc-primary" type="button" data-hdc-action="save-editor">Save changes</button><p role="status" data-hdc-status>No unsaved changes.</p>'
    elif kind == "line-chart":
        body = '<figure class="hdc-chart"><figcaption><strong>Monthly revenue</strong><span>Revenue rose from January through June.</span></figcaption><svg viewBox="0 0 360 150" role="img" aria-label="Revenue climbs from 18 to 42 thousand dollars"><path d="M20 125 L82 111 L144 91 L206 99 L268 55 L340 24" fill="none" stroke="currentColor" stroke-width="4"/><g fill="currentColor"><circle cx="20" cy="125" r="4"/><circle cx="82" cy="111" r="4"/><circle cx="144" cy="91" r="4"/><circle cx="206" cy="99" r="4"/><circle cx="268" cy="55" r="4"/><circle cx="340" cy="24" r="4"/></g></svg></figure>'
    elif kind in {"bar-chart", "donut-chart", "scatter-chart"}:
        chart_class = {"bar-chart": "bars", "donut-chart": "donut", "scatter-chart": "scatter"}[
            kind
        ]
        body = f'<figure class="hdc-chart hdc-chart-{chart_class}"><figcaption><strong>{name} output</strong><span>Accessible static preview with a text conclusion.</span></figcaption><div class="hdc-chart-art" role="img" aria-label="Sample chart showing a clear upward pattern"><i></i><i></i><i></i><i></i><i></i></div></figure>'
    elif kind == "auto":
        body = '<dl class="hdc-description"><dt>Region</dt><dd>iad</dd><dt>Healthy</dt><dd><span class="hdc-badge">True</span></dd><dt>Replicas</dt><dd>3</dd></dl>'
    else:
        body = static_demo(spec)
    simulated = kind in {
        "data-editor",
        "color-mode",
        "chat-input",
    }
    note = (
        '<div class="hdc-request" data-hdc-request hidden><span>Simulated HTMX</span><code>GET /fragment → 200</code></div>'
        if simulated
        else ""
    )
    return f'<section class="hedron-component-demo" data-hedron-component-demo="{name}"><div class="hdc-stage">{body}</div>{note}</section>'


def _live_demo_section(spec: ComponentDoc) -> str:
    """Render the Live demo block (tabs for sims, static HTML otherwise)."""
    raw = demo_html(spec)
    if raw.startswith("__HEDRON_SIM_TABS__:"):
        sim_name = raw.split(":", 1)[1]
        return _format_sim_live_demo(sim_name)
    return (
        f"{raw}\n\n"
        "The preview is a local docs simulation (not a running Hedron server). "
        "Interactive demos show a “Simulated HTMX” trace when applicable."
    )


def static_demo(spec: ComponentDoc) -> str:
    name = spec.name
    if spec.group == "landmarks":
        tag = {
            "Header": "header",
            "Main": "main",
            "Nav": "nav",
            "Aside": "aside",
            "Footer": "footer",
            "Section": "section",
        }[name]
        return f'<{tag} class="hdc-landmark"><span>&lt;{tag}&gt;</span><strong>{name} content</strong><p>{spec.summary}</p></{tag}>'
    if name == "Page":
        return '<div class="hdc-browser"><div><i></i><i></i><i></i><span data-hdc-title>Account · Acme</span></div><main><h3>Account</h3><p>Signed in as ada@example.com</p></main></div>'
    if name in {"Head", "Title"}:
        return '<div class="hdc-browser"><div><i></i><i></i><i></i><span>Billing · Acme</span></div><main><dl class="hdc-description"><dt>title</dt><dd>Billing · Acme</dd><dt>description</dt><dd>Manage billing</dd></dl></main></div>'
    if name == "Container":
        return '<div class="hdc-container"><span class="hdc-eyebrow">Account settings</span><h3>Profile</h3><p>This readable block stays centered with a bounded width.</p><a href="#component-demo-result">Edit profile →</a></div>'
    if name == "Stack":
        return '<div class="hdc-stack"><span><b>Build completed</b><small>42 seconds ago</small></span><span><b>Preview deployed</b><small>Environment ready</small></span><span><b>Review requested</b><small>2 teammates notified</small></span></div>'
    if name == "PageHeader":
        return '<header class="hdc-type"><span class="hdc-eyebrow">Operate</span><h2>Pipelines</h2><p class="hdc-muted">Source to destination jobs.</p><div class="hdc-inline"><button class="hdc-button hdc-primary" type="button">New</button></div></header>'
    if name == "SplitView":
        return '<div class="hdc-grid"><span><small>Source</small><strong>orders.csv</strong><em>Ready</em></span><span><small>Destination</small><strong>warehouse</strong><em>Connected</em></span></div>'
    if name == "MasterDetail":
        return '<div class="hdc-grid"><nav aria-label="Master list"><small>Items</small><strong>Alpha</strong><em>Selected</em></nav><section aria-label="Detail panel"><small>Detail</small><strong>Alpha</strong><em>Ready</em></section></div>'
    if name == "FormGrid":
        return '<div class="hdc-grid"><div class="hdc-form"><label for="demo-fg-name">Name</label><input id="demo-fg-name" type="text" value="Ada"></div><div class="hdc-form"><label for="demo-fg-email">Email</label><input id="demo-fg-email" type="email" value="ada@example.com"></div></div>'
    if name == "ActionGroup":
        return '<div class="hdc-inline"><button class="hdc-button" type="button">Cancel</button><button class="hdc-button hdc-primary" type="button">Save</button></div>'
    if name == "SkipLink":
        return '<p><a class="hdc-chip" href="#component-demo-result">Skip to main content</a><span class="hdc-muted">Focusable bypass to the main panel.</span></p>'
    if name == "RequestIndicator":
        return '<div class="hdc-loading" role="status" aria-live="polite"><i></i><span>Saving…</span></div>'
    if name == "ProcessFlow":
        return '<ol class="hdc-list" aria-label="Release pipeline"><li><span>Ingest</span><small>Complete</small></li><li><span>Validate</span><small>In progress</small></li><li><span>Publish</span><small>Not started</small></li></ol>'
    if name == "FlowStep":
        return '<div class="hdc-stack"><span><b>Validate schemas</b><small>In progress · Checking required columns</small></span></div>'
    if name == "ConnectorNode":
        return '<article class="hdc-connector-node"><div class="hdc-inline"><span class="hdc-badge">CSV</span><strong>Source</strong></div><small>Ready · Local upload</small><em>orders.csv</em></article>'
    if name == "ConnectorFlow":
        return '<div class="hdc-connector-flow"><article class="hdc-connector-node"><strong>CSV source</strong><small>Ready</small></article><div class="hdc-connector-track" aria-label="Transfer stages"><span>Transfer</span></div><article class="hdc-connector-node"><strong>Warehouse target</strong><small>Running</small></article></div>'
    if name == "ConnectorTrack":
        return '<div class="hdc-connector-track" aria-label="Transfer stages"><span>Transfer stages</span><small>TLS 1.3 · Encrypted in transit</small></div>'
    if name == "Inline":
        return '<div class="hdc-inline"><span class="hdc-chip">Python</span><span class="hdc-chip">HTMX</span><span class="hdc-chip">FastAPI</span></div>'
    if name == "Grid":
        return '<div class="hdc-grid"><span><small>Latency</small><strong>184 ms</strong><em>↓ 12%</em></span><span><small>Errors</small><strong>0.08%</strong><em>↓ 4%</em></span><span><small>Traffic</small><strong>28.4k</strong><em>↑ 9%</em></span></div>'
    if name == "GridItem":
        return '<div class="hdc-grid"><span><small>Span 2</small><strong>Wide cell</strong><em>GridItem</em></span></div>'
    if name == "Surface":
        return '<div class="hdc-container"><strong>Raised surface</strong><p class="hdc-muted">Presentation tokens only — no application CSS.</p></div>'
    if name == "StyleScope":
        return '<div class="hdc-container" data-hedron-style-scope="true" data-hedron-theme="aurora" data-hedron-color-mode="dark" data-hedron-density="compact"><strong>Scoped panel</strong><p class="hdc-muted">Theme, color mode, and density markers only.</p></div>'
    if name == "Brand":
        return '<div class="hdc-inline"><strong>Hedron</strong><span class="hdc-muted">Brand mark</span></div>'
    if name == "AccountSummary":
        return '<div class="hdc-inline"><strong>Ada Lovelace</strong><span class="hdc-muted">Admin</span></div>'
    if name == "EnvironmentBanner":
        return '<div class="hdc-banner hdc-warning" role="status"><strong>Staging</strong></div>'
    if name == "NavStatus":
        return '<span class="hdc-chip">3 updates</span>'
    if name == "AppFooter":
        return '<footer class="hdc-muted"><span>© Acme</span> · <span>Support</span></footer>'
    if name == "ResourceList":
        return '<div class="hdc-stack"><span><b>Orders</b><small>Open work</small></span><span><b>Sites</b><small>Ready</small></span></div>'
    if name == "ResourceRow":
        return '<div class="hdc-stack"><span><b>North warehouse</b><small>Ready</small></span></div>'
    if name == "Avatar":
        return '<div class="hdc-inline"><span class="hdc-badge" aria-label="Ada Lovelace">AL</span></div>'
    if name == "Identity":
        return '<div class="hdc-inline"><span class="hdc-badge" aria-label="Ada Lovelace">AL</span><span><b>Ada Lovelace</b><small class="hdc-muted">Admin</small></span></div>'
    if name == "Divider":
        return '<div class="hdc-divider-demo"><span>Overview</span><i role="separator" aria-orientation="vertical"></i><span>Activity</span></div>'
    if name == "Heading":
        return '<div class="hdc-type"><span class="hdc-eyebrow">Production</span><h2>Deployment history</h2><p>Heading level two introduces this section.</p></div>'
    if name == "Text":
        return '<div class="hdc-type"><p><strong>Changes saved.</strong> This text is a paragraph that carries the primary message.</p><span class="hdc-muted">Updated just now · inline supporting text</span></div>'
    if name == "Typography":
        return '<div class="hdc-type"><span class="hdc-eyebrow">Title role</span><p><strong>Release readiness</strong></p><span class="hdc-muted">Body role · supporting copy on the type scale.</span></div>'
    if name == "Icon":
        return '<div class="hdc-inline"><span class="hdc-badge hdc-success" role="img" aria-label="Complete">✓</span><span class="hdc-muted">Trusted registry icon · size md</span></div>'
    if name == "StateView":
        return '<div class="hdc-alert" role="status"><strong>Empty</strong><p>No pipelines yet. Create a pipeline to start ingesting data.</p><button class="hdc-button hdc-primary" type="button">New pipeline</button></div>'
    if name in {"Link", "LinkButton"}:
        cls = ' class="hdc-button hdc-primary"' if name == "LinkButton" else ""
        return f'<div class="hdc-link-demo"><span class="hdc-eyebrow">Navigation</span><a{cls} href="#component-demo-result" data-hdc-local-link>{"Create account →" if name == "LinkButton" else "View audit log →"}</a><p id="component-demo-result" class="hdc-muted">A real anchor preserves browser navigation behavior.</p></div>'
    if name == "Image":
        return '<figure class="hdc-image"><div role="img" aria-label="Abstract teal landscape used as a documentation placeholder"><span>Image preview</span></div><figcaption>Meaningful alternative: “The platform team at the meetup.”</figcaption></figure>'
    if name in {"CodeBlock", "CodeViewer"}:
        return '<pre class="hdc-code"><code><span>from</span> hedron <span>import</span> Text\n\nText(<em>"Hello, Hedron"</em>)</code></pre>'
    if name == "JSONViewer":
        return '<pre class="hdc-code"><code>{\n  "job": 42,\n  "status": "complete",\n  "token": "***"\n}</code></pre>'
    if name == "List":
        return '<ol class="hdc-list"><li><span>Create a branch</span><small>Keep the change isolated</small></li><li><span>Add the component</span><small>Compose native semantics</small></li><li><span>Run checks</span><small>Verify behavior and output</small></li></ol>'
    if name == "DescriptionList":
        return '<dl class="hdc-description"><dt>Region</dt><dd>us-east-1</dd><dt>Status</dt><dd><span class="hdc-badge">Healthy</span></dd></dl>'
    if name == "Table":
        return '<table class="hdc-table"><caption>Service health</caption><thead><tr><th>Service</th><th>Status</th></tr></thead><tbody><tr><td><strong>API</strong></td><td><span class="hdc-badge hdc-success">Healthy</span></td></tr><tr><td><strong>Worker</strong></td><td><span class="hdc-badge hdc-success">Healthy</span></td></tr></tbody></table>'
    if name == "Markdown":
        return '<article class="hdc-markdown"><h2>Release notes</h2><ul><li>Safer URLs</li><li>Faster rendering</li></ul><blockquote>Generated from Markdown source.</blockquote></article>'
    if name == "Card":
        return '<article class="hdc-card"><header><span>Latest deployment</span><span class="hdc-badge hdc-success">Ready</span></header><p><strong>api-production</strong><br><span class="hdc-muted">Build completed in 42 seconds.</span></p><footer><a href="#">View deployment →</a></footer></article>'
    if name == "Badge":
        return '<div class="hdc-inline"><span class="hdc-badge">Beta</span><span class="hdc-badge hdc-success">Healthy</span><span class="hdc-badge hdc-warning">Review</span></div>'
    if name == "Alert":
        return '<div class="hdc-alert" role="status"><strong>Saved</strong><p>Your changes were saved.</p></div>'
    if name == "Skeleton":
        return '<div aria-label="Loading preview"><span class="hdc-skeleton"></span><span class="hdc-skeleton"></span><span class="hdc-skeleton hdc-short"></span></div>'
    if name == "IconButton":
        return '<button class="hdc-icon-button" type="button" aria-label="Delete report" data-hdc-action="count"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M6.5 3.5h7M8 3.5V2h4v1.5M5 5.5h10l-.6 11H5.6L5 5.5Zm3 2v6m4-6v6"/></svg></button><p class="hdc-muted" data-hdc-status>Accessible name: Delete report</p>'
    if name == "FormField":
        return '<div class="hdc-form"><label for="demo-email">Email address <b>Required</b></label><input id="demo-email" type="email" aria-describedby="demo-email-help"><small id="demo-email-help">We only use this for receipts.</small></div>'
    if name == "Label":
        return '<div class="hdc-form"><label for="demo-search">Search projects</label><input id="demo-search" type="search" placeholder="Try typing…"></div>'
    if name == "TextInput":
        return '<div class="hdc-form"><label for="demo-text">Email</label><input id="demo-text" type="email" autocomplete="email" placeholder="ada@example.com"></div>'
    if name == "TextArea":
        return '<div class="hdc-form"><label for="demo-notes">Deployment notes</label><textarea id="demo-notes" rows="4" placeholder="Add context…"></textarea></div>'
    if name == "Select":
        return '<div class="hdc-form"><label for="demo-region">Region</label><select id="demo-region"><option>US East</option><option>Europe</option><option>Asia Pacific</option></select></div>'
    if name == "Checkbox":
        return '<label class="hdc-choice hdc-choice-card"><input type="checkbox"><span><strong>Service terms</strong><small>I agree to the acceptable-use and data policies.</small></span></label>'
    if name == "RadioGroup":
        return '<fieldset class="hdc-choices"><legend>Billing plan</legend><label><input type="radio" name="demo-plan" checked> Free</label><label><input type="radio" name="demo-plan"> Pro</label></fieldset>'
    if name == "SubmitButton":
        return '<form data-hdc-form><button class="hdc-button hdc-primary" type="submit">Save profile</button></form><p role="status" data-hdc-status>Ready to save.</p>'
    if name == "FormErrors":
        return '<div class="hdc-errors" role="alert"><strong>Check the form</strong><ul><li>Email is required.</li><li>Choose a billing plan.</li></ul></div>'
    if name == "Loading":
        return '<div class="hdc-loading" role="status" aria-live="polite" aria-busy="true"><i></i><span>Loading account activity…</span></div>'
    if name == "Metric":
        return '<dl class="hdc-metric"><dt>Monthly revenue</dt><dd>$84,200</dd><dd class="hdc-up" aria-label="change plus 8.4 percent">↗ +8.4%</dd></dl>'
    if name == "Progress":
        return '<div class="hdc-progress"><label for="demo-progress">Import progress</label><progress id="demo-progress" value="68" max="100">68%</progress><span>68%</span></div>'
    if name == "Status":
        return '<div class="hdc-status" role="status"><i></i><span>Import complete: 84 records added.</span></div>'
    if name == "Expander":
        return '<details class="hdc-expander"><summary>Advanced settings</summary><p>Configure retry and timeout behavior.</p></details>'
    if name == "Sidebar":
        return '<div class="hdc-shell"><aside aria-label="Workspace"><strong>Acme</strong><a href="#">Overview</a><a href="#">Settings</a></aside><main><h3>Overview</h3><p>Primary page content</p></main></div>'
    if name == "ChatMessage":
        return '<section class="hdc-chat" aria-label="Deployment conversation"><header class="hdc-chat-header"><span class="hdc-chat-avatar" aria-hidden="true">H</span><span><strong>Release assistant</strong><small><i aria-hidden="true"></i>Online</small></span></header><div class="hdc-transcript" role="log"><span class="hdc-chat-day">Today</span><article class="hdc-chat-message hdc-chat-user"><span class="hdc-chat-avatar" aria-hidden="true">Y</span><div><strong>You</strong><p>Is the release ready?</p><time datetime="14:31">2:31 PM</time></div></article><article class="hdc-chat-message hdc-chat-assistant"><span class="hdc-chat-avatar" aria-hidden="true">H</span><div><strong>Hedron</strong><p>Your deployment is ready. All checks passed.</p><time datetime="14:32">2:32 PM · Delivered</time></div></article></div></section>'
    if name == "ConfirmButton":
        return '<button class="hdc-button" type="button" data-hdc-action="confirm-delete">Delete item</button><p class="hdc-muted" role="status" data-hdc-status>Confirmation required before the action runs.</p>'
    if name == "DateInput":
        return '<div class="hdc-form"><label for="demo-date">Due date</label><input id="demo-date" type="date" value="2026-08-05"></div>'
    if name == "DateTimeInput":
        return '<div class="hdc-form"><label for="demo-datetime">Scheduled at</label><input id="demo-datetime" type="datetime-local" value="2026-08-05T14:30"></div>'
    if name == "TimeInput":
        return '<div class="hdc-form"><label for="demo-time">Start time</label><input id="demo-time" type="time" value="09:30"></div>'
    if name == "NumberInput":
        return '<div class="hdc-form"><label for="demo-number">Replicas</label><input id="demo-number" type="number" min="1" max="20" value="3"></div>'
    if name == "Tooltip":
        return '<p>Hover or focus <button class="hdc-button" type="button" title="More info about this control">Help</button> for the accessible title tip.</p>'
    if name == "CircularProgress":
        return '<div class="hdc-progress" role="status" aria-label="Upload 50 percent"><svg viewBox="0 0 36 36" width="48" height="48" aria-hidden="true"><circle cx="18" cy="18" r="15" fill="none" stroke="currentColor" stroke-opacity="0.2" stroke-width="3"/><circle cx="18" cy="18" r="15" fill="none" stroke="currentColor" stroke-width="3" stroke-dasharray="47 94" transform="rotate(-90 18 18)"/></svg><span>50%</span></div>'
    if name == "MenuButton":
        return '<div class="hdc-inline"><button class="hdc-button" type="button" aria-haspopup="menu" aria-expanded="false">More</button><span class="hdc-muted">Opens a menu of actions (Edit · Archive).</span></div>'
    if name == "NavLink":
        return '<nav class="hdc-inline" aria-label="Demo"><a class="hdc-chip" href="#component-demo-result" aria-current="page">Overview</a><a class="hdc-chip" href="#component-demo-result">Settings</a></nav>'
    if name == "ToggleSwitch":
        return '<label class="hdc-choice"><input type="checkbox" role="switch" checked><span><strong>Email digests</strong><small>Weekly summary</small></span></label>'
    if name == "ChipInput":
        return '<div class="hdc-form"><label for="demo-chips">Tags</label><div class="hdc-inline"><span class="hdc-chip">python</span><span class="hdc-chip">htmx</span><input id="demo-chips" type="text" placeholder="Add tag…"></div></div>'
    if name == "RangeInput":
        return '<div class="hdc-form"><label for="demo-range">Volume</label><input id="demo-range" type="range" min="0" max="100" value="40"></div>'
    if name == "ColorInput":
        return '<div class="hdc-form"><label for="demo-color">Accent</label><input id="demo-color" type="color" value="#0f766e"></div>'
    if name == "MultiSelect":
        return '<div class="hdc-form"><label for="demo-multi">Teams</label><select id="demo-multi" multiple size="3"><option selected>Platform</option><option selected>Research</option><option>Design</option></select></div>'
    if name == "OobHost":
        return '<div class="hdc-fragment" id="demo-oob-host"><span class="hdc-badge">OOB host</span><span><strong>#status</strong><small>Stable swap root for out-of-band updates.</small></span></div>'
    if name == "AttrHost":
        return '<div class="hdc-fragment" id="demo-attr-host" data-state="idle"><strong>Attr host</strong><small>Receives attribute-only OOB patches.</small></div>'
    if name == "Carousel":
        return '<div class="hdc-stack" role="region" aria-label="Demo carousel"><strong>Slide 1 · Overview</strong><p class="hdc-muted">Ordered slides with previous/next controls in the live component.</p></div>'
    if name == "Timeline":
        return '<ol class="hdc-list"><li><span>Deploy started</span><small>14:01</small></li><li><span>Checks passed</span><small>14:04</small></li><li><span>Live</span><small>14:05</small></li></ol>'
    if name == "Audio":
        return '<div class="hdc-download"><span class="hdc-file-icon" aria-hidden="true">♪</span><span><strong>Audio player</strong><small>Requires a SafeUrl source in the real component.</small></span></div>'
    if name == "Video":
        return '<div class="hdc-download"><span class="hdc-file-icon" aria-hidden="true">▶</span><span><strong>Video player</strong><small>Requires a SafeUrl source in the real component.</small></span></div>'
    if name == "CameraCapture":
        return '<label class="hdc-file"><span class="hdc-file-icon" aria-hidden="true">C</span><strong>Camera capture</strong><small>capture=environment · permission/retention policy required</small><input type="file" accept="image/*" capture="environment"></label>'
    if name == "MicrophoneCapture":
        return '<label class="hdc-file"><span class="hdc-file-icon" aria-hidden="true">M</span><strong>Microphone capture</strong><small>capture=user · permission/retention policy required</small><input type="file" accept="audio/*" capture="user"></label>'
    if name == "GeolocationButton":
        return '<button class="hdc-button" type="button">Share location</button><p class="hdc-muted">Spoofable form fields — not authorization.</p>'
    if name == "PageIcon":
        return '<div class="hdc-inline"><span class="hdc-file-icon" aria-hidden="true">★</span><span><strong>Favicon helper</strong><small>Emits link/image metadata for the document head.</small></span></div>'
    if name == "Spacer":
        return (
            '<div class="hdc-stack"><span>Above</span>'
            '<div class="hedron-spacer" data-hedron-layout="spacer" data-hedron-gap="lg" '
            'data-hedron-spacer-axis="block" aria-hidden="true"></div>'
            "<span>Below</span></div>"
        )
    if name == "Pills":
        return '<div class="hdc-inline"><span class="hdc-chip">All</span><span class="hdc-chip">Active</span><span class="hdc-chip">Archived</span></div>'
    if name == "SegmentedControl":
        return '<div class="hdc-inline" role="group" aria-label="View"><button class="hdc-button hdc-primary" type="button">List</button><button class="hdc-button" type="button">Board</button></div>'
    if name == "RatingInput":
        return '<div class="hdc-form" role="group" aria-label="Rating"><span aria-hidden="true">★★★★☆</span><span class="hdc-muted">4 of 5</span></div>'
    if name == "Popover":
        return '<button class="hdc-button" type="button" aria-expanded="false">Details</button><p class="hdc-muted">Popover content appears on activation in the live component.</p>'
    if name == "Help":
        return '<button class="hdc-icon-button" type="button" aria-label="Help" title="What does this field mean?">?</button>'
    if name == "ClipboardCopy":
        return '<button class="hdc-button" type="button" data-hdc-action="show-toast">Copy API key</button><p class="hdc-muted" role="status">Copies a provided string to the clipboard.</p>'
    return f'<div class="hdc-result"><strong>{name}</strong><span>{spec.summary}</span></div>'


_PARAM_MEANINGS: dict[str, str] = {
    "*nodes": "Positional child nodes.",
    "nodes": "Positional child nodes.",
    "children": "Keyword alternative for child nodes; combines with positional children.",
    "name": "Form control `name` submitted with the request.",
    "label": "Accessible label text shown to users.",
    "legend": "Accessible group legend for related controls.",
    "id": "Optional DOM `id`.",
    "class_": "Optional CSS class string (`class` in HTML).",
    "mark": "Optional stable test mark (`data-hedron-mark`).",
    "src": "Media or document URL (`SafeUrl` preferred for untrusted input).",
    "href": "Optional navigation URL when the control is a link.",
    "alt": "Required accessible alternative text for the image.",
    "title": "Accessible title (document, iframe, dialog, or media).",
    "text": "Plain text content.",
    "body": "Body content node or string.",
    "value": "Current control value.",
    "values": "Selected or seeded multi-values.",
    "options": "Choice list as `(value, label)` pairs (or plain strings where accepted).",
    "placeholder": "Hint text shown when the control is empty.",
    "required": "Whether the control must be filled before submit.",
    "disabled": "Whether the control is non-interactive.",
    "checked": "Whether a boolean control starts checked.",
    "accept": "File `accept` filter (MIME / extension list).",
    "capture": "Media capture facing mode (`user` or `environment`).",
    "min": "Minimum allowed value.",
    "max": "Maximum allowed value.",
    "maximum": "Upper bound for progress or rating scales.",
    "step": "Stepping interval for numeric / temporal inputs.",
    "placement": "Layout placement for the dock.",
    "slides": "Ordered carousel slides (nodes or `(label, node)` pairs).",
    "entries": "Timeline entries as `(when, title, body)` or mapping records.",
    "items": "Gallery items (`GalleryItem` or mapping records).",
    "lightbox": "Whether clicking an item opens a lightbox details UI.",
    "confirm": "Confirmation prompt text shown before the action runs.",
    "type": "Native button `type` (`button`, `submit`, or `reset`).",
    "variant": "Visual / semantic variant for the control.",
    "mode": "Presentation mode for the disclosure surface.",
    "open": "Whether the inspector starts expanded.",
    "for_": "Optional `for` / control association id.",
    "indeterminate": "Whether progress is indeterminate (ignores `value`).",
    "controls": "Whether native media controls are shown.",
    "autoplay": "Whether media attempts autoplay (browser-gated).",
    "loop": "Whether media loops.",
    "muted": "Whether media starts muted.",
    "preload": "Native media `preload` hint.",
    "poster": "Optional video poster image URL.",
    "tracks": "Optional track elements or track mappings.",
    "allow_external": "Allow non-same-origin / non-asset URLs when True.",
    "allow_remote": "Allow remote iframe sources when True.",
    "sandbox": "IFrame `sandbox` token string (empty = fully sandboxed).",
    "allow": "Optional iframe `allow` feature policy string.",
    "referrerpolicy": "IFrame referrer policy.",
    "width": "Optional width hint (CSS length or pixels).",
    "height": "Optional height hint (CSS length or pixels).",
    "size": "Spacer size (CSS length).",
    "axis": "Spacer axis (`block`, `inline`, or `both`).",
    "center": "Map center as `(lat, lon)`.",
    "zoom": "Initial map zoom level.",
    "tiles": "Optional tile URL template (must pass allowlist checks).",
    "tile_allowlist": "Allowed tile URL prefixes / hosts.",
    "attribution": "Map attribution text.",
    "markers": "Marker specs, mappings, or range tick markers.",
    "geojson": "GeoJSON mapping or `GeoJSONLayer` (feature-capped).",
    "max_features": "Maximum GeoJSON features rendered.",
    "latex": "LaTeX source rendered safely as MathML/text fallback.",
    "display": "Whether math uses display (block) mode.",
    "lat_name": "Form field name for latitude.",
    "lon_name": "Form field name for longitude.",
    "accuracy_name": "Form field name for reported accuracy.",
    "overflow_label": "Accessible label for overflow / more-actions control.",
    "aria_describedby": "Optional `aria-describedby` id reference.",
    "aria_invalid": "Optional `aria-invalid` value.",
    "aria_required": "Optional `aria-required` value.",
}


def _params_are_stub(params: tuple[tuple[str, str, str], ...]) -> bool:
    names = [name for name, _, _ in params]
    return not names or names == ["mark"]


def _annotation_text(annotation: object) -> str:
    if annotation is inspect.Parameter.empty:
        return "Any"
    text = str(annotation)
    text = text.replace("typing.", "")
    for prefix in (
        "hedron_core.nodes.",
        "hedron_core.urls.",
        "hedron.builtins.",
        "hedron_core.",
        "hedron.",
    ):
        text = text.replace(prefix, "")
    return text.replace("NoneType", "None")


def introspect_constructor(name: str) -> tuple[str, tuple[tuple[str, str, str], ...]] | None:
    """Return live ``(signature, params)`` for a public component, or ``None``."""
    try:
        import hedron as hedron_pkg
    except ImportError:
        return None
    cls = getattr(hedron_pkg, name, None)
    if cls is None or not callable(getattr(cls, "__init__", None)):
        return None
    try:
        sig = inspect.signature(cls.__init__)
    except (TypeError, ValueError):
        return None
    rows: list[tuple[str, str, str]] = []
    for pname, param in sig.parameters.items():
        if pname == "self":
            continue
        if param.kind is inspect.Parameter.VAR_KEYWORD:
            continue
        if param.kind is inspect.Parameter.VAR_POSITIONAL:
            key = f"*{pname}"
            rows.append(
                (
                    key,
                    _annotation_text(param.annotation),
                    _PARAM_MEANINGS.get(key, _PARAM_MEANINGS.get(pname, "Positional child nodes.")),
                )
            )
            continue
        type_ = _annotation_text(param.annotation)
        meaning = _PARAM_MEANINGS.get(pname, "Constructor parameter.")
        if param.default is not inspect.Parameter.empty:
            meaning = f"{meaning} Default: `{param.default!r}`."
        rows.append((pname, type_, meaning))
    if not rows:
        return None
    rendered = str(sig).replace("(self, ", "(").replace("(self)", "()")
    if rendered.endswith(" -> None"):
        rendered = rendered[: -len(" -> None")]
    signature = f"{name}{rendered}"
    return signature, tuple(rows)


def resolve_spec(spec: ComponentDoc) -> ComponentDoc:
    """Fill stub constructor tables from the live ``__init__`` signature."""
    if not _params_are_stub(spec.params):
        return spec
    introspected = introspect_constructor(spec.name)
    if introspected is None:
        return spec
    signature, params = introspected
    return ComponentDoc(
        name=spec.name,
        group=spec.group,
        summary=spec.summary,
        signature=signature,
        example=spec.example,
        params=params,
        detail=spec.detail,
        a11y=spec.a11y,
        pitfall=spec.pitfall,
        package=spec.package,
        server=spec.server,
        demo=spec.demo,
    )


def page_text(spec: ComponentDoc) -> str:
    spec = resolve_spec(spec)
    params = "\n".join(
        f"| `{name}` | `{type_}` | {meaning} |" for name, type_, meaning in spec.params
    )
    mode_name = "RenderMode.PAGE" if spec.name == "Page" else "RenderMode.FRAGMENT"
    mode = f"`{mode_name}`"
    simulated = spec.demo in {
        "form",
        "auto-form",
        "refresh",
        "lazy",
        "poll",
        "infinite",
        "pagination",
        "error",
        "toast",
        "fragment",
        "data-editor",
        "color-mode",
        "chat-input",
    } or spec.name in {
        "AppShell",
        "MainPanel",
        "NavLink",
        "HtmxLink",
        "OobHost",
        "AttrHost",
        "Loading",
        "FormErrors",
        "Skeleton",
        "ConfirmButton",
    }
    known_imports = sorted(
        {
            candidate.name
            for candidate in COMPONENTS
            if re.search(rf"\b{candidate.name}\b", spec.example)
        }
    )
    if "ColorMode." in spec.example:
        known_imports.append("ColorMode")
    if "html." in spec.example:
        known_imports.append("html")
    imports = ", ".join(sorted(set(known_imports)))
    server_note = (
        "This component can initiate or represent a backend interaction. The live documentation intercepts that interaction with JavaScript and shows the same pending, success, or replacement states without making a real request. In an application, keep the URL, authorization, validation, and returned fragment on the server; JavaScript is only progressive enhancement."
        if simulated
        else "This component's core behavior is server-rendered HTML and does not require a browser runtime. The preview is ordinary semantic HTML, so keyboard, form, link, and disclosure behavior comes from the platform."
    )
    if spec.name in {"Chart", "LineChart", "AreaChart", "BarChart", "ScatterChart"}:
        server_note = (
            "The server-rendered figure, summary, and table remain useful without JavaScript. "
            "When the `hedron_charts` plugin assets load, the local `hedron-chart` module "
            "progressively enhances that fallback and remounts safely after HTMX swaps."
        )
    elif spec.name in {"PlotlyChart", "AltairChart"}:
        server_note = (
            "The server emits bounded, non-executable JSON and accessible metadata. The "
            "interactive visual requires the corresponding vendored browser host/runtime; "
            "these adapters remain Experimental and fail closed when the runtime is unavailable."
        )
    if simulated or spec.server not in {"No", "Page response"}:
        mutation_note = (
            "Mutating flows must use POST, validate CSRF, authorize on the server, "
            "re-validate typed input, and return a bounded fragment. GET remains safe "
            "and repeatable; native submit should still work without HTMX."
        )
    elif spec.group in {"charts", "data"} or "charts" in spec.package or "data" in spec.package:
        mutation_note = (
            f"`{spec.name}` renders data the server already prepared. Keep queries, "
            "authorization, and redaction on the route or data source — do not treat "
            "the component as a place for side effects."
        )
    elif spec.group in {"forms", "controls", "interaction"}:
        mutation_note = (
            f"`{spec.name}` participates in interaction markup. Pair it with an explicit "
            "`@action` / `@component` POST (and CSRF) when the control mutates state."
        )
    else:
        mutation_note = (
            f"`{spec.name}` is primarily presentational; keep any mutation on an explicit "
            "action or component route."
        )
    optional = (
        _optional_install_text(spec.package)
        if "[" in spec.package or spec.package.startswith("hedron-")
        else ""
    )
    is_charts = "charts" in spec.package
    workspace_only = ""
    import_module = "hedron_charts" if is_charts else "hedron"
    distribution = f"`{spec.package}`"
    related = (
        "[Charts guide](../guides/charts-and-htmx.md) · "
        "[Charts API](../api/CHART.md) · "
        "[hedron-charts package](../packages/hedron-charts.md)"
        if is_charts
        else "[All component demos](index.md) · [Built-in API](../api/BUILT_INS.md) · [Testing](../guides/testing.md)"
    )
    phase_note = (
        "\n!!! note \"Phase 0.61 in-tree preview\"\n\n"
        "    This additive contract is implemented in-tree for Phase 0.61. It is not part of "
        "the published 0.60.x Supported surface until "
        "[RELEASE_0_61](https://github.com/eddiethedean/hedron/blob/main/docs/acceptance/RELEASE_0_61.md) is signed off.\n"
        if spec.name in _PHASE_061_COMPONENTS
        else ""
    )
    return f"""---
title: {spec.name}
description: {spec.summary}
---

# `{spec.name}`

{spec.summary}{phase_note}

| | |
|---|---|
| Import | `from {import_module} import {spec.name}` |
| Distribution | {distribution} |
| Backend activity | {spec.server} |
| Normal render mode | {mode} |

## Live demo

{_live_demo_section(spec)}{optional}

## Basic use

```python
{workspace_only}from {import_module} import {imports}

component = {spec.example}
```

Compose under `Page` for full documents, or return from a fragment route for HTMX swaps.

## How it works

{spec.detail}

{server_note}

## Constructor and parameters

```python
{spec.signature}
```

| Parameter | Type | Meaning |
|---|---|---|
{params}

## Composition and backend behavior

Keep `{spec.name}` at the smallest semantic boundary. Fragment routes should return only
the replaced region and preserve stable target IDs across success, validation, empty,
loading, and error responses.

{mutation_note}

## Accessibility

{spec.a11y}

## Security

Escaping and `SafeUrl` / `TrustedHtml` are framework concerns; authorization and data
exposure remain application code. Redact secrets before rendering.

## Common mistakes

- {spec.pitfall}
- Do not copy docs-preview JavaScript into an application server.

## Testing

```python
from hedron import RenderMode, render

result = render(component, mode={mode_name})
assert result.html
assert not result.diagnostics
```

{related}
"""


def index_text() -> str:
    rows = []
    for key, (title, description) in GROUPS.items():
        members = [spec for spec in COMPONENTS if spec.group == key]
        links = " · ".join(f"[`{spec.name}`]({spec.slug}.md)" for spec in members)
        rows.append(f"## {title}\n\n{description}\n\n{links}")
    return (
        """---
hide:
  - toc
---

# Component demos

Every public Hedron component has a dedicated page (searchable; linked from the category
pages below). The left nav lists **categories**, not every component — start with the
table of ten, then open a group. Static components use real semantic HTML. Features that
normally call an HTMX endpoint use a clearly labelled JavaScript simulation so loading,
replacement, retry, paging, polling, editing, and validation remain usable on the hosted
documentation site.

!!! info "What the simulation does"

    JavaScript supplies deterministic in-browser responses only inside these docs previews. Production examples keep authentication, authorization, CSRF, validation, persistence, caching, and fragment rendering on the Python server. Each interactive page explains that boundary.

## Start with these 10

| Component | Why |
|---|---|
| [`Page`](page.md) / [`Text`](text.md) | First full document |
| [`Stack`](stack.md) / [`Card`](card.md) | Layout and surfaces |
| [`Form`](form.md) / [`TextInput`](text-input.md) / [`SubmitButton`](submit-button.md) | Classic forms |
| [`Button`](button.md) / [`RefreshButton`](refresh-button.md) | Commands and HTMX refresh |
| [`DataTable`](data-table.md) | Tabular data (`hedron[data]`) |

Then browse the groups below. Golden path:
[HTMX interactions](../guides/htmx-interactions.md) →
[Minimal form](../guides/minimal-form.md).

Use the pages below to choose a component, inspect its output, understand its constructor, and test its accessibility and backend contract.

"""
        + "\n\n".join(rows)
        + "\n"
    )


def group_index_text(key: str) -> str:
    title, description = GROUPS[key]
    members = [spec for spec in COMPONENTS if spec.group == key]
    cards = "\n".join(f"- [`{spec.name}`]({spec.slug}.md) — {spec.summary}" for spec in members)
    return f"# {title}\n\n{description}\n\n{cards}\n"


def expected_files() -> dict[Path, str]:
    files = {DOCS / "index.md": index_text()}
    for key in GROUPS:
        files[DOCS / f"{key}.md"] = group_index_text(key)
    for spec in COMPONENTS:
        files[DOCS / f"{spec.slug}.md"] = page_text(resolve_spec(spec))
    return files


def _literal_all(relative_path: str) -> set[str]:
    tree = ast.parse((ROOT / relative_path).read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets
        ):
            value = ast.literal_eval(node.value)
            return {str(item) for item in value}
    raise RuntimeError(f"No literal __all__ found in {relative_path}")


def _direct_component_classes(*relative_paths: str) -> set[str]:
    names: set[str] = set()
    for relative_path in relative_paths:
        tree = ast.parse((ROOT / relative_path).read_text())
        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or node.name.startswith("_"):
                continue
            for base in node.bases:
                root = base.value if isinstance(base, ast.Subscript) else base
                if isinstance(root, ast.Name) and root.id == "Component":
                    names.add(node.name)
                    break
    return names


def discover_builtin_components() -> set[str]:
    """Read the public built-in sources without importing optional dependencies."""
    # Vocabulary constants and non-Component models are exported for authors but
    # are not dedicated component-demo pages.
    non_components = {
        "APPEARANCES",
        "BREAKPOINTS",
        "CONTENT_WIDTHS",
        "DENSITIES",
        "ELEVATIONS",
        "EMPHASES",
        "GAPS",
        "GAP_TOKENS",
        "OVERFLOW_MODES",
        "PADDINGS",
        "RESPONSIVE_POLICIES",
        "SHAPES",
        "SIZES",
        "STATE_KINDS",
        "TRACKS",
        "TYPOGRAPHY_ROLES",
        "WIDTHS",
        "TableColumn",  # Pydantic model for Table metadata, not a Component
        "ThemePreference",
        "action_attrs",
        "oob_swap",
        "resolve_theme_preference",
        "theme_boot_asset",
        "theme_markers",
    }
    names = _literal_all("packages/hedron-core/src/hedron_core/builtins/__init__.py")
    names |= {
        name
        for name in _literal_all("packages/hedron/src/hedron/builtins/__init__.py")
        if name not in non_components
    }
    names -= non_components
    names |= _direct_component_classes(
        "packages/hedron-core/src/hedron_core/auto/widget.py",
        "packages/hedron-core/src/hedron_core/color_mode.py",
        "packages/hedron/src/hedron/builtins/files.py",
        "packages/hedron/src/hedron/builtins/chat.py",
        "packages/hedron/src/hedron/content.py",
        "packages/hedron-data/src/hedron_data/table.py",
        "packages/hedron-data/src/hedron_data/editor.py",
        "packages/hedron-charts/src/hedron_charts/components.py",
        "packages/hedron-charts/src/hedron_charts/element.py",
    )
    return names


def check_inventory() -> list[str]:
    documented = {spec.name for spec in COMPONENTS}
    implemented = discover_builtin_components()
    failures: list[str] = []
    if missing := sorted(implemented - documented):
        failures.append(f"built-in components without a dedicated doc page: {', '.join(missing)}")
    if stale := sorted(documented - implemented):
        failures.append(
            f"component doc entries without an implemented built-in: {', '.join(stale)}"
        )
    if duplicates := sorted(
        name for name in documented if sum(spec.name == name for spec in COMPONENTS) > 1
    ):
        failures.append(f"duplicate component doc entries: {', '.join(duplicates)}")
    unresolved = sorted(
        spec.name
        for spec in COMPONENTS
        if _params_are_stub(spec.params) and _params_are_stub(resolve_spec(spec).params)
    )
    if unresolved:
        failures.append(
            "stub constructor params could not be introspected: " + ", ".join(unresolved)
        )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when generated docs differ")
    args = parser.parse_args()
    expected = expected_files()
    failures: list[str] = check_inventory()
    for path, content in expected.items():
        current = path.read_text() if path.exists() else ""
        if current == content:
            continue
        if args.check:
            diff = "".join(
                difflib.unified_diff(
                    current.splitlines(True),
                    content.splitlines(True),
                    fromfile=str(path),
                    tofile=f"{path} (generated)",
                    n=2,
                )
            )
            failures.append(diff or f"missing {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            print(f"wrote {path.relative_to(ROOT)}")
    if args.check:
        extras = sorted(path for path in DOCS.glob("*.md") if path not in expected)
        if extras:
            failures.append(
                "unexpected component doc pages: "
                + ", ".join(str(path.relative_to(ROOT)) for path in extras)
            )
    if failures:
        print("\n".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
