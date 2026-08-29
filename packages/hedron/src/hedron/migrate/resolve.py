"""Static Streamlit symbol resolution (aliases, sidebar, decorators)."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResolvedCall:
    symbol: str  # e.g. "st.title", "st.cache_data"
    node: ast.AST
    call: ast.Call | None
    decorator: bool = False
    assigned_to: str | None = None
    in_sidebar: bool = False
    args_summary: dict[str, Any] = field(default_factory=dict[str, Any])


def _literal(node: ast.AST | None) -> Any:
    if node is None:
        return None
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError):
        if isinstance(node, ast.Name):
            return f"<name:{node.id}>"
        if isinstance(node, ast.Attribute):
            return f"<attr:{ast.unparse(node)}>"
        return f"<expr:{type(node).__name__}>"


def _summarize_call(call: ast.Call) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for index, arg in enumerate(call.args):
        summary[f"arg{index}"] = _literal(arg)
    for kw in call.keywords:
        key = kw.arg or "**"
        summary[key] = _literal(kw.value)
    return summary


def _attr_chain(node: ast.AST) -> list[str] | None:
    parts: list[str] = []
    cur: ast.AST | None = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
        parts.reverse()
        return parts
    return None


class StreamlitResolver(ast.NodeVisitor):
    """Collect proven Streamlit call/decorator sites without executing code."""

    def __init__(self) -> None:
        self.module_aliases: dict[str, str] = {}  # local name -> streamlit module
        self.from_imports: dict[str, str] = {}  # local name -> st.symbol
        self.calls: list[ResolvedCall] = []
        self._assign_target: str | None = None
        self._sidebar_depth = 0

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == "streamlit":
                self.module_aliases[alias.asname or "streamlit"] = "streamlit"
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module == "streamlit":
            for alias in node.names:
                local = alias.asname or alias.name
                self.from_imports[local] = f"st.{alias.name}"
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        # Track simple aliasing: st = streamlit / ui = st
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if isinstance(node.value, ast.Name):
                if node.value.id in self.module_aliases:
                    self.module_aliases[name] = self.module_aliases[node.value.id]
                if node.value.id in self.from_imports:
                    self.from_imports[name] = self.from_imports[node.value.id]
            prev = self._assign_target
            self._assign_target = name
            self.visit(node.value)
            self._assign_target = prev
            return
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.target, ast.Name) and node.value is not None:
            prev = self._assign_target
            self._assign_target = node.target.id
            self.visit(node.value)
            self._assign_target = prev
            return
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_decorators(node.decorator_list)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_decorators(node.decorator_list)
        self.generic_visit(node)

    def _visit_decorators(self, decorators: list[ast.expr]) -> None:
        for dec in decorators:
            symbol = self._symbol_from_expr(dec if not isinstance(dec, ast.Call) else dec.func)
            if symbol is None:
                continue
            call = dec if isinstance(dec, ast.Call) else None
            self.calls.append(
                ResolvedCall(
                    symbol=symbol,
                    node=dec,
                    call=call,
                    decorator=True,
                    args_summary=_summarize_call(call) if call else {},
                )
            )

    def visit_Call(self, node: ast.Call) -> None:
        symbol = self._symbol_from_expr(node.func)
        in_sidebar = self._sidebar_depth > 0
        if symbol is not None:
            # st.sidebar.selectbox(...) — attribute chain includes sidebar
            chain = _attr_chain(node.func)
            if chain and len(chain) >= 3 and chain[1] == "sidebar":
                in_sidebar = True
                # Normalize to st.<api> for registry lookup
                symbol = f"st.{chain[-1]}"
            elif chain and len(chain) == 2 and chain[1] == "sidebar":
                symbol = "st.sidebar"
            self.calls.append(
                ResolvedCall(
                    symbol=symbol,
                    node=node,
                    call=node,
                    assigned_to=self._assign_target,
                    in_sidebar=in_sidebar,
                    args_summary=_summarize_call(node),
                )
            )
            # Enter sidebar context for with st.sidebar: handled separately
        # Column handle calls: revenue.metric(...) when revenue = st.columns(...)[0]
        # Handled via attribute name heuristics when base is Name
        if symbol is None and isinstance(node.func, ast.Attribute):
            method = node.func.attr
            if method in _COLUMN_METHODS and isinstance(node.func.value, ast.Name):
                self.calls.append(
                    ResolvedCall(
                        symbol=f"st.{method}",
                        node=node,
                        call=node,
                        assigned_to=self._assign_target,
                        in_sidebar=in_sidebar,
                        args_summary=_summarize_call(node),
                    )
                )
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        entered = 0
        for item in node.items:
            ctx = item.context_expr
            symbol = self._symbol_from_expr(ctx if not isinstance(ctx, ast.Call) else ctx.func)
            if symbol == "st.sidebar" or (
                isinstance(ctx, ast.Attribute)
                and _attr_chain(ctx) is not None
                and _attr_chain(ctx) == [self._st_name() or "st", "sidebar"]
            ):
                self._sidebar_depth += 1
                entered += 1
            elif symbol is not None:
                call = ctx if isinstance(ctx, ast.Call) else None
                self.calls.append(
                    ResolvedCall(
                        symbol=symbol,
                        node=ctx,
                        call=call,
                        args_summary=_summarize_call(call) if call else {},
                        in_sidebar=self._sidebar_depth > 0,
                    )
                )
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars is not None:
                self.visit(item.optional_vars)
        for stmt in node.body:
            self.visit(stmt)
        self._sidebar_depth -= entered

    def _st_name(self) -> str | None:
        for name, mod in self.module_aliases.items():
            if mod == "streamlit":
                return name
        return None

    def _symbol_from_expr(self, expr: ast.AST) -> str | None:
        if isinstance(expr, ast.Name) and expr.id in self.from_imports:
            return self.from_imports[expr.id]
        chain = _attr_chain(expr)
        if not chain:
            return None
        head = chain[0]
        if head in self.module_aliases:
            # streamlit.foo or st.foo[.bar]
            if len(chain) == 1:
                return "st"
            if chain[1] == "sidebar" and len(chain) == 2:
                return "st.sidebar"
            if chain[1] == "sidebar" and len(chain) >= 3:
                return f"st.{chain[-1]}"
            if chain[1] == "session_state":
                return "st.session_state"
            if chain[1] == "query_params":
                return "st.query_params"
            return f"st.{chain[1]}"
        if head in self.from_imports and len(chain) == 1:
            return self.from_imports[head]
        return None


_COLUMN_METHODS = frozenset(
    {
        "metric",
        "write",
        "markdown",
        "title",
        "header",
        "subheader",
        "dataframe",
        "table",
        "line_chart",
        "bar_chart",
        "area_chart",
        "scatter_chart",
        "pyplot",
        "plotly_chart",
        "altair_chart",
        "image",
        "code",
        "json",
        "success",
        "info",
        "warning",
        "error",
        "button",
        "text_input",
        "selectbox",
        "slider",
        "checkbox",
    }
)


def resolve_streamlit_calls(tree: ast.AST) -> list[ResolvedCall]:
    resolver = StreamlitResolver()
    resolver.visit(tree)
    return resolver.calls
