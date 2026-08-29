"""Minimal CSS rule AST for scoped rewriting."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CssDecl:
    prop: str
    value: str


def _css_rule_list() -> list[CssRule]:
    return []


@dataclass
class CssRule:
    prelude: str
    decls: list[CssDecl] = field(default_factory=list[CssDecl])
    children: list[CssRule] = field(default_factory=_css_rule_list)
    kind: str = "style"  # style | at-rule | statement | comment


@dataclass
class CssStylesheet:
    rules: list[CssRule] = field(default_factory=list[CssRule])


def parse_stylesheet(source: str) -> CssStylesheet:
    """Parse a focused CSS subset into nested rules (not a full CSS engine)."""
    i = 0
    n = len(source)
    rules: list[CssRule] = []

    def skip_ws() -> None:
        nonlocal i
        while i < n and source[i].isspace():
            i += 1

    def parse_block() -> tuple[list[CssDecl], list[CssRule]]:
        nonlocal i
        decls: list[CssDecl] = []
        children: list[CssRule] = []
        skip_ws()
        while i < n and source[i] != "}":
            skip_ws()
            if i < n and source[i] == "}":
                break
            if source.startswith("/*", i):
                end = source.find("*/", i + 2)
                end = n if end < 0 else end + 2
                children.append(CssRule(prelude=source[i:end], kind="comment"))
                i = end
                continue
            # Peek prelude until { or ;
            start = i
            depth = 0
            while i < n:
                ch = source[i]
                if ch == "{":
                    break
                if ch == "}" and depth == 0:
                    break
                if ch == ";" and depth == 0:
                    break
                if ch in {'"', "'"}:
                    quote = ch
                    i += 1
                    while i < n and source[i] != quote:
                        if source[i] == "\\" and i + 1 < n:
                            i += 2
                        else:
                            i += 1
                    i += 1
                    continue
                i += 1
            prelude = source[start:i].strip()
            if i < n and source[i] == ";":
                # declaration
                i += 1
                if ":" in prelude:
                    prop, _, value = prelude.partition(":")
                    decls.append(CssDecl(prop.strip(), value.strip()))
                continue
            if i < n and source[i] == "{":
                i += 1  # consume {
                child_decls, child_rules = parse_block()
                if i < n and source[i] == "}":
                    i += 1
                kind = "at-rule" if prelude.startswith("@") else "style"
                children.append(
                    CssRule(prelude=prelude, decls=child_decls, children=child_rules, kind=kind)
                )
                continue
            # Last declaration without trailing semicolon before `}`.
            if prelude and ":" in prelude:
                prop, _, value = prelude.partition(":")
                decls.append(CssDecl(prop.strip(), value.strip()))
            break
        return decls, children

    skip_ws()
    while i < n:
        skip_ws()
        if i >= n:
            break
        if source.startswith("/*", i):
            end = source.find("*/", i + 2)
            end = n if end < 0 else end + 2
            rules.append(CssRule(prelude=source[i:end], kind="comment"))
            i = end
            continue
        start = i
        while i < n and source[i] not in "{;":
            if source.startswith("/*", i):
                break
            i += 1
        prelude = source[start:i].strip()
        if i < n and source[i] == ";":
            i += 1
            if prelude:
                rules.append(CssRule(prelude=prelude, kind="statement"))
            skip_ws()
            continue
        if i >= n:
            break
        i += 1  # {
        decls, children = parse_block()
        if i < n and source[i] == "}":
            i += 1
        if prelude:
            kind = "at-rule" if prelude.startswith("@") else "style"
            rules.append(CssRule(prelude=prelude, decls=decls, children=children, kind=kind))
        skip_ws()
    return CssStylesheet(rules=rules)


def emit_stylesheet(sheet: CssStylesheet) -> str:
    def emit_rule(rule: CssRule, indent: int = 0) -> str:
        pad = "  " * indent
        inner_pad = "  " * (indent + 1)
        if rule.kind == "statement":
            return f"{pad}{rule.prelude};"
        if rule.kind == "comment":
            return f"{pad}{rule.prelude}"
        lines = [f"{pad}{rule.prelude} {{"]
        for decl in rule.decls:
            lines.append(f"{inner_pad}{decl.prop}: {decl.value};")
        for child in rule.children:
            lines.append(emit_rule(child, indent + 1))
        lines.append(f"{pad}}}")
        return "\n".join(lines)

    return "\n".join(emit_rule(r) for r in sheet.rules) + ("\n" if sheet.rules else "")
