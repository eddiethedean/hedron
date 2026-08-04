"""Strict Jinja integration with Hedron component rendering."""

from __future__ import annotations

import re
from collections.abc import Mapping
from contextvars import ContextVar
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from jinja2 import Environment, StrictUndefined, TemplateError, TemplateSyntaxError, nodes
from jinja2.ext import Extension
from markupsafe import Markup

from hedron_core import (
    AssetRef,
    Component,
    Diagnostic,
    DiagnosticSeverity,
    HedronError,
    Model,
    RenderContext,
    RenderMode,
    RenderResult,
    SafeUrl,
    Secret,
    SourceSpan,
    TrustedHtml,
    render,
)
from hedron_core.diagnostics import error, make_diagnostic
from hedron_core.html import html
from hedron_jinja.contracts import TemplateSpec, _validate_template_name

_ALIAS_RE = re.compile(r"^[A-Z][A-Za-z0-9_.-]*$")
_PAGE_DOCTYPE_RE = re.compile(r"^\s*<!doctype\s+html\b", re.IGNORECASE)


@dataclass(slots=True)
class _SlotCollector:
    component_alias: str
    values: dict[str, list[str]] = field(default_factory=dict)


@dataclass(slots=True)
class _RenderSession:
    template_name: str
    context: RenderContext
    max_component_invocations: int
    max_output_chars: int
    component_invocations: int = 0
    assets: dict[tuple[str, str], AssetRef] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    identity_map: dict[str, str] = field(default_factory=dict)
    diagnostics: list[Diagnostic] = field(default_factory=list)
    traces: list[Mapping[str, Any]] = field(default_factory=list)
    slot_stack: list[_SlotCollector] = field(default_factory=list)

    def merge(self, result: RenderResult) -> None:
        ordinal = self.component_invocations
        for asset in result.assets:
            key = (asset.kind, asset.href)
            previous = self.assets.get(key)
            if previous is not None and previous != asset:
                raise error(
                    "HED-JINJA-0013",
                    title="Conflicting component asset",
                    explanation=f"Component renders disagree about asset {asset.href!r}.",
                    remediation="Register one canonical definition for each asset identity.",
                )
            self.assets[key] = asset
        for name, value in result.headers.items():
            previous = self.headers.get(name)
            if previous is not None and previous != value:
                raise error(
                    "HED-JINJA-0013",
                    title="Conflicting component header",
                    explanation=f"Component renders disagree about header {name!r}.",
                    remediation="Resolve the header conflict before rendering the template.",
                )
            self.headers[name] = value
        for name, value in result.identity_map.items():
            self.identity_map[f"template:{ordinal}:{name}"] = value
        self.diagnostics.extend(result.diagnostics)
        if result.trace is not None:
            self.traces.append(result.trace)


_ACTIVE_SESSION: ContextVar[_RenderSession | None] = ContextVar(
    "hedron_jinja_active_session", default=None
)


class HedronJinjaExtension(Extension):
    """Jinja tags for inline components, explicit component bodies, and named slots."""

    tags = {"hedron", "slot"}

    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        self.owner: HedronJinja | None = None

    def parse(self, parser: Any) -> nodes.Node:
        token = next(parser.stream)
        if token.value == "slot":
            return self._parse_slot(parser, token.lineno)
        return self._parse_component(parser, token.lineno)

    def _parse_component(self, parser: Any, lineno: int) -> nodes.Node:
        alias = parser.parse_expression()
        if not isinstance(alias, nodes.Const) or not isinstance(alias.value, str):
            parser.fail("Hedron component aliases must be string literals", lineno)

        kwargs: list[nodes.Keyword] = []
        prop_names: list[str] = []
        with_body = False
        while parser.stream.current.type != "block_end":
            if parser.stream.current.test("name:with"):
                next(parser.stream)
                parser.stream.expect("name:body")
                with_body = True
                break
            name = parser.stream.expect("name").value
            parser.stream.expect("assign")
            kwargs.append(nodes.Keyword(name, parser.parse_expression()))
            prop_names.append(name)

        if parser.stream.current.type != "block_end":
            parser.fail("`with body` must be the final part of a Hedron tag", lineno)
        if self.owner is not None:
            self.owner._validate_component_call(alias.value, prop_names, lineno)

        call = self.call_method("_render_component", [alias], kwargs)
        if not with_body:
            return nodes.Output([call]).set_lineno(lineno)
        body = parser.parse_statements(("name:endhedron",), drop_needle=True)
        return nodes.CallBlock(call, [], [], body).set_lineno(lineno)

    def _parse_slot(self, parser: Any, lineno: int) -> nodes.Node:
        name = parser.parse_expression()
        if not isinstance(name, nodes.Const) or not isinstance(name.value, str):
            parser.fail("Hedron slot names must be string literals", lineno)
        body = parser.parse_statements(("name:endslot",), drop_needle=True)
        call = self.call_method("_render_slot", [name])
        return nodes.CallBlock(call, [], [], body).set_lineno(lineno)

    def _render_component(self, alias: str, caller: Any = None, **props: Any) -> Markup:
        owner = self.owner
        if owner is None:
            raise error(
                "HED-JINJA-0006",
                title="Unbound Hedron Jinja extension",
                explanation="The Jinja environment is not bound to a HedronJinja instance.",
                remediation="Construct HedronJinja(environment, components=...) first.",
            )
        return owner._render_component(alias, props, caller=caller)

    def _render_slot(self, name: str, caller: Any) -> Markup:
        owner = self.owner
        if owner is None:
            raise error(
                "HED-JINJA-0006",
                title="Unbound Hedron Jinja extension",
                explanation="The Jinja environment is not bound to a HedronJinja instance.",
            )
        return owner._render_slot(name, caller)


class HedronJinja:
    """Bind one Jinja environment to an explicit Hedron component namespace."""

    def __init__(
        self,
        environment: Environment,
        *,
        components: Mapping[str, type[Component[Any]]] | None = None,
        strict: bool = True,
        max_component_invocations: int = 10_000,
        max_output_chars: int = 10_000_000,
    ) -> None:
        self.environment = environment
        self.strict = strict
        self.max_component_invocations = max_component_invocations
        self.max_output_chars = max_output_chars
        self._components: dict[str, type[Component[Any]]] = {}
        self._frozen = False

        existing = next(
            (
                extension
                for extension in environment.extensions.values()
                if isinstance(extension, HedronJinjaExtension)
            ),
            None,
        )
        if existing is not None and existing.owner is not None:
            raise error(
                "HED-JINJA-0014",
                title="Jinja environment already bound",
                explanation="One Jinja environment can belong to only one HedronJinja instance.",
                remediation="Create a separate Environment for the other binding namespace.",
            )
        if existing is None:
            environment.add_extension(HedronJinjaExtension)
            existing = next(
                extension
                for extension in environment.extensions.values()
                if isinstance(extension, HedronJinjaExtension)
            )
        existing.owner = self

        if strict:
            environment.undefined = StrictUndefined
            environment.autoescape = True
            environment.filters.pop("safe", None)
        previous_finalize = environment.finalize

        def finalize(value: Any) -> Any:
            if isinstance(value, Secret):
                raise error(
                    "HED-JINJA-0015",
                    title="Secret cannot be rendered",
                    explanation="A Secret reached Jinja output.",
                    remediation="Prepare a non-secret presentation value in Python.",
                )
            if isinstance(value, TrustedHtml):
                raise error(
                    "HED-JINJA-0009",
                    title="TrustedHtml filter required",
                    explanation="TrustedHtml must use the `hedron_trusted` filter.",
                    remediation="Render the value with `|hedron_trusted`.",
                )
            if isinstance(value, SafeUrl):
                raise error(
                    "HED-JINJA-0010",
                    title="SafeUrl filter required",
                    explanation="SafeUrl must use the `hedron_url` filter.",
                    remediation="Render the value with `|hedron_url`.",
                )
            return previous_finalize(value) if previous_finalize is not None else value

        environment.finalize = finalize
        environment.filters["hedron_trusted"] = self._trusted_filter
        environment.filters["hedron_url"] = self._url_filter

        for alias, factory in (components or {}).items():
            self.register_component(alias, factory)

    @property
    def components(self) -> Mapping[str, type[Component[Any]]]:
        return MappingProxyType(self._components)

    def register_component(self, alias: str, factory: type[Component[Any]]) -> None:
        if self._frozen:
            raise error(
                "HED-JINJA-0003",
                title="Component bindings are frozen",
                explanation=f"Cannot register {alias!r} after checking or rendering began.",
                remediation="Register every component during application startup.",
            )
        if not _ALIAS_RE.fullmatch(alias):
            raise error(
                "HED-JINJA-0003",
                title="Invalid component alias",
                explanation=f"Alias {alias!r} is not a static uppercase component name.",
                remediation="Use an alias matching [A-Z][A-Za-z0-9_.-]*.",
            )
        if alias in self._components:
            raise error(
                "HED-JINJA-0003",
                title="Duplicate component alias",
                explanation=f"Alias {alias!r} is already registered.",
                remediation="Register each alias exactly once.",
            )
        if not isinstance(factory, type) or not issubclass(factory, Component):
            raise error(
                "HED-JINJA-0003",
                title="Component binding needs a typed component",
                explanation=f"Alias {alias!r} does not reference a Component subclass.",
                remediation="Bind a Component subclass with a declared Props model.",
            )
        self._components[alias] = factory

    def freeze(self) -> None:
        self._frozen = True

    def check(self, spec_or_name: TemplateSpec[Any] | str) -> tuple[Diagnostic, ...]:
        self.freeze()
        name, _spec = self._resolve(spec_or_name)
        try:
            source, _filename, _uptodate = self.environment.loader.get_source(  # type: ignore[union-attr]
                self.environment, name
            )
            self.environment.parse(source, name=name, filename=name)
        except TemplateSyntaxError as exc:
            return (
                make_diagnostic(
                    "HED-JINJA-0005",
                    severity=DiagnosticSeverity.ERROR,
                    title="Invalid Hedron Jinja template",
                    explanation=str(exc.message),
                    remediation="Correct the template syntax or component contract.",
                    span=SourceSpan(path=name, start_line=exc.lineno or 1),
                ),
            )
        except (TemplateError, OSError) as exc:
            return (
                make_diagnostic(
                    "HED-JINJA-0002",
                    severity=DiagnosticSeverity.ERROR,
                    title="Template could not be loaded",
                    explanation=str(exc),
                    remediation="Declare the template in the configured Jinja loader.",
                    span=SourceSpan(path=name, start_line=1),
                ),
            )
        return ()

    def render(
        self,
        spec_or_name: TemplateSpec[Any] | str,
        view: Model | Mapping[str, Any],
        *,
        context: RenderContext | None = None,
        mode: RenderMode | None = None,
    ) -> RenderResult:
        self.freeze()
        name, spec = self._resolve(spec_or_name)
        self._validate_view(spec, view)
        diagnostics = self.check(spec_or_name)
        if diagnostics:
            raise HedronError(*diagnostics)
        session = self._new_session(name, context)
        token = _ACTIVE_SESSION.set(session)
        try:
            rendered = self.environment.get_template(name).render(view=view)
        finally:
            _ACTIVE_SESSION.reset(token)
        return self._finish(session, rendered, mode or spec.mode)

    async def render_async(
        self,
        spec_or_name: TemplateSpec[Any] | str,
        view: Model | Mapping[str, Any],
        *,
        context: RenderContext | None = None,
        mode: RenderMode | None = None,
    ) -> RenderResult:
        if not self.environment.is_async:
            raise error(
                "HED-JINJA-0014",
                title="Jinja environment is not async",
                explanation="render_async() requires Environment(enable_async=True).",
                remediation="Enable async Jinja or call render().",
            )
        self.freeze()
        name, spec = self._resolve(spec_or_name)
        self._validate_view(spec, view)
        diagnostics = self.check(spec_or_name)
        if diagnostics:
            raise HedronError(*diagnostics)
        session = self._new_session(name, context)
        token = _ACTIVE_SESSION.set(session)
        try:
            rendered = await self.environment.get_template(name).render_async(view=view)
        finally:
            _ACTIVE_SESSION.reset(token)
        return self._finish(session, rendered, mode or spec.mode)

    def _resolve(self, spec_or_name: TemplateSpec[Any] | str) -> tuple[str, TemplateSpec[Any]]:
        spec = (
            spec_or_name
            if isinstance(spec_or_name, TemplateSpec)
            else TemplateSpec(spec_or_name)
        )
        _validate_template_name(spec.name)
        if self.environment.loader is None:
            raise error(
                "HED-JINJA-0002",
                title="Jinja loader required",
                explanation="HedronJinja cannot resolve templates without an environment loader.",
                remediation="Configure FileSystemLoader, PackageLoader, or an approved loader.",
            )
        return spec.name, spec

    def _validate_view(self, spec: TemplateSpec[Any], view: Any) -> None:
        if spec.view_type is not None and not isinstance(view, spec.view_type):
            raise error(
                "HED-JINJA-0008",
                title="Template view contract failed",
                explanation=f"Template {spec.name!r} requires {spec.view_type.__name__}.",
                remediation="Validate and prepare the declared view model in Python.",
            )
        if not isinstance(view, (Model, Mapping)):
            raise error(
                "HED-JINJA-0008",
                title="Invalid template view",
                explanation="Templates accept a Hedron Model or an explicit mapping.",
                remediation="Pass a bounded presentation-ready view value.",
            )

    def _validate_component_call(self, alias: str, prop_names: list[str], lineno: int) -> None:
        factory = self._components.get(alias)
        if factory is None:
            raise TemplateSyntaxError(f"unknown Hedron component alias {alias!r}", lineno)
        duplicates = {name for name in prop_names if prop_names.count(name) > 1}
        if duplicates:
            raise TemplateSyntaxError(f"duplicate component props: {sorted(duplicates)}", lineno)
        forwarded = [name for name in prop_names if name != "key"]
        invalid = set(forwarded) - set(factory.props_type.model_fields)
        if invalid:
            raise TemplateSyntaxError(
                f"unknown props for {alias}: {', '.join(sorted(invalid))}", lineno
            )
        required = {
            name for name, info in factory.props_type.model_fields.items() if info.is_required()
        }
        missing = required - set(forwarded)
        if missing:
            raise TemplateSyntaxError(
                f"missing required props for {alias}: {', '.join(sorted(missing))}", lineno
            )

    def _new_session(self, name: str, context: RenderContext | None) -> _RenderSession:
        return _RenderSession(
            template_name=name,
            context=context or RenderContext.standalone(),
            max_component_invocations=self.max_component_invocations,
            max_output_chars=self.max_output_chars,
        )

    def _session(self) -> _RenderSession:
        session = _ACTIVE_SESSION.get()
        if session is None:
            raise error(
                "HED-JINJA-0006",
                title="Hedron tag used outside a render session",
                explanation="Direct Jinja rendering would discard Hedron render metadata.",
                remediation="Use HedronJinja.render() or render_async().",
            )
        return session

    def _render_component(self, alias: str, props: dict[str, Any], *, caller: Any) -> Markup:
        session = self._session()
        session.component_invocations += 1
        if session.component_invocations > session.max_component_invocations:
            raise error(
                "HED-JINJA-0012",
                title="Component invocation limit exceeded",
                explanation=(
                    f"Template exceeded {session.max_component_invocations} component invocations."
                ),
                remediation="Reduce repeated component work or tighten the view model.",
            )
        factory = self._components.get(alias)
        if factory is None:
            raise error(
                "HED-JINJA-0004",
                title="Unknown component alias",
                explanation=f"Component alias {alias!r} is not in the template allowlist.",
                remediation="Register the component explicitly during startup.",
            )

        key = props.pop("key", None)
        collector = _SlotCollector(alias)
        body = ""
        if caller is not None:
            session.slot_stack.append(collector)
            try:
                body = str(caller())
            finally:
                session.slot_stack.pop()

        component = factory(**props)
        if key is not None:
            component.key(str(key))
        if body.strip():
            body_node = html.raw(
                TrustedHtml.reviewed(body, source=f"hedron-jinja:{session.template_name}:body")
            )
            if component.slots.get("body") is not None:
                component.slot("body", body_node)
            else:
                component.children(body_node)
        for slot_name, values in collector.values.items():
            cardinality = component.slots.get(slot_name)
            if cardinality is None:
                raise error(
                    "HED-JINJA-0007",
                    title="Unknown component slot",
                    explanation=f"{alias!r} does not declare slot {slot_name!r}.",
                    remediation="Use a slot declared by the component contract.",
                )
            if cardinality != "many" and len(values) > 1:
                raise error(
                    "HED-JINJA-0007",
                    title="Duplicate component slot",
                    explanation=f"Slot {slot_name!r} accepts one value.",
                    remediation="Provide the slot once or declare cardinality `many`.",
                )
            for value in values:
                slot_node = html.raw(
                    TrustedHtml.reviewed(
                        value, source=f"hedron-jinja:{session.template_name}:slot:{slot_name}"
                    )
                )
                component.slot(slot_name, slot_node)

        result = render(component, context=session.context, mode=RenderMode.FRAGMENT)
        session.merge(result)
        return Markup(result.html)

    def _render_slot(self, name: str, caller: Any) -> Markup:
        session = self._session()
        if not session.slot_stack:
            raise error(
                "HED-JINJA-0007",
                title="Slot outside a component body",
                explanation="A slot tag must be inside `{% hedron ... with body %}`.",
                remediation="Move the slot into its owning Hedron component block.",
            )
        rendered = str(caller())
        session.slot_stack[-1].values.setdefault(name, []).append(rendered)
        return Markup("")

    def _finish(self, session: _RenderSession, rendered: str, mode: RenderMode) -> RenderResult:
        if len(rendered) > session.max_output_chars:
            raise error(
                "HED-JINJA-0012",
                title="Template output limit exceeded",
                explanation=f"Template output exceeds {session.max_output_chars} characters.",
                remediation="Reduce rendered data or split the response into bounded fragments.",
            )
        if mode is RenderMode.PAGE:
            lower = rendered.lower()
            valid = (
                _PAGE_DOCTYPE_RE.search(rendered) is not None
                and lower.count("<html") == 1
                and lower.count("<head") == 1
                and lower.count("<body") == 1
            )
            if not valid:
                raise error(
                    "HED-JINJA-0017",
                    title="Invalid page template shape",
                    explanation="Page templates need one doctype, html, head, and body element.",
                    remediation="Emit one complete HTML document or render as a fragment.",
                )
        elif re.search(r"<\s*(?:html|head|body)\b", rendered, re.IGNORECASE):
            raise error(
                "HED-JINJA-0017",
                title="Document element in fragment",
                explanation="Fragment templates cannot emit html, head, or body elements.",
                remediation="Use RenderMode.PAGE or remove document-level markup.",
            )
        return RenderResult(
            html=rendered,
            mode=mode,
            assets=tuple(session.assets.values()),
            headers=MappingProxyType(dict(session.headers)),
            identity_map=MappingProxyType(dict(session.identity_map)),
            diagnostics=tuple(session.diagnostics),
            trace=MappingProxyType(
                {
                    "template": session.template_name,
                    "component_invocations": session.component_invocations,
                    "components": tuple(session.traces),
                }
            ),
        )

    @staticmethod
    def _trusted_filter(value: Any) -> Markup:
        if not isinstance(value, TrustedHtml):
            raise error(
                "HED-JINJA-0009",
                title="TrustedHtml required",
                explanation="`hedron_trusted` accepts only a reviewed TrustedHtml value.",
                remediation="Create trusted content at a reviewed Python boundary.",
            )
        return Markup(value.value)

    @staticmethod
    def _url_filter(value: Any) -> str:
        if not isinstance(value, SafeUrl):
            raise error(
                "HED-JINJA-0010",
                title="SafeUrl required",
                explanation="`hedron_url` accepts only a purpose-validated SafeUrl value.",
                remediation="Parse the URL for its intended purpose in Python.",
            )
        return value.value
