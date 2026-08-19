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

CSS_COMPILER_FORMAT = 1

_CLASS_RE = re.compile(r"\.([A-Za-z_][\w-]*)")
_GLOBAL_RE = re.compile(r":global\(([^)]*)\)")
_URL_RE = re.compile(r"url\(\s*(['\"]?)([^)'\"]+)\1\s*\)", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class CssCompileResult:
    css: str
    manifest: CssSymbolManifest
    asset_urls: tuple[str, ...]
    diagnostics: tuple[Diagnostic, ...] = ()


def scoped_identifier(component_id: str, symbol: str, *, kind: str = "class") -> str:
    digest = content_digest(f"v{CSS_COMPILER_FORMAT}|{kind}|{component_id}|{symbol}")
    safe_symbol = re.sub(r"[^A-Za-z0-9_-]", "_", symbol)
    return f"h-{safe_symbol}-{digest[:10]}"


def _iter_rules(rules: Sequence[CssRule]) -> list[CssRule]:
    out: list[CssRule] = []
    for rule in rules:
        out.append(rule)
        out.extend(_iter_rules(rule.children))
    return out


def _discover(sheet: CssStylesheet) -> tuple[dict[str, str], dict[str, str], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    classes: dict[str, str] = {}
    keyframes: dict[str, str] = {}

    for rule in _iter_rules(sheet.rules):
        prelude = rule.prelude
        # Mask globals for class discovery
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
        if re.search(r"(?<![:\w-])(html|body)(\s|,|$)", masked):
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


def _rewrite_classes(chunk: str, class_map: Mapping[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        return f".{class_map.get(name, name)}"

    return _CLASS_RE.sub(repl, chunk)


def _rewrite_animation_value(value: str, keyframe_map: Mapping[str, str]) -> str:
    tokens: list[str] = []
    for tok in re.split(r"(\s+|,)", value):
        stripped = tok.strip()
        if stripped in keyframe_map:
            tokens.append(keyframe_map[stripped])
        else:
            tokens.append(tok)
    return "".join(tokens)


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
    else:
        prelude = _rewrite_prelude(prelude, class_map)

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
        decls = [CssDecl(d.prop, check_value(d.value)) for d in rule.decls]
        children = [walk(c) for c in rule.children]
        return CssRule(prelude=rule.prelude, decls=decls, children=children, kind=rule.kind)

    return CssStylesheet(rules=[walk(r) for r in sheet.rules]), tuple(found)


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

    classes, keyframes, diagnostics = _discover(sheet)
    errors = [d for d in diagnostics if d.severity is DiagnosticSeverity.ERROR]
    if errors:
        raise HedronError(*errors)

    class_map: dict[str, str] = {}
    for name in classes:
        scoped = scoped_identifier(component_id, name, kind="class")
        class_map[name] = f"h-{content_digest(scoped)[:8]}" if production_names else scoped

    keyframe_map: dict[str, str] = {}
    for name in keyframes:
        scoped = scoped_identifier(component_id, name, kind="keyframes")
        keyframe_map[name] = f"h-kf-{content_digest(scoped)[:8]}" if production_names else scoped

    rewritten_rules = [_rewrite_rule(r, class_map, keyframe_map) for r in sheet.rules]
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
