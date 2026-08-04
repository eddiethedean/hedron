"""HDJ v1 prologue parsing, isolated loading, and conservative static analysis."""

from __future__ import annotations

import hashlib
import re
import tomllib
from collections.abc import Iterable
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urlsplit

from jinja2 import BaseLoader, Environment, TemplateNotFound, nodes

from hedron_core import (
    Diagnostic,
    DiagnosticSeverity,
    HedronError,
    SourceSpan,
)
from hedron_core.diagnostics import error, make_diagnostic
from hedron_jinja.contracts import TemplateDeclaration, TemplateKind, validate_template_name

FORMAT_VERSION = 1
MAX_PROLOGUE_BYTES = 65_536
MAX_PROLOGUE_LINES = 256

INVARIANT_FEATURES = frozenset({"web.html", "jinja.core"})
PROFILE_FEATURES: dict[str, frozenset[str]] = {
    "minimal": INVARIANT_FEATURES,
    "standard": INVARIANT_FEATURES
    | frozenset(
        {
            "web.css",
            "jinja.composition",
            "hedron.components",
            "hedron.assets",
            "hedron.routes",
            "hedron.forms",
            "hedron.styles",
            "hedron.themes",
            "hedron.interaction",
            "htmx.core",
            "htmx.history",
            "htmx.oob",
            "browser.modules",
        }
    ),
    "full": INVARIANT_FEATURES
    | frozenset(
        {
            "web.css",
            "web.javascript",
            "web.custom-elements",
            "jinja.composition",
            "hedron.components",
            "hedron.assets",
            "hedron.routes",
            "hedron.forms",
            "hedron.styles",
            "hedron.themes",
            "hedron.interaction",
            "htmx.core",
            "htmx.history",
            "htmx.oob",
            "htmx.events",
            "htmx.advanced-selectors",
            "htmx.view-transitions",
            "browser.modules",
        }
    ),
    "custom": INVARIANT_FEATURES,
}

EXPLICIT_FEATURES = frozenset(
    {
        "jinja.i18n",
        "jinja.do",
        "jinja.loop-controls",
        "jinja.async",
        "hedron.data",
        "hedron.charts",
    }
)
KNOWN_FEATURES = frozenset().union(*PROFILE_FEATURES.values()) | EXPLICIT_FEATURES
DEFERRED_V1_FEATURES = frozenset({"jinja.dynamic-dependencies", "jinja.foreign"})

BUILTIN_CAPABILITIES = frozenset(
    {
        "browser.inline-style",
        "browser.inline-script",
        "browser.head-mutation",
        "htmx.eval",
        "htmx.response-scripts",
    }
)
_PROVIDER_FEATURE_RE = re.compile(r"^(?:jinja|htmx)\.extension:[a-z0-9][a-z0-9._-]*$")
_NETWORK_CAPABILITY_RE = re.compile(
    r"^network\.(?:script|style|image|connect|frame|font|media)-origin:(https://[^/]+)$"
)
_LOGICAL_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:/-]*$")
_REGION_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]*$")
_TAG_RE = re.compile(r"<\s*([A-Za-z][A-Za-z0-9:-]*)\b")
_OUTPUT_RE = re.compile(r"{{(?P<expr>.*?)}}", re.DOTALL)


@dataclass(frozen=True, slots=True)
class ParsedHdjSource:
    declaration: TemplateDeclaration
    raw: str
    body: str
    compiled: str


@dataclass(frozen=True, slots=True)
class DependencyEdge:
    relation: str
    target: str | None
    line: int


def _source_error(name: str, line: int, message: str, remediation: str) -> HedronError:
    return error(
        "HED-JINJA-0018",
        title="Invalid HDJ source prologue",
        explanation=message,
        remediation=remediation,
        span=SourceSpan(path=name, start_line=line),
    )


def parse_hdj_source(name: str, raw: str) -> ParsedHdjSource:
    validate_template_name(name)
    if not name.endswith(".hdj"):
        raise _source_error(
            name, 1, "HDJ loaders accept only '.hdj' sources.", "Rename the source."
        )
    if raw.startswith("\ufeff") or not (raw.startswith("---hdj\n") or raw.startswith("---hdj\r\n")):
        raise _source_error(
            name,
            1,
            "An HDJ source must begin at character zero with `---hdj` and a newline.",
            "Remove a BOM or leading content and add the mandatory prologue.",
        )

    lines = raw.splitlines(keepends=True)
    closing_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip("\r\n") == "---":
            closing_index = index
            break
        if index >= MAX_PROLOGUE_LINES:
            raise _source_error(
                name,
                index + 1,
                f"The HDJ prologue exceeds {MAX_PROLOGUE_LINES} lines.",
                "Keep declarations concise and move executable content into the template body.",
            )
    if closing_index is None:
        raise _source_error(name, 1, "The HDJ prologue has no closing `---` line.", "Add it.")

    prologue_text = "".join(lines[1:closing_index])
    if len(prologue_text.encode("utf-8")) > MAX_PROLOGUE_BYTES:
        raise _source_error(
            name,
            1,
            f"The HDJ prologue exceeds {MAX_PROLOGUE_BYTES} UTF-8 bytes.",
            "Reduce the static declaration size.",
        )
    try:
        data = tomllib.loads(prologue_text)
    except tomllib.TOMLDecodeError as exc:
        raise _source_error(
            name,
            1 + (getattr(exc, "lineno", 1) or 1),
            f"Invalid TOML: {exc}",
            "Correct the static TOML prologue.",
        ) from exc

    allowed_keys = {"version", "kind", "profile", "features", "requires", "assets", "regions"}
    unknown_keys = set(data) - allowed_keys
    if unknown_keys:
        raise _source_error(
            name,
            2,
            f"Unknown format-v1 keys: {', '.join(sorted(unknown_keys))}.",
            "Remove misspelled or unsupported keys.",
        )
    missing_keys = {"version", "kind", "profile"} - set(data)
    if missing_keys:
        raise _source_error(
            name,
            2,
            f"Missing required keys: {', '.join(sorted(missing_keys))}.",
            "Declare version, kind, and profile.",
        )
    version = data["version"]
    if isinstance(version, bool) or not isinstance(version, int) or version != FORMAT_VERSION:
        raise _source_error(
            name, 2, "Only integer HDJ version 1 is supported.", "Set `version = 1`."
        )
    try:
        kind = TemplateKind(data["kind"])
    except (TypeError, ValueError) as exc:
        raise _source_error(
            name, 2, "`kind` must be page, fragment, or library.", "Correct it."
        ) from exc
    profile = data["profile"]
    if not isinstance(profile, str) or profile not in PROFILE_FEATURES:
        raise _source_error(
            name, 2, "`profile` must be minimal, standard, full, or custom.", "Correct it."
        )

    features = _string_tuple(name, data, "features")
    requires = _string_tuple(name, data, "requires")
    assets = _string_tuple(name, data, "assets")
    regions = _string_tuple(name, data, "regions")
    for feature in features:
        if feature in DEFERRED_V1_FEATURES:
            raise _source_error(
                name,
                2,
                f"Feature {feature!r} is intentionally deferred from HDJ format v1.",
                "Use static .hdj dependencies in 0.9.",
            )
        if feature not in KNOWN_FEATURES and not _PROVIDER_FEATURE_RE.fullmatch(feature):
            raise _source_error(
                name, 2, f"Unknown feature ID {feature!r}.", "Use a format-v1 feature ID."
            )
    for capability in requires:
        if capability not in BUILTIN_CAPABILITIES and not _valid_network_capability(capability):
            raise _source_error(
                name,
                2,
                f"Unknown or context-free capability ID {capability!r}.",
                "Use a built-in capability or a purpose-specific network origin.",
            )
    for asset in assets:
        if not _LOGICAL_ID_RE.fullmatch(asset):
            raise _source_error(
                name, 2, f"Invalid asset ID {asset!r}.", "Use a canonical logical ID."
            )
    for region in regions:
        if not _REGION_RE.fullmatch(region):
            raise _source_error(
                name, 2, f"Invalid region ID {region!r}.", "Use a stable HTML-compatible ID."
            )

    effective = PROFILE_FEATURES[profile] | frozenset(features)
    body_start_line = closing_index + 2
    body = "".join(lines[closing_index + 1 :])
    guard_ending = "\r\n" if lines[closing_index].endswith("\r\n") else "\n"
    # A spanning Jinja comment preserves the original line numbers without
    # emitting the prologue's padding as leading response whitespace.
    compiled = (
        "{#\n" + ("\n" * (closing_index - 1)) + "#}{% hdj_guard %}{#" + guard_ending + "#}" + body
    )
    declaration = TemplateDeclaration(
        name=name,
        format_version=version,
        kind=kind,
        profile=profile,
        declared_features=frozenset(features),
        effective_features=effective,
        requires=frozenset(requires),
        assets=assets,
        regions=regions,
        source_digest=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        body_start_line=body_start_line,
    )
    return ParsedHdjSource(declaration=declaration, raw=raw, body=body, compiled=compiled)


def _string_tuple(name: str, data: dict[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key, [])
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise _source_error(
            name, 2, f"`{key}` must be an array of non-empty strings.", "Correct its type."
        )
    if len(value) != len(set(value)):
        raise _source_error(name, 2, f"`{key}` contains duplicates.", "List each value once.")
    return tuple(value)


def _valid_network_capability(capability: str) -> bool:
    match = _NETWORK_CAPABILITY_RE.fullmatch(capability)
    if match is None:
        return False
    parts = urlsplit(match.group(1))
    return bool(
        parts.scheme == "https"
        and parts.hostname
        and parts.username is None
        and parts.password is None
        and not parts.path
        and not parts.query
        and not parts.fragment
    )


class HdjLoader(BaseLoader):
    """A loader boundary that accepts HDJ sources only and strips their prologues."""

    def __init__(self, delegate: BaseLoader) -> None:
        self.delegate = delegate

    def get_parsed_source(self, environment: Environment, template: str) -> ParsedHdjSource:
        validate_template_name(template)
        if not template.endswith(".hdj"):
            raise TemplateNotFound(template, "HDJ loader accepts only .hdj sources")
        raw, _filename, _uptodate = self.delegate.get_source(environment, template)
        return parse_hdj_source(template, raw)

    def get_source(self, environment: Environment, template: str) -> tuple[str, str | None, Any]:
        validate_template_name(template)
        if not template.endswith(".hdj"):
            raise TemplateNotFound(template, "HDJ loader accepts only .hdj sources")
        raw, filename, uptodate = self.delegate.get_source(environment, template)
        parsed = parse_hdj_source(template, raw)
        return parsed.compiled, filename, uptodate

    def list_templates(self) -> list[str]:
        return sorted(name for name in self.delegate.list_templates() if name.endswith(".hdj"))


def dependency_edges(
    environment: Environment, parsed: ParsedHdjSource
) -> tuple[DependencyEdge, ...]:
    ast = environment.parse(parsed.compiled, name=parsed.declaration.name)
    edges: list[DependencyEdge] = []
    for node in ast.find_all((nodes.Extends, nodes.Include, nodes.Import, nodes.FromImport)):
        if isinstance(node, nodes.Extends):
            relation = "extends"
        elif isinstance(node, nodes.Include):
            relation = "include"
        else:
            relation = "import"
        target_expr = node.template
        targets = _constant_template_names(target_expr)
        if targets is None:
            edges.append(DependencyEdge(relation, None, node.lineno))
        else:
            edges.extend(DependencyEdge(relation, target, node.lineno) for target in targets)
    return tuple(edges)


def _constant_template_names(expr: nodes.Expr) -> tuple[str, ...] | None:
    if isinstance(expr, nodes.Const):
        if isinstance(expr.value, str):
            return (expr.value,)
        if isinstance(expr.value, (tuple, list)) and all(isinstance(v, str) for v in expr.value):
            return tuple(expr.value)
        return None
    if isinstance(expr, (nodes.Tuple, nodes.List)):
        values: list[str] = []
        for item in expr.items:
            if not isinstance(item, nodes.Const) or not isinstance(item.value, str):
                return None
            values.append(item.value)
        return tuple(values)
    return None


def observed_features(environment: Environment, parsed: ParsedHdjSource) -> frozenset[str]:
    body = _mask_jinja_comments(parsed.body)
    ast = environment.parse(parsed.compiled, name=parsed.declaration.name)
    observed = set(INVARIANT_FEATURES)
    if any(
        ast.find_all(
            (
                nodes.Extends,
                nodes.Include,
                nodes.Import,
                nodes.FromImport,
                nodes.Macro,
                nodes.CallBlock,
                nodes.Block,
            )
        )
    ):
        observed.add("jinja.composition")
    if re.search(r"{%[-+]?\s*hedron(?:\s|$)", body):
        observed.add("hedron.components")
    if parsed.declaration.assets or re.search(
        r"{%[-+]?\s*hedron_asset\b|\bhdj\.asset_url\s*\(|\|\s*hedron_asset_url\b", body
    ):
        observed.add("hedron.assets")
    if re.search(r"\bhdj\.url\s*\(|\|\s*hedron_(?:nav|form)_url\b", body):
        observed.add("hedron.routes")
    if re.search(r"\bhdj\.csrf_input\s*\(|\|\s*hedron_form_url\b", body):
        observed.add("hedron.forms")
    if re.search(r"\bhdj\.theme\b", body):
        observed.add("hedron.themes")
    if re.search(r"<\s*style\b|\sstyle\s*=|<\s*link\b[^>]*\brel\s*=\s*['\"]stylesheet", body, re.I):
        observed.add("web.css")
    if re.search(r"<\s*script\b|\son[a-z]+\s*=", body, re.I):
        observed.add("web.javascript")
    if any("-" in match.group(1) for match in _TAG_RE.finditer(body)):
        observed.add("web.custom-elements")
    if re.search(r"\shx-[\w:-]+\s*=", body, re.I):
        observed.add("htmx.core")
        observed.add("hedron.interaction")
    if re.search(r"\shx-(?:boost|push-url|replace-url|history|history-elt)\s*=", body, re.I):
        observed.add("htmx.history")
    if re.search(r"\shx-(?:select-oob|swap-oob|preserve)\s*=", body, re.I):
        observed.add("htmx.oob")
    if re.search(r"\shx-on(?::|-)|\bhtmx:(?:load|afterSwap|beforeCleanupElement)\b", body, re.I):
        observed.add("htmx.events")
    if re.search(r"<\s*script\b[^>]*\btype\s*=\s*['\"]module['\"]", body, re.I):
        observed.add("browser.modules")
    return frozenset(observed)


_HX_URL_ATTRS = frozenset(
    {
        "hx-get",
        "hx-post",
        "hx-put",
        "hx-patch",
        "hx-delete",
        "hx-push-url",
        "hx-replace-url",
    }
)
_HX_EVAL_ATTRS = frozenset(
    {
        "hx-on",
        "hx-vals",
        "hx-headers",
        "hx-vars",
        "hx-confirm",
        "hx-prompt",
        "hx-include",
        "hx-params",
        "hx-trigger",
    }
)
_HX_JS_VALUE_RE = re.compile(r"(?:^|[\s,{])js\s*:", re.I)
_HX_TRIGGER_FILTER_RE = re.compile(r"\[[^\]]+\]")


class _LiteralCapabilityParser(HTMLParser):
    def __init__(self, kind: TemplateKind) -> None:
        super().__init__(convert_charrefs=False)
        self.kind = kind
        self.capabilities: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name.lower(): value for name, value in attrs}
        if tag.lower() == "style" or "style" in values:
            self.capabilities.add("browser.inline-style")
        if tag.lower() == "script":
            inline = not values.get("src")
            if inline:
                self.capabilities.add("browser.inline-script")
            if self.kind is TemplateKind.FRAGMENT:
                self.capabilities.add("htmx.response-scripts")
        for name, value in attrs:
            lowered = name.lower()
            if lowered.startswith("on"):
                self.capabilities.add("browser.inline-script")
            if lowered.startswith("hx-on") or _hx_value_needs_eval(lowered, value):
                self.capabilities.add("htmx.eval")
            if (
                lowered in {"hx-select", "hx-target", "hx-include"}
                and value
                and (
                    value.startswith("closest ")
                    or value.startswith("find ")
                    or value.startswith("next ")
                    or value.startswith("previous ")
                )
            ):
                # Advanced relative selectors are feature-gated; capability stays local.
                pass
            if value:
                purpose = _remote_purpose(tag.lower(), lowered)
                parts = urlsplit(value.strip())
                if purpose and parts.scheme.lower() in {"http", "https"} and parts.netloc:
                    self.capabilities.add(
                        f"network.{purpose}-origin:{parts.scheme.lower()}://{parts.netloc.lower()}"
                    )


def _hx_value_needs_eval(attribute: str, value: str | None) -> bool:
    if value is None:
        return False
    if attribute.startswith("hx-on"):
        return True
    if attribute not in _HX_EVAL_ATTRS and not attribute.startswith("hx-on"):
        return False
    return bool(_HX_JS_VALUE_RE.search(value))


def _remote_purpose(tag: str, attribute: str) -> str | None:
    if attribute.startswith("hx-"):
        return "connect"
    if tag == "script" and attribute == "src":
        return "script"
    if tag == "link" and attribute == "href":
        return "style"
    if tag in {"img", "source"} and attribute in {"src", "srcset"}:
        return "image"
    if tag in {"iframe", "frame"} and attribute == "src":
        return "frame"
    if tag in {"audio", "video", "track"} and attribute in {"src", "poster"}:
        return "media"
    return None


def inferred_capabilities(parsed: ParsedHdjSource) -> frozenset[str]:
    parser = _LiteralCapabilityParser(parsed.declaration.kind)
    parser.feed(_mask_jinja_comments(parsed.body))
    return frozenset(parser.capabilities)


def contextual_diagnostics(parsed: ParsedHdjSource) -> tuple[Diagnostic, ...]:
    """Check the deliberately finite set of strict-mode dynamic output sinks."""
    original_body = parsed.body
    body = _mask_raw_expressions(_mask_jinja_comments(original_body))
    diagnostics: list[Diagnostic] = []
    unsafe_escape = re.search(r"\|\s*safe\b|{%[-+]?\s*autoescape\s+false\b", body)
    if unsafe_escape is not None:
        diagnostics.append(
            _context_diag(
                parsed,
                original_body,
                unsafe_escape.start(),
                "Generic Jinja safety escape is not allowed",
                "Use a context-specific HDJ bridge.",
            )
        )
    diagnostics.extend(_htmx_local_diagnostics(parsed, original_body, body))
    for match in _OUTPUT_RE.finditer(body):
        expr = match.group("expr").strip()
        before = body[: match.start()]
        if before.rfind("<!--") > before.rfind("-->"):
            diagnostics.append(
                _context_diag(
                    parsed,
                    original_body,
                    match.start(),
                    "Dynamic output in an HTML comment is not supported in strict HDJ",
                    "Use static comment text or move the value into visible escaped content.",
                )
            )
            continue
        last_open = before.rfind("<")
        last_close = before.rfind(">")
        in_tag = last_open > last_close
        tag_prefix = before[last_open:] if in_tag else ""
        attribute: str | None = None
        if in_tag:
            attr_match = re.search(r"([:\w-]+)\s*=\s*(['\"])[^'\"]*$", tag_prefix, re.I)
            if attr_match:
                attribute = attr_match.group(1).lower()
            elif re.search(r"=\s*$", tag_prefix):
                diagnostics.append(
                    _context_diag(
                        parsed,
                        original_body,
                        match.start(),
                        "Dynamic output in an unquoted attribute is not supported in strict HDJ",
                        "Quote the attribute value and use its context-specific bridge.",
                    )
                )
                continue
            elif re.search(r"<\s*$|(?:^|\s)[\w:-]*$", tag_prefix):
                diagnostics.append(
                    _context_diag(
                        parsed,
                        original_body,
                        match.start(),
                        "Dynamic tag or attribute names are not supported in strict HDJ",
                        "Use a static name or strict=False.",
                    )
                )
                continue
        container = None if in_tag else _open_raw_container(before)
        if attribute in {"style", "srcdoc"} or (
            attribute and (attribute.startswith("on") or attribute.startswith("hx-on"))
        ):
            diagnostics.append(
                _context_diag(
                    parsed,
                    original_body,
                    match.start(),
                    f"Dynamic output in `{attribute}` is executable or context-sensitive",
                    "Move behavior to a registered module or use a named advanced adapter.",
                )
            )
            continue
        expected_filter = _expected_url_filter(tag_prefix, attribute)
        if expected_filter and not re.search(rf"\|\s*{re.escape(expected_filter)}\b", expr):
            diagnostics.append(
                _context_diag(
                    parsed,
                    original_body,
                    match.start(),
                    f"Dynamic URL sink requires `|{expected_filter}`",
                    "Pass a purpose-compatible SafeUrl through that filter.",
                )
            )
        if "hedron_trusted" in expr and (in_tag or container in {"script", "style"}):
            diagnostics.append(
                _context_diag(
                    parsed,
                    original_body,
                    match.start(),
                    "TrustedHtml is valid only in HTML body content",
                    "Use a context-specific value or move the expression outside the "
                    "attribute/script/style sink.",
                )
            )
        if container in {"script", "style"} and "|tojson" not in expr:
            diagnostics.append(
                _context_diag(
                    parsed,
                    original_body,
                    match.start(),
                    f"Dynamic `{container}` source is not supported in strict HDJ",
                    "Use `tojson` for bounded data in script or a registered asset/module.",
                )
            )
    return tuple(diagnostics)


def _mask_jinja_comments(body: str) -> str:
    return re.sub(
        r"{#.*?#}",
        lambda match: re.sub(r"[^\r\n]", " ", match.group(0)),
        body,
        flags=re.DOTALL,
    )


def _mask_raw_expressions(body: str) -> str:
    def mask(match: re.Match[str]) -> str:
        return re.sub(r"{{|}}", "  ", match.group(0))

    return re.sub(
        r"{%[-+]?\s*raw\s*[-+]?%}.*?{%[-+]?\s*endraw\s*[-+]?%}",
        mask,
        body,
        flags=re.DOTALL,
    )


def _open_raw_container(before: str) -> str | None:
    script_open = len(re.findall(r"<\s*script\b", before, re.I))
    script_close = len(re.findall(r"<\s*/\s*script\s*>", before, re.I))
    if script_open > script_close:
        return "script"
    style_open = len(re.findall(r"<\s*style\b", before, re.I))
    style_close = len(re.findall(r"<\s*/\s*style\s*>", before, re.I))
    if style_open > style_close:
        return "style"
    return None


def _expected_url_filter(tag_prefix: str, attribute: str | None) -> str | None:
    if attribute is None:
        return None
    if attribute in {"action", "formaction", "hx-post", "hx-put", "hx-patch", "hx-delete"}:
        return "hedron_form_url"
    if attribute in {"src", "srcset", "poster", "data"}:
        return "hedron_asset_url"
    if attribute == "href" and re.search(r"<\s*link\b", tag_prefix, re.I):
        return "hedron_asset_url"
    if attribute in {"href", "hx-get", "hx-push-url", "hx-replace-url"}:
        return "hedron_nav_url"
    return None


def _htmx_local_diagnostics(
    parsed: ParsedHdjSource, original_body: str, body: str
) -> list[Diagnostic]:
    """Emit locally provable HTMX attribute diagnostics without browser claims."""
    diagnostics: list[Diagnostic] = []
    for match in re.finditer(
        r"""\s(hx-[\w:-]+)\s*=\s*(['"])(.*?)\2""",
        body,
        flags=re.I | re.DOTALL,
    ):
        attribute = match.group(1).lower()
        value = match.group(3)
        offset = match.start(1)
        if attribute in _HX_URL_ATTRS and "{{" in value and "}}" in value:
            # Dynamic URL sinks are already covered by the output-expression matrix.
            continue
        if attribute == "hx-trigger" and _HX_TRIGGER_FILTER_RE.search(value):
            diagnostics.append(
                make_diagnostic(
                    "HED-JINJA-0026",
                    severity=DiagnosticSeverity.WARNING,
                    title="HTMX trigger filter is locally noted",
                    explanation=(
                        "Trigger filters are accepted as author-written HTMX syntax; "
                        "browser race and cancellation proof is phase 0.10."
                    ),
                    remediation=(
                        "Keep filters deterministic and declare any js: eval capability explicitly."
                    ),
                    span=SourceSpan(
                        path=parsed.declaration.name,
                        start_line=parsed.declaration.body_start_line
                        + original_body.count("\n", 0, offset),
                    ),
                )
            )
        if attribute in _HX_URL_ATTRS:
            stripped = value.strip()
            if not stripped or "{{" in stripped:
                continue
            parts = urlsplit(stripped)
            if parts.scheme.lower() in {"javascript", "data", "vbscript"}:
                diagnostics.append(
                    _context_diag(
                        parsed,
                        original_body,
                        offset,
                        f"Literal `{attribute}` URL scheme {parts.scheme!r} is not allowed",
                        "Use an http(s) or same-origin path SafeUrl / static URL.",
                    )
                )
    return diagnostics


def _context_diag(
    parsed: ParsedHdjSource,
    body: str,
    offset: int,
    explanation: str,
    remediation: str,
) -> Diagnostic:
    line = parsed.declaration.body_start_line + body.count("\n", 0, offset)
    return make_diagnostic(
        "HED-JINJA-0021",
        severity=DiagnosticSeverity.ERROR,
        title="Unsafe or unprovable dynamic output context",
        explanation=explanation,
        remediation=remediation,
        span=SourceSpan(path=parsed.declaration.name, start_line=line),
    )


def diagnostics_have_errors(diagnostics: Iterable[Diagnostic]) -> bool:
    return any(diagnostic.severity is DiagnosticSeverity.ERROR for diagnostic in diagnostics)
