"""Scoped CSS AST compiler."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from hedron_core.codes import (
    HED_ASSET_MISSING,
    HED_ASSET_TRAVERSAL,
    HED_CSS_DUPLICATE,
    HED_CSS_PARSE,
    HED_CSS_REMOTE,
    HED_CSS_UNSAFE_GLOBAL,
)
from hedron_core.css.ast import CssDecl, CssRule, CssStylesheet, emit_stylesheet, parse_stylesheet
from hedron_core.diagnostics import (
    Diagnostic,
    DiagnosticSeverity,
    HedronError,
    error,
    make_diagnostic,
)
from hedron_core.identifiers import content_digest
from hedron_core.manifests import CSS_SYMBOL_MANIFEST_FORMAT, CssSymbolManifest

__all__ = ["CssCompileResult", "compile_css", "scoped_identifier"]

CSS_COMPILER_FORMAT = 2
# The compiler format may advance without invalidating public symbols.  The
# 0.59 contract requires v1 symbol hashes to remain stable unless a separately
# recorded collision/security migration changes them.
SYMBOL_HASH_FORMAT = 1

_CLASS_RE = re.compile(r"\.([A-Za-z_][\w-]*)")
_GLOBAL_RE = re.compile(r":global\(([^)]*)\)")
_URL_RE = re.compile(r"url\(\s*(['\"]?)([^)'\"]+)\1\s*\)", re.IGNORECASE)
_IMPORT_TARGET_RE = re.compile(
    r"^@import\s+(?:url\(\s*(['\"]?)([^)'\"]+)\1\s*\)|(['\"])(.*?)\3)",
    re.IGNORECASE,
)
_UNSAFE_VALUE_RE = re.compile(
    r"(?:expression\s*\(|-moz-binding\s*:|behavior\s*:)",
    re.IGNORECASE,
)
_PRIVATE_SELECTOR_RE = re.compile(r"\.(?:hedron|h)-[A-Za-z0-9_-]+")
_BEHAVIOR_PROPERTIES = frozenset({"content", "pointer-events", "user-select"})


@dataclass(frozen=True, slots=True)
class CssCompileResult:
    css: str
    manifest: CssSymbolManifest
    asset_urls: tuple[str, ...]
    diagnostics: tuple[Diagnostic, ...] = ()


def scoped_identifier(component_id: str, symbol: str, *, kind: str = "class") -> str:
    digest = content_digest(f"v{SYMBOL_HASH_FORMAT}|{kind}|{component_id}|{symbol}")
    safe_symbol = re.sub(r"[^A-Za-z0-9_-]", "_", symbol)
    return f"h-{safe_symbol}-{digest[:10]}"


def _iter_rules(rules: Sequence[CssRule]) -> list[CssRule]:
    out: list[CssRule] = []
    for rule in rules:
        out.append(rule)
        out.extend(_iter_rules(rule.children))
    return out


def _discover(
    sheet: CssStylesheet,
    *,
    allow_global: bool = False,
) -> tuple[dict[str, str], dict[str, str], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    classes: dict[str, str] = {}
    keyframes: dict[str, str] = {}

    for rule in _iter_rules(sheet.rules):
        prelude = rule.prelude
        masked = ""
        # A class-like token in an at-rule prelude is not a selector.  In
        # particular, ``@import \"theme.css\"`` must never create a symbol
        # named ``css``.  Selector discovery is intentionally limited to style
        # rules; selector-bearing feature tests are handled during rewriting.
        if rule.kind == "style":
            masked = _GLOBAL_RE.sub(lambda m: ":global()", prelude)
            for match in _CLASS_RE.finditer(masked):
                classes[match.group(1)] = match.group(1)
        if rule.kind == "at-rule" and prelude.lower().startswith("@keyframes"):
            parts = prelude.split(None, 1)
            if len(parts) == 2:
                name = parts[1].strip()
                if name in keyframes:
                    diagnostics.append(
                        make_diagnostic(
                            HED_CSS_DUPLICATE,
                            severity=DiagnosticSeverity.ERROR,
                            title="Duplicate keyframes",
                            explanation=f"@keyframes {name} is declared more than once.",
                            remediation="Rename or merge the keyframe definitions.",
                        )
                    )
                keyframes[name] = name
        if not allow_global and re.search(r"(?<![:\w-])(html|body)(\s|,|$)", masked):
            diagnostics.append(
                make_diagnostic(
                    HED_CSS_UNSAFE_GLOBAL,
                    severity=DiagnosticSeverity.ERROR,
                    title="Unsafe global selector",
                    explanation="Bare html/body selectors require :global(...).",
                    remediation="Wrap the selector in :global(...) explicitly.",
                )
            )
    return classes, keyframes, diagnostics


def _rewrite_prelude(prelude: str, class_map: Mapping[str, str]) -> str:
    parts: list[str] = []
    pos = 0
    for match in _GLOBAL_RE.finditer(prelude):
        before = prelude[pos : match.start()]
        parts.append(_rewrite_classes(before, class_map))
        parts.append(match.group(1))
        pos = match.end()
    parts.append(_rewrite_classes(prelude[pos:], class_map))
    return "".join(parts)


def _scope_prelude(prelude: str, scope_root: str) -> str:
    """Prefix ordinary selectors with a stable application scope root."""
    if not scope_root or prelude.startswith("@"):
        return prelude
    selectors: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    escaped = False
    for index, char in enumerate(prelude):
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
        elif char in "([":
            depth += 1
        elif char in ")]":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            selectors.append(prelude[start:index].strip())
            start = index + 1
    selectors.append(prelude[start:].strip())
    return ", ".join(
        f"{scope_root} {selector}" if selector else scope_root for selector in selectors
    )


def _rewrite_classes(chunk: str, class_map: Mapping[str, str]) -> str:
    # Rewrite only selector identifiers.  Regex replacement is unsafe here:
    # class-looking text inside strings, comments, URLs, decimals, and CSS
    # escapes is not a selector symbol.
    out: list[str] = []
    i = 0
    n = len(chunk)
    while i < n:
        if chunk.startswith("/*", i):
            end = chunk.find("*/", i + 2)
            end = n if end < 0 else end + 2
            out.append(chunk[i:end])
            i = end
            continue
        ch = chunk[i]
        if ch in {"'", '"'}:
            quote = ch
            start = i
            i += 1
            while i < n:
                if chunk[i] == "\\":
                    i += 2
                    continue
                i += 1
                if chunk[i - 1] == quote:
                    break
            out.append(chunk[start:i])
            continue
        if chunk.startswith(":global(", i):
            start = i
            depth = 0
            while i < n:
                if chunk[i] == "(":
                    depth += 1
                elif chunk[i] == ")":
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                i += 1
            out.append(chunk[start:i])
            continue
        if ch == "." and i + 1 < n and (chunk[i + 1].isalpha() or chunk[i + 1] in "_-"):
            j = i + 2
            while j < n and (chunk[j].isalnum() or chunk[j] in "_-\\"):
                j += 1
            name = chunk[i + 1 : j]
            out.append("." + class_map.get(name, name))
            i = j
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _rewrite_animation_value(value: str, keyframe_map: Mapping[str, str]) -> str:
    # Animation names are identifiers embedded in a shorthand grammar.  Walk
    # identifiers while preserving strings/comments/functions and only replace
    # names discovered in @keyframes; timing functions and CSS-wide keywords
    # therefore remain untouched.
    reserved = {
        "none",
        "initial",
        "inherit",
        "unset",
        "revert",
        "revert-layer",
        "linear",
        "ease",
        "ease-in",
        "ease-out",
        "ease-in-out",
        "step-start",
        "step-end",
    }
    out: list[str] = []
    i = 0
    n = len(value)
    while i < n:
        if value.startswith("/*", i):
            end = value.find("*/", i + 2)
            end = n if end < 0 else end + 2
            out.append(value[i:end])
            i = end
            continue
        if value[i] in {"'", '"'}:
            quote = value[i]
            start = i
            i += 1
            while i < n:
                if value[i] == "\\":
                    i += 2
                    continue
                i += 1
                if value[i - 1] == quote:
                    break
            out.append(value[start:i])
            continue
        if value[i].isalpha() or value[i] in "_-":
            start = i
            i += 1
            while i < n and (value[i].isalnum() or value[i] in "_-\\"):
                i += 1
            token = value[start:i]
            if i < n and value[i] == "(":
                out.append(token)
            elif token not in reserved:
                out.append(keyframe_map.get(token, token))
            else:
                out.append(token)
            continue
        out.append(value[i])
        i += 1
    return "".join(out)


def _rewrite_rule(
    rule: CssRule,
    class_map: Mapping[str, str],
    keyframe_map: Mapping[str, str],
) -> CssRule:
    prelude = rule.prelude
    if rule.kind == "at-rule" and prelude.lower().startswith("@keyframes"):
        parts = prelude.split(None, 1)
        if len(parts) == 2 and parts[1].strip() in keyframe_map:
            prelude = f"@keyframes {keyframe_map[parts[1].strip()]}"
    elif rule.kind == "at-rule" and prelude.lower().startswith("@import"):
        # Do not rewrite class selectors inside @import URLs (``.com`` / ``.css``).
        prelude = rule.prelude
    elif rule.kind == "at-rule" and prelude.lower().startswith("@supports"):
        # The selector() feature test is selector grammar; other supports
        # declarations must remain byte-for-byte authored values.
        prelude = re.sub(
            r"(selector\()([^)]*)(\))",
            lambda match: (
                match.group(1) + _rewrite_classes(match.group(2), class_map) + match.group(3)
            ),
            prelude,
            flags=re.IGNORECASE,
        )
    else:
        prelude = _rewrite_prelude(prelude, class_map) if rule.kind == "style" else rule.prelude

    decls: list[CssDecl] = []
    for decl in rule.decls:
        value = decl.value
        if decl.prop.lower() in {"animation", "animation-name"}:
            value = _rewrite_animation_value(value, keyframe_map)
        decls.append(CssDecl(decl.prop, value))

    children = [_rewrite_rule(child, class_map, keyframe_map) for child in rule.children]
    return CssRule(prelude=prelude, decls=decls, children=children, kind=rule.kind)


def _check_urls_in_sheet(
    sheet: CssStylesheet,
    *,
    allow_remote: bool,
    registered_roots: Sequence[Path],
    component_dir: Path | None,
) -> tuple[CssStylesheet, tuple[str, ...]]:
    found: list[str] = []
    roots = tuple(Path(r).resolve() for r in registered_roots)

    def check_value(value: str) -> str:
        if _UNSAFE_VALUE_RE.search(value):
            raise error(
                HED_CSS_UNSAFE_GLOBAL,
                title="Unsafe CSS value rejected",
                explanation=f"Declaration value {value!r} uses a banned CSS construct.",
                remediation="Remove expression(), -moz-binding, and behavior declarations.",
            )

        def repl(match: re.Match[str]) -> str:
            quote = match.group(1)
            url = match.group(2).strip()
            if url.startswith("data:"):
                found.append(url)
                return match.group(0)
            parsed = urlparse(url)
            if parsed.scheme == "file" or (parsed.scheme == "" and url.startswith("/")):
                raise error(
                    HED_ASSET_TRAVERSAL,
                    title="Absolute CSS URL rejected",
                    explanation=f"url({url}) is an absolute filesystem path.",
                    remediation="Use a component-relative asset under a registered root.",
                )
            if parsed.scheme in {"http", "https"} or url.startswith("//"):
                if not allow_remote:
                    raise error(
                        HED_CSS_REMOTE,
                        title="Remote CSS URL rejected",
                        explanation=f"Remote url({url}) is not allowed by asset policy.",
                        remediation="Use a component-relative asset under a registered root.",
                    )
                found.append(url)
                return match.group(0)
            # Relative asset URL requires registered roots.
            if not roots:
                raise error(
                    HED_ASSET_TRAVERSAL,
                    title="CSS URL outside registered roots",
                    explanation=(
                        f"url({url}) cannot be validated because no registered "
                        "asset roots were provided."
                    ),
                    remediation="Pass registered_roots / component_dir when compiling CSS.",
                )
            if any(part == ".." for part in Path(url).parts):
                raise error(
                    HED_ASSET_TRAVERSAL,
                    title="CSS URL path traversal rejected",
                    explanation=f"url({url}) escapes the registered asset roots.",
                    remediation="Keep asset URLs inside registered component roots.",
                )
            if component_dir is None:
                raise error(
                    HED_ASSET_TRAVERSAL,
                    title="CSS URL outside registered roots",
                    explanation=f"url({url}) requires a component_dir for resolution.",
                    remediation="Pass component_dir when compiling CSS with relative URLs.",
                )
            link = component_dir / url
            if link.is_symlink():
                raise error(
                    HED_ASSET_TRAVERSAL,
                    title="Symlinked CSS asset rejected",
                    explanation=f"url({url}) resolves through a symlink.",
                    remediation="Use a real file under a registered root.",
                )
            candidate = link.resolve()
            if not any(candidate == root or root in candidate.parents for root in roots):
                raise error(
                    HED_ASSET_TRAVERSAL,
                    title="CSS URL outside registered roots",
                    explanation=f"url({url}) resolves outside registered asset roots.",
                    remediation="Register the asset root or relocate the file.",
                )
            if not candidate.is_file():
                raise error(
                    HED_ASSET_MISSING,
                    title="CSS asset missing",
                    explanation=f"url({url}) does not resolve to an existing file.",
                    remediation="Add the asset file or fix the URL.",
                )
            found.append(url)
            q = quote or '"'
            return f"url({q}{url}{q})"

        return _URL_RE.sub(repl, value)

    def walk(rule: CssRule) -> CssRule:
        # Validate URLs in @import preludes (not only declaration values).
        prelude = rule.prelude
        if prelude.lower().startswith("@import"):
            prelude = check_value(prelude)
            match = _IMPORT_TARGET_RE.match(prelude.strip())
            if match:
                url = match.group(2) or match.group(4) or ""
                parsed = urlparse(url.strip())
                if parsed.scheme in {"http", "https"} or url.startswith("//"):
                    raise error(
                        HED_CSS_REMOTE,
                        title="Remote CSS import rejected",
                        explanation=f"Remote import {url!r} is not allowed by asset policy.",
                        remediation="Use a component-relative stylesheet under a registered root.",
                    )
        decls = [CssDecl(d.prop, check_value(d.value)) for d in rule.decls]
        children = [walk(c) for c in rule.children]
        return CssRule(prelude=prelude, decls=decls, children=children, kind=rule.kind)

    return CssStylesheet(rules=[walk(r) for r in sheet.rules]), tuple(found)


def _check_application_policy(
    sheet: CssStylesheet,
    *,
    component_id: str,
    allow_global: bool,
) -> None:
    if not component_id.startswith("application:"):
        return
    for rule in _iter_rules(sheet.rules):
        if rule.kind == "style":
            if _PRIVATE_SELECTOR_RE.search(rule.prelude):
                raise error(
                    HED_CSS_UNSAFE_GLOBAL,
                    title="Private Hedron selector rejected",
                    explanation=(
                        f"Application CSS cannot target generated selector {rule.prelude!r}."
                    ),
                    remediation="Use a manifest-backed data-hedron component/part/state hook.",
                    component_id=component_id,
                )
            if not allow_global and ":global(" in rule.prelude:
                raise error(
                    HED_CSS_UNSAFE_GLOBAL,
                    title="Global selector requires explicit opt-in",
                    explanation="Application CSS may not escape its scope without global_=True.",
                    remediation="Register the stylesheet with global_=True only when required.",
                    component_id=component_id,
                )
        for declaration in rule.decls:
            if declaration.prop.strip().lower() in _BEHAVIOR_PROPERTIES:
                raise error(
                    HED_CSS_UNSAFE_GLOBAL,
                    title="Behavior-changing CSS rejected",
                    explanation=(
                        f"Application CSS property {declaration.prop!r} is not a "
                        "presentation-only override."
                    ),
                    remediation="Use a semantic component prop or a public presentation token.",
                    component_id=component_id,
                )


def _braces_balanced_outside_literals(source: str) -> bool:
    depth = 0
    in_string: str | None = None
    in_comment = False
    escaped = False
    index = 0
    length = len(source)
    while index < length:
        ch = source[index]
        nxt = source[index + 1] if index + 1 < length else ""
        if in_comment:
            if ch == "*" and nxt == "/":
                in_comment = False
                index += 2
                continue
            index += 1
            continue
        if in_string is not None:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == in_string:
                in_string = None
            index += 1
            continue
        if ch == "/" and nxt == "*":
            in_comment = True
            index += 2
            continue
        if ch in {'"', "'"}:
            in_string = ch
            index += 1
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                return False
        index += 1
    return depth == 0 and in_string is None and not in_comment


def compile_css(
    source: str,
    *,
    component_id: str,
    layer: str = "components",
    allow_remote: bool = False,
    registered_roots: Sequence[Path] | None = None,
    component_dir: Path | None = None,
    production_names: bool = False,
    scope_root: str | None = None,
    rewrite_selectors: bool = True,
    allow_global: bool = False,
) -> CssCompileResult:
    """Compile component CSS into scoped output + symbol manifest via AST rewrite."""
    from hedron_core.compile_gate import assert_runtime_compile_allowed
    from hedron_core.css.layers import wrap_in_layer

    assert_runtime_compile_allowed(what="CSS")

    try:
        sheet = parse_stylesheet(source)
    except Exception as exc:
        raise error(
            HED_CSS_PARSE,
            title="CSS parse error",
            explanation=f"Failed to parse component stylesheet: {exc}",
            remediation="Fix the stylesheet syntax.",
            component_id=component_id,
        ) from exc

    if not _braces_balanced_outside_literals(source):
        raise error(
            HED_CSS_PARSE,
            title="CSS parse error",
            explanation="Unbalanced braces in component stylesheet.",
            remediation="Fix the stylesheet syntax.",
            component_id=component_id,
        )

    _check_application_policy(sheet, component_id=component_id, allow_global=allow_global)
    classes, keyframes, diagnostics = _discover(sheet, allow_global=allow_global)
    errors = [d for d in diagnostics if d.severity is DiagnosticSeverity.ERROR]
    if errors:
        raise HedronError(*errors)

    class_map: dict[str, str] = {}
    keyframe_map: dict[str, str] = {}
    if rewrite_selectors:
        for name in classes:
            scoped = scoped_identifier(component_id, name, kind="class")
            class_map[name] = f"h-{content_digest(scoped)[:8]}" if production_names else scoped
        for name in keyframes:
            scoped = scoped_identifier(component_id, name, kind="keyframes")
            keyframe_map[name] = (
                f"h-kf-{content_digest(scoped)[:8]}" if production_names else scoped
            )

    rewritten_rules = [_rewrite_rule(r, class_map, keyframe_map) for r in sheet.rules]
    if scope_root:

        def scope_rule(rule: CssRule) -> CssRule:
            prelude = (
                _scope_prelude(rule.prelude, scope_root) if rule.kind == "style" else rule.prelude
            )
            return CssRule(
                prelude=prelude,
                decls=list(rule.decls),
                children=[scope_rule(child) for child in rule.children],
                kind=rule.kind,
            )

        rewritten_rules = [scope_rule(rule) for rule in rewritten_rules]
    rewritten_sheet = CssStylesheet(rules=rewritten_rules)
    rewritten_sheet, asset_urls = _check_urls_in_sheet(
        rewritten_sheet,
        allow_remote=allow_remote,
        registered_roots=tuple(registered_roots or ()),
        component_dir=component_dir,
    )
    css_body = emit_stylesheet(rewritten_sheet)
    layered = wrap_in_layer(css_body, layer)
    manifest = CssSymbolManifest(
        format_version=CSS_SYMBOL_MANIFEST_FORMAT,
        component_id=component_id,
        symbols=class_map,
        keyframes=keyframe_map,
    )
    return CssCompileResult(
        css=layered,
        manifest=manifest,
        asset_urls=asset_urls,
        diagnostics=tuple(diagnostics),
    )
