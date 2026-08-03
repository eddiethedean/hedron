"""HDN lexer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from hedron_core.codes import HED_HDN_LEX
from hedron_core.diagnostics import error

__all__ = ["Token", "TokenKind", "lex"]


class TokenKind(StrEnum):
    TEXT = "TEXT"
    LANGLE = "LANGLE"  # <
    RANGLE = "RANGLE"  # >
    SLASH = "SLASH"  # /
    EQUALS = "EQUALS"
    IDENT = "IDENT"
    STRING = "STRING"
    LBRACE = "LBRACE"  # {
    RBRACE = "RBRACE"  # }
    HASH = "HASH"  # #
    COLON = "COLON"
    AT = "AT"
    COMMENT = "COMMENT"
    EOF = "EOF"


@dataclass(frozen=True, slots=True)
class Token:
    kind: TokenKind
    value: str
    line: int
    column: int
    index: int


def lex(source: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    line = 1
    col = 1
    n = len(source)

    def emit(kind: TokenKind, value: str, start_i: int, start_line: int, start_col: int) -> None:
        tokens.append(Token(kind, value, start_line, start_col, start_i))

    def advance(count: int = 1) -> None:
        nonlocal i, line, col
        for _ in range(count):
            if i < n and source[i] == "\n":
                line += 1
                col = 1
            else:
                col += 1
            i += 1

    in_tag = False

    while i < n:
        ch = source[i]
        start_i, start_line, start_col = i, line, col

        if not in_tag:
            if source.startswith("<!--", i):
                end = source.find("-->", i + 4)
                if end < 0:
                    raise error(
                        HED_HDN_LEX,
                        title="Unterminated HDN comment",
                        explanation=f"Comment starting at {line}:{col} never closed.",
                        remediation="Close the comment with -->.",
                        context={"line": line, "column": col},
                    )
                value = source[i : end + 3]
                emit(TokenKind.COMMENT, value, start_i, start_line, start_col)
                advance(len(value))
                continue
            if ch == "{":
                emit(TokenKind.LBRACE, "{", start_i, start_line, start_col)
                advance()
                # Expression mode until matching }
                depth = 1
                expr_start = i
                while i < n and depth:
                    if source[i] == "{":
                        depth += 1
                    elif source[i] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    elif source[i] in {'"', "'"}:
                        q = source[i]
                        advance()
                        while i < n and source[i] != q:
                            if source[i] == "\\" and i + 1 < n:
                                advance(2)
                            else:
                                advance()
                        if i < n:
                            advance()
                        continue
                    advance()
                if depth:
                    raise error(
                        HED_HDN_LEX,
                        title="Unterminated HDN expression",
                        explanation=(
                            f"Expression starting at {start_line}:{start_col} never closed."
                        ),
                        remediation="Close the expression with }.",
                        context={"line": start_line, "column": start_col},
                    )
                expr = source[expr_start:i]
                emit(TokenKind.IDENT, expr, expr_start, start_line, start_col + 1)
                emit(TokenKind.RBRACE, "}", i, line, col)
                advance()
                continue
            if ch == "<":
                emit(TokenKind.LANGLE, "<", start_i, start_line, start_col)
                advance()
                in_tag = True
                continue
            # text until < or {
            start = i
            while i < n and source[i] not in "<{":
                if source.startswith("<!--", i):
                    break
                advance()
            text = source[start:i]
            if text:
                emit(TokenKind.TEXT, text, start_i, start_line, start_col)
            continue

        # in_tag
        if ch.isspace():
            advance()
            continue
        if ch == ">":
            emit(TokenKind.RANGLE, ">", start_i, start_line, start_col)
            advance()
            in_tag = False
            continue
        if ch == "/":
            emit(TokenKind.SLASH, "/", start_i, start_line, start_col)
            advance()
            continue
        if ch == "=":
            emit(TokenKind.EQUALS, "=", start_i, start_line, start_col)
            advance()
            continue
        if ch == "{":
            emit(TokenKind.LBRACE, "{", start_i, start_line, start_col)
            advance()
            depth = 1
            expr_start = i
            while i < n and depth:
                if source[i] == "{":
                    depth += 1
                elif source[i] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                elif source[i] in {'"', "'"}:
                    q = source[i]
                    advance()
                    while i < n and source[i] != q:
                        if source[i] == "\\" and i + 1 < n:
                            advance(2)
                        else:
                            advance()
                    if i < n:
                        advance()
                    continue
                advance()
            if depth:
                raise error(
                    HED_HDN_LEX,
                    title="Unterminated HDN expression",
                    explanation=(f"Expression starting at {start_line}:{start_col} never closed."),
                    remediation="Close the expression with }.",
                )
            expr = source[expr_start:i]
            emit(TokenKind.IDENT, expr, expr_start, start_line, start_col + 1)
            emit(TokenKind.RBRACE, "}", i, line, col)
            advance()
            continue
        if ch in {'"', "'"}:
            quote = ch
            advance()
            buf: list[str] = []
            while i < n and source[i] != quote:
                if source[i] == "\\" and i + 1 < n:
                    buf.append(source[i + 1])
                    advance(2)
                else:
                    buf.append(source[i])
                    advance()
            if i >= n:
                raise error(
                    HED_HDN_LEX,
                    title="Unterminated string",
                    explanation=f"String starting at {start_line}:{start_col} never closed.",
                    remediation="Close the string literal.",
                )
            advance()  # closing quote
            emit(TokenKind.STRING, "".join(buf), start_i, start_line, start_col)
            continue
        if ch.isalpha() or ch in "_:":
            start = i
            while i < n and (source[i].isalnum() or source[i] in "_-:"):
                advance()
            emit(TokenKind.IDENT, source[start:i], start_i, start_line, start_col)
            continue
        raise error(
            HED_HDN_LEX,
            title="Unexpected character",
            explanation=f"Unexpected {ch!r} at {line}:{col}.",
            remediation="Check HDN tag syntax.",
            context={"line": line, "column": col},
        )

    tokens.append(Token(TokenKind.EOF, "", line, col, i))
    return tokens
