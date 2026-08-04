"""HDN parser."""

from __future__ import annotations

import ast as py_ast
import re

from hedron_core.codes import HED_HDN_PARSE
from hedron_core.diagnostics import error
from hedron_core.hdn.ast import (
    Document,
    ElementNode,
    ExprNode,
    ForNode,
    FragmentNode,
    HtmlRawNode,
    IfNode,
    ImportNode,
    Node,
    SlotNode,
    SourceSpan,
    TextNode,
)
from hedron_core.hdn.lexer import Token, TokenKind, lex

__all__ = ["parse_hdn"]

_IMPORT_RE = re.compile(
    r"^@import\s+(?P<local>[A-Za-z_][A-Za-z0-9_]*)\s+from\s+"
    r"(?P<source>\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*')$"
)


class _Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.i = 0

    def peek(self) -> Token:
        return self.tokens[self.i]

    def advance(self) -> Token:
        tok = self.tokens[self.i]
        self.i += 1
        return tok

    def expect(self, kind: TokenKind) -> Token:
        tok = self.advance()
        if tok.kind != kind:
            raise error(
                HED_HDN_PARSE,
                title="Unexpected token",
                explanation=f"Expected {kind.value}, got {tok.kind.value} ({tok.value!r}).",
                remediation="Fix the HDN syntax.",
                context={"line": tok.line, "column": tok.column},
            )
        return tok

    def span(self, tok: Token) -> SourceSpan:
        return SourceSpan(tok.line, tok.column, tok.index)

    def parse_document(self) -> Document:
        body: list[Node] = []
        saw_content = False
        while self.peek().kind != TokenKind.EOF:
            if self.peek().kind == TokenKind.COMMENT:
                self.advance()
                continue
            node = self.parse_node(allow_import=True)
            if isinstance(node, ImportNode):
                if saw_content:
                    raise error(
                        HED_HDN_PARSE,
                        title="Component import must precede markup",
                        explanation=(
                            "HDN component imports are only allowed before rendered content."
                        ),
                        remediation=(
                            "Move the {@import ...} declaration to the top of the template."
                        ),
                        context={"line": node.span.line, "column": node.span.column},
                    )
            elif not isinstance(node, TextNode) or node.value.strip():
                saw_content = True
            body.append(node)
        return Document(body=body)

    def parse_node(self, *, allow_import: bool = False) -> Node:
        tok = self.peek()
        if tok.kind == TokenKind.TEXT:
            self.advance()
            return TextNode(span=self.span(tok), value=tok.value)
        if tok.kind == TokenKind.LBRACE:
            return self.parse_brace(allow_import=allow_import)
        if tok.kind == TokenKind.LANGLE:
            return self.parse_element_or_fragment()
        raise error(
            HED_HDN_PARSE,
            title="Unexpected content",
            explanation=f"Unexpected token {tok.kind.value} at {tok.line}:{tok.column}.",
            remediation="Expected text, expression, or tag.",
            context={"line": tok.line, "column": tok.column},
        )

    def parse_brace(self, *, allow_import: bool = False) -> Node:
        start = self.expect(TokenKind.LBRACE)
        # Next token is IDENT containing expression source (lexer packs it)
        expr_tok = self.expect(TokenKind.IDENT)
        self.expect(TokenKind.RBRACE)
        src = expr_tok.value.strip()
        if src.startswith("#if "):
            return self.parse_if_block(start, src[4:].strip())
        if src.startswith("#for "):
            return self.parse_for_block(start, src[5:].strip())
        if src.startswith("@import"):
            if not allow_import:
                raise error(
                    HED_HDN_PARSE,
                    title="Nested component import",
                    explanation="HDN component imports are only allowed at the document root.",
                    remediation="Move the {@import ...} declaration to the top of the template.",
                    context={"line": start.line, "column": start.column},
                )
            return self.parse_import(start, src)
        if src.startswith("@html "):
            return HtmlRawNode(span=self.span(start), expression=src[6:].strip())
        if src in {":else", "/if", "/for"}:
            raise error(
                HED_HDN_PARSE,
                title="Orphan block marker",
                explanation=f"Unexpected {{{src}}} outside a block.",
                remediation="Use markers only inside {#if}/{#for} blocks.",
                context={"line": start.line, "column": start.column},
            )
        return ExprNode(span=self.span(start), source=src)

    def parse_import(self, start: Token, source: str) -> ImportNode:
        match = _IMPORT_RE.fullmatch(source)
        if match is None:
            raise error(
                HED_HDN_PARSE,
                title="Invalid component import",
                explanation=f"Could not parse component import {source!r}.",
                remediation='Use {@import LocalName from "component-logical-id"}.',
                context={"line": start.line, "column": start.column},
            )
        local_name = match.group("local")
        if not local_name[:1].isupper():
            raise error(
                HED_HDN_PARSE,
                title="Invalid component import name",
                explanation=f"Imported component name {local_name!r} must start uppercase.",
                remediation="Use an uppercase local name so HDN treats the tag as a component.",
                context={"line": start.line, "column": start.column},
            )
        try:
            component_ref = py_ast.literal_eval(match.group("source"))
        except (SyntaxError, ValueError) as exc:
            raise error(
                HED_HDN_PARSE,
                title="Invalid component import reference",
                explanation="The component logical identifier is not a valid string literal.",
                remediation='Use {@import LocalName from "component-logical-id"}.',
                context={"line": start.line, "column": start.column},
            ) from exc
        if not isinstance(component_ref, str) or not component_ref.strip():
            raise error(
                HED_HDN_PARSE,
                title="Invalid component import reference",
                explanation="A component import needs a non-empty logical identifier.",
                remediation='Use {@import LocalName from "component-logical-id"}.',
                context={"line": start.line, "column": start.column},
            )
        if any(ord(char) < 32 for char in component_ref):
            raise error(
                HED_HDN_PARSE,
                title="Invalid component import reference",
                explanation="Component logical identifiers cannot contain control characters.",
                remediation="Use the registered component's stable logical identifier.",
                context={"line": start.line, "column": start.column},
            )
        return ImportNode(
            span=self.span(start),
            local_name=local_name,
            component_ref=component_ref,
        )

    def parse_if_block(self, start: Token, condition: str) -> IfNode:
        then_body: list[Node] = []
        else_body: list[Node] = []
        target = then_body
        while True:
            tok = self.peek()
            if tok.kind == TokenKind.EOF:
                raise error(
                    HED_HDN_PARSE,
                    title="Unclosed {#if}",
                    explanation=f"{{#if}} at {start.line}:{start.column} was never closed.",
                    remediation="Add {/if}.",
                )
            if tok.kind == TokenKind.LBRACE:
                # peek expression
                # We need to look ahead without consuming incorrectly
                save = self.i
                self.advance()
                expr_tok = self.expect(TokenKind.IDENT)
                self.expect(TokenKind.RBRACE)
                src = expr_tok.value.strip()
                if src == ":else":
                    target = else_body
                    continue
                if src == "/if":
                    break
                # not a marker — rewind and parse as node
                self.i = save
                target.append(self.parse_node())
                continue
            target.append(self.parse_node())
        return IfNode(
            span=self.span(start),
            condition=condition,
            then_body=then_body,
            else_body=else_body,
        )

    def parse_for_block(self, start: Token, header: str) -> ForNode:
        # header: "item in items"
        if " in " not in header:
            raise error(
                HED_HDN_PARSE,
                title="Invalid {#for}",
                explanation="Expected `{#for item in items}`.",
                remediation="Use `in` between the item name and iterable.",
                context={"line": start.line, "column": start.column},
            )
        item, _, iterable = header.partition(" in ")
        item = item.strip()
        iterable = iterable.strip()
        body: list[Node] = []
        while True:
            tok = self.peek()
            if tok.kind == TokenKind.EOF:
                raise error(
                    HED_HDN_PARSE,
                    title="Unclosed {#for}",
                    explanation=f"{{#for}} at {start.line}:{start.column} was never closed.",
                    remediation="Add {/for}.",
                )
            if tok.kind == TokenKind.LBRACE:
                save = self.i
                self.advance()
                expr_tok = self.expect(TokenKind.IDENT)
                self.expect(TokenKind.RBRACE)
                src = expr_tok.value.strip()
                if src == "/for":
                    break
                self.i = save
                body.append(self.parse_node())
                continue
            body.append(self.parse_node())
        return ForNode(span=self.span(start), item=item, iterable=iterable, body=body)

    def parse_element_or_fragment(self) -> Node:
        start = self.expect(TokenKind.LANGLE)
        # fragment <>
        if self.peek().kind == TokenKind.RANGLE:
            self.advance()
            children: list[Node] = []
            while True:
                tok = self.peek()
                if tok.kind == TokenKind.LANGLE and self.tokens[self.i + 1].kind == TokenKind.SLASH:
                    self.advance()
                    self.expect(TokenKind.SLASH)
                    self.expect(TokenKind.RANGLE)
                    break
                if tok.kind == TokenKind.EOF:
                    raise error(
                        HED_HDN_PARSE,
                        title="Unclosed fragment",
                        explanation="Fragment <> was never closed.",
                        remediation="Close with </>.",
                    )
                children.append(self.parse_node())
            return FragmentNode(span=self.span(start), children=children)

        # closing tag misplaced
        if self.peek().kind == TokenKind.SLASH:
            raise error(
                HED_HDN_PARSE,
                title="Unexpected closing tag",
                explanation="Found a closing tag without an open tag.",
                remediation="Remove the stray closing tag.",
                context={"line": start.line, "column": start.column},
            )

        name_tok = self.expect(TokenKind.IDENT)
        tag = name_tok.value
        attrs: dict[str, object] = {}
        while self.peek().kind not in {TokenKind.RANGLE, TokenKind.SLASH, TokenKind.EOF}:
            attr_name = self.expect(TokenKind.IDENT).value
            if self.peek().kind == TokenKind.EQUALS:
                self.advance()
                if self.peek().kind == TokenKind.STRING:
                    attrs[attr_name] = self.advance().value
                elif self.peek().kind == TokenKind.LBRACE:
                    self.advance()
                    expr = self.expect(TokenKind.IDENT).value
                    self.expect(TokenKind.RBRACE)
                    attrs[attr_name] = ExprNode(span=self.span(name_tok), source=expr.strip())
                else:
                    raise error(
                        HED_HDN_PARSE,
                        title="Invalid attribute value",
                        explanation=f"Attribute {attr_name} needs a string or {{expression}}.",
                        remediation='Use attr="value" or attr={expr}.',
                    )
            else:
                attrs[attr_name] = True

        self_closing = False
        if self.peek().kind == TokenKind.SLASH:
            self.advance()
            self_closing = True
        self.expect(TokenKind.RANGLE)

        if tag == "slot":
            children = []
            if not self_closing:
                children = self.parse_children(tag)
            slot_name = attrs.get("name", "default")
            if isinstance(slot_name, ExprNode):
                raise error(
                    HED_HDN_PARSE,
                    title="Dynamic slot name rejected",
                    explanation="Slot names must be static strings.",
                    remediation='Use <slot name="...">.',
                )
            return SlotNode(
                span=self.span(start),
                name=str(slot_name),
                children=children,
            )

        children = []
        if not self_closing:
            children = self.parse_children(tag)
        return ElementNode(
            span=self.span(start),
            tag=tag,
            attrs=attrs,
            children=children,
            self_closing=self_closing,
        )

    def parse_children(self, tag: str) -> list[Node]:
        children: list[Node] = []
        while True:
            tok = self.peek()
            if tok.kind == TokenKind.EOF:
                raise error(
                    HED_HDN_PARSE,
                    title="Unclosed tag",
                    explanation=f"<{tag}> was never closed.",
                    remediation=f"Add </{tag}>.",
                )
            if tok.kind == TokenKind.LANGLE and self.tokens[self.i + 1].kind == TokenKind.SLASH:
                self.advance()
                self.expect(TokenKind.SLASH)
                close = self.expect(TokenKind.IDENT).value
                self.expect(TokenKind.RANGLE)
                if close != tag:
                    raise error(
                        HED_HDN_PARSE,
                        title="Mismatched closing tag",
                        explanation=f"Expected </{tag}>, got </{close}>.",
                        remediation="Fix the closing tag name.",
                    )
                break
            children.append(self.parse_node())
        return children


def parse_hdn(source: str) -> Document:
    tokens = lex(source)
    return _Parser(tokens).parse_document()
