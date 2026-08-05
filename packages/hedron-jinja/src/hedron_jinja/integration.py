"""Strict HDJ v1 integration with shared Hedron component rendering."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Iterator, Mapping
from contextvars import ContextVar
from dataclasses import dataclass, field
from html.parser import HTMLParser
from types import MappingProxyType
from typing import Any, NoReturn, Protocol
from urllib.parse import urlsplit
from weakref import ReferenceType, WeakKeyDictionary, ref

from jinja2 import Environment, StrictUndefined, Template, TemplateError, TemplateSyntaxError, nodes
from jinja2.ext import Extension
from jinja2.nativetypes import NativeEnvironment
from jinja2.parser import Parser
from jinja2.runtime import Context
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
    UrlPurpose,
)
from hedron_core import (
    RenderSession as CoreRenderSession,
)
from hedron_core.diagnostics import error, make_diagnostic
from hedron_core.html import html
from hedron_core.typing_aliases import RenderTrace
from hedron_jinja.contracts import (
    HdjContext,
    TemplateCapabilities,
    TemplateDeclaration,
    TemplateKind,
    TemplateSource,
    TemplateSpec,
    validate_template_name,
)
from hedron_jinja.source import (
    EXPLICIT_FEATURES,
    HdjLoader,
    ParsedHdjSource,
    contextual_diagnostics,
    dependency_edges,
    diagnostics_have_errors,
    generic_safety_escape_diagnostics,
    inferred_capabilities,
    observed_features,
)

_ALIAS_RE = re.compile(r"^[A-Z][A-Za-z0-9_.-]*$")
_LOGICAL_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:/-]*$")
_PAGE_DOCTYPE_RE = re.compile(r"^\s*<!doctype\s+html\b", re.IGNORECASE)
_CONDITIONAL_ASSET_RE = re.compile(r"{%[-+]?\s*hedron_asset\b")


class _JinjaCaller(Protocol):
    """Jinja ``caller`` / CallBlock callback (untyped at attribute level; RFC-0031)."""

    def __call__(self) -> object: ...


def _hdj_template_class(base: type[Template]) -> type[Template]:
    """Buffer ordinary stream(); expose explicit two-phase streaming for 0.10."""

    class HdjTemplate(base):  # type: ignore[valid-type,misc]
        def stream(self, *args: object, **kwargs: object) -> NoReturn:
            raise error(
                "HED-JINJA-0014",
                title="Direct Jinja streaming is not supported",
                explanation=(
                    "Template.stream() would emit HTML before RenderResult metadata is complete."
                ),
                remediation=(
                    "Use HedronJinja.render() / render_async(), or "
                    "HedronJinja.two_phase_stream() for the explicit 0.10 streaming API."
                ),
            )

    HdjTemplate.__name__ = f"Hdj{base.__name__}"
    HdjTemplate.__qualname__ = f"Hdj{base.__qualname__}"
    return HdjTemplate


@dataclass(frozen=True, slots=True)
class TwoPhaseStream:
    """Metadata-first HDJ stream: finalize RenderResult, then yield body chunks."""

    result: RenderResult
    body_chunks: tuple[str, ...]

    def iter_phases(self) -> Iterator[tuple[str, RenderResult | str]]:
        yield ("metadata", self.result)
        for chunk in self.body_chunks:
            yield ("body", chunk)


@dataclass(slots=True)
class _SlotCollector:
    component_alias: str
    values: dict[str, list[str]] = field(default_factory=dict)


@dataclass(slots=True)
class _RenderSession:
    binding: HedronJinja
    template_name: str
    logical_id: str
    declaration: TemplateDeclaration
    context: RenderContext
    mode: RenderMode
    core: CoreRenderSession
    static_asset_ids: frozenset[str]
    max_component_invocations: int
    max_output_chars: int
    max_metadata_items: int
    component_invocations: int = 0
    assets: dict[tuple[str, str], AssetRef] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    diagnostics: list[Diagnostic] = field(default_factory=list)
    traces: list[RenderTrace | Mapping[str, object]] = field(default_factory=list)
    slot_stack: list[_SlotCollector] = field(default_factory=list)

    def merge(self, result: RenderResult) -> None:
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
        self.diagnostics.extend(result.diagnostics)
        if result.trace is not None:
            self.traces.append(result.trace)
        self.ensure_metadata_budget()

    def ensure_metadata_budget(self) -> None:
        total = (
            len(self.assets)
            + len(self.headers)
            + len(self.core.identity_map)
            + len(self.diagnostics)
            + len(self.traces)
        )
        if total > self.max_metadata_items:
            raise error(
                "HED-JINJA-0012",
                title="Template metadata limit exceeded",
                explanation=f"Template accumulated more than {self.max_metadata_items} items.",
                remediation=(
                    "Reduce repeated metadata or raise the request-local limit deliberately."
                ),
            )


_ACTIVE_SESSION: ContextVar[_RenderSession | None] = ContextVar(
    "hedron_jinja_active_session", default=None
)
_BINDINGS: WeakKeyDictionary[Environment, ReferenceType[HedronJinja]] = WeakKeyDictionary()


def _environment_binding(environment: Environment) -> HedronJinja | None:
    binding_ref = _BINDINGS.get(environment)
    return binding_ref() if binding_ref is not None else None


class HedronJinjaExtension(Extension):
    """The small HDJ grammar: guard, components, slots, and conditional assets."""

    tags = {"hdj_guard", "hedron", "slot", "hedron_asset"}

    def parse(self, parser: Parser) -> nodes.Node:
        token = next(parser.stream)
        if token.value == "hdj_guard":
            call = self.call_method("_guard", [nodes.ContextReference()])
            return nodes.Output([call]).set_lineno(token.lineno)
        if token.value == "slot":
            return self._parse_slot(parser, token.lineno)
        if token.value == "hedron_asset":
            return self._parse_asset(parser, token.lineno)
        return self._parse_component(parser, token.lineno)

    def _parse_component(self, parser: Parser, lineno: int) -> nodes.Node:
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
        binding = _environment_binding(self.environment)
        if binding is not None:
            binding._validate_component_call(alias.value, prop_names, lineno)
        call = self.call_method("_render_component", [nodes.ContextReference(), alias], kwargs)
        if not with_body:
            return nodes.Output([call]).set_lineno(lineno)
        body = parser.parse_statements(("name:endhedron",), drop_needle=True)
        return nodes.CallBlock(call, [], [], body).set_lineno(lineno)

    def _parse_slot(self, parser: Parser, lineno: int) -> nodes.Node:
        name = parser.parse_expression()
        if not isinstance(name, nodes.Const) or not isinstance(name.value, str):
            parser.fail("Hedron slot names must be string literals", lineno)
        body = parser.parse_statements(("name:endslot",), drop_needle=True)
        call = self.call_method("_render_slot", [nodes.ContextReference(), name])
        return nodes.CallBlock(call, [], [], body).set_lineno(lineno)

    def _parse_asset(self, parser: Parser, lineno: int) -> nodes.Node:
        logical_id = parser.parse_expression()
        if not isinstance(logical_id, nodes.Const) or not isinstance(logical_id.value, str):
            parser.fail("Hedron asset IDs must be string literals", lineno)
        call = self.call_method("_require_asset", [nodes.ContextReference(), logical_id])
        return nodes.Output([call]).set_lineno(lineno)

    def _guard(self, context: Context) -> Markup:
        _runtime_binding(context)
        return Markup("")

    def _render_component(
        self,
        context: Context,
        alias: str,
        caller: _JinjaCaller | None = None,
        **props: object,
    ) -> Markup:
        return _runtime_binding(context)._render_component(alias, props, caller=caller)

    def _render_slot(self, context: Context, name: str, caller: _JinjaCaller) -> Markup:
        return _runtime_binding(context)._render_slot(name, caller)

    def _require_asset(self, context: Context, logical_id: str) -> Markup:
        return _runtime_binding(context)._require_asset(logical_id)


def _runtime_binding(context: Context) -> HedronJinja:
    session = _ACTIVE_SESSION.get()
    if session is None or context.environment is not session.binding.environment:
        raise error(
            "HED-JINJA-0006",
            title="HDJ template used outside its render session",
            explanation="Direct Jinja rendering would bypass the HDJ source and metadata contract.",
            remediation="Use HedronJinja.render() or render_async().",
        )
    return session.binding


class HedronJinja:
    """Bind one fresh Jinja environment to an explicit HDJ namespace."""

    def __init__(
        self,
        environment: Environment,
        *,
        components: Mapping[str, type[Component[Any]]] | None = None,
        assets: Mapping[str, AssetRef] | None = None,
        strict: bool = True,
        allowed_capabilities: Iterable[str] = (),
        max_component_invocations: int = 10_000,
        max_output_chars: int = 10_000_000,
        max_metadata_items: int = 10_000,
        max_dependency_depth: int = 32,
        url_builder: Callable[..., SafeUrl] | None = None,
        csrf_builder: Callable[[], TrustedHtml] | None = None,
    ) -> None:
        limits = {
            "max_component_invocations": max_component_invocations,
            "max_output_chars": max_output_chars,
            "max_metadata_items": max_metadata_items,
            "max_dependency_depth": max_dependency_depth,
        }
        invalid_limits = [
            name
            for name, value in limits.items()
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0
        ]
        if invalid_limits:
            raise ValueError(f"HDJ limits must be positive: {', '.join(invalid_limits)}")
        if isinstance(environment, NativeEnvironment):
            raise error(
                "HED-JINJA-0014",
                title="NativeEnvironment is not supported",
                explanation="HDJ produces HTML plus RenderResult metadata.",
                remediation="Use a normal jinja2.Environment.",
            )
        if _environment_binding(environment) is not None:
            raise error(
                "HED-JINJA-0014",
                title="Jinja environment already bound",
                explanation="One environment can belong to only one HedronJinja instance.",
                remediation="Create a fresh Environment for the other binding.",
            )
        if environment.loader is None:
            raise error(
                "HED-JINJA-0002",
                title="Jinja loader required",
                explanation="HedronJinja cannot resolve templates without a loader.",
                remediation=(
                    "Configure a FileSystemLoader, PackageLoader, or explicit namespace loader."
                ),
            )
        if isinstance(environment.loader, HdjLoader):
            raise error(
                "HED-JINJA-0014",
                title="HDJ loader is already installed",
                explanation="A derived or previously bound environment cannot be rebound safely.",
                remediation="Construct HedronJinja with a fresh base Jinja environment.",
            )
        if environment.cache and len(environment.cache):
            raise error(
                "HED-JINJA-0014",
                title="Jinja environment is already in use",
                explanation="Templates were loaded before the HDJ boundary was installed.",
                remediation="Bind a fresh, fully configured Environment before loading templates.",
            )

        self.environment = environment
        self.strict = strict
        self.allowed_capabilities = frozenset(allowed_capabilities)
        self.max_component_invocations = max_component_invocations
        self.max_output_chars = max_output_chars
        self.max_metadata_items = max_metadata_items
        self.max_dependency_depth = max_dependency_depth
        self.url_builder = url_builder
        self.csrf_builder = csrf_builder
        self._components: dict[str, type[Component[Any]]] = {}
        self._assets: dict[str, AssetRef] = {}
        self._frozen = False

        environment.loader = HdjLoader(environment.loader)
        environment.template_class = _hdj_template_class(environment.template_class)
        environment.add_extension(HedronJinjaExtension)
        # Always force autoescape; HDJ never renders with autoescape=False.
        environment.autoescape = True
        if strict:
            environment.undefined = StrictUndefined
        previous_finalize = environment.finalize

        def finalize(value: object) -> object:
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
                    explanation="TrustedHtml must use `hedron_trusted` in HTML body content.",
                    remediation="Render it with `|hedron_trusted` at that sink.",
                )
            if isinstance(value, SafeUrl):
                raise error(
                    "HED-JINJA-0010",
                    title="Purpose-specific SafeUrl filter required",
                    explanation="SafeUrl must use a sink-specific HDJ URL filter.",
                    remediation="Use hedron_nav_url, hedron_form_url, or hedron_asset_url.",
                )
            return previous_finalize(value) if previous_finalize is not None else value

        environment.finalize = finalize
        environment.filters["safe"] = self._generic_safe_filter
        environment.filters["hedron_trusted"] = self._trusted_filter
        environment.filters["hedron_nav_url"] = self._navigation_url_filter
        environment.filters["hedron_form_url"] = self._form_url_filter
        environment.filters["hedron_asset_url"] = self._asset_url_filter
        _BINDINGS[environment] = ref(self)

        for alias, factory in (components or {}).items():
            self.register_component(alias, factory)
        for logical_id, asset in (assets or {}).items():
            self.register_asset(logical_id, asset)
        self._environment_fingerprint = self._fingerprint_environment()

    @property
    def components(self) -> Mapping[str, type[Component[Any]]]:
        return MappingProxyType(self._components)

    @property
    def assets(self) -> Mapping[str, AssetRef]:
        return MappingProxyType(self._assets)

    def register_component(self, alias: str, factory: type[Component[Any]]) -> None:
        self._require_mutable("component", alias)
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

    def register_asset(self, logical_id: str, asset: AssetRef) -> None:
        self._require_mutable("asset", logical_id)
        if not _LOGICAL_ID_RE.fullmatch(logical_id) or not isinstance(asset, AssetRef):
            raise error(
                "HED-JINJA-0019",
                title="Invalid HDJ asset binding",
                explanation=f"Asset {logical_id!r} needs a canonical ID and AssetRef value.",
                remediation="Register a validated local or policy-approved asset.",
            )
        if logical_id in self._assets:
            raise error(
                "HED-JINJA-0019",
                title="Duplicate HDJ asset binding",
                explanation=f"Asset ID {logical_id!r} is already registered.",
                remediation="Register one canonical definition.",
            )
        parts = urlsplit(asset.href)
        if parts.scheme and parts.scheme.lower() != "https":
            raise error(
                "HED-JINJA-0019",
                title="HDJ assets require local or HTTPS URLs",
                explanation=f"Asset {logical_id!r} uses unsupported scheme {parts.scheme!r}.",
                remediation="Use a registered local path or an explicit HTTPS origin.",
            )
        try:
            SafeUrl.parse(
                asset.href,
                purpose=UrlPurpose.ASSET,
                allow_external=parts.scheme.lower() == "https",
            )
        except (HedronError, TypeError, ValueError) as exc:
            raise error(
                "HED-JINJA-0019",
                title="Invalid HDJ asset URL",
                explanation=f"Asset {logical_id!r} has an invalid URL.",
                remediation="Register a validated local or HTTPS asset URL.",
            ) from exc
        if parts.scheme.lower() == "https" and self._asset_kind_purpose(asset.kind) is None:
            raise error(
                "HED-JINJA-0019",
                title="Remote HDJ asset kind has no policy purpose",
                explanation=f"Asset kind {asset.kind!r} cannot map to a network capability.",
                remediation="Use a supported script, style, image, font, or media kind.",
            )
        self._assets[logical_id] = asset

    def _require_mutable(self, kind: str, name: str) -> None:
        if self._frozen:
            raise error(
                "HED-JINJA-0003",
                title="HDJ bindings are frozen",
                explanation=f"Cannot register {kind} {name!r} after checking or rendering began.",
                remediation="Register every binding during application startup.",
            )

    def freeze(self) -> None:
        self._assert_environment_unchanged()
        self._frozen = True

    def describe(self, spec_or_name: TemplateSpec[Model] | str) -> TemplateDeclaration:
        self.freeze()
        name, spec = self._resolve(spec_or_name)
        parsed = self._parsed(name)
        self._validate_spec_declaration(spec, parsed.declaration)
        return parsed.declaration

    def check(
        self,
        spec_or_name: TemplateSpec[Model] | str,
    ) -> tuple[Diagnostic, ...]:
        self.freeze()
        try:
            name, spec = self._resolve(spec_or_name)
            graph = self._dependency_graph(name)
            diagnostics = self._check_graph(graph, spec)
        except HedronError as exc:
            return exc.diagnostics
        except TemplateSyntaxError as exc:
            name = spec_or_name.name if isinstance(spec_or_name, TemplateSpec) else spec_or_name
            return (
                make_diagnostic(
                    "HED-JINJA-0005",
                    severity=DiagnosticSeverity.ERROR,
                    title="Invalid HDJ template",
                    explanation=str(exc.message),
                    remediation="Correct the template syntax or component contract.",
                    span=SourceSpan(path=name, start_line=exc.lineno or 1),
                ),
            )
        except (TemplateError, OSError, ValueError) as exc:
            name = spec_or_name.name if isinstance(spec_or_name, TemplateSpec) else spec_or_name
            return (
                make_diagnostic(
                    "HED-JINJA-0002",
                    severity=DiagnosticSeverity.ERROR,
                    title="Template could not be loaded",
                    explanation=str(exc),
                    remediation="Declare a canonical .hdj source in the configured loader.",
                    span=SourceSpan(path=name, start_line=1),
                ),
            )
        return tuple(diagnostics)

    def capabilities(self, spec_or_name: TemplateSpec[Model] | str) -> TemplateCapabilities:
        self.freeze()
        name, spec = self._resolve(spec_or_name)
        graph = self._dependency_graph(name)
        declared: set[str] = set()
        inferred: set[str] = set()
        for parsed in graph:
            declared.update(parsed.declaration.requires)
            inferred.update(inferred_capabilities(parsed))
            for logical_id in parsed.declaration.assets:
                capability = self._registered_asset_capability(logical_id)
                if capability:
                    inferred.add(capability)
        for logical_id in spec.assets:
            capability = self._registered_asset_capability(logical_id)
            if capability:
                inferred.add(capability)
        if graph[0].declaration.kind is TemplateKind.FRAGMENT and (
            spec.assets
            or any(item.declaration.assets for item in graph)
            or any(_CONDITIONAL_ASSET_RE.search(item.body) for item in graph)
        ):
            inferred.add("browser.head-mutation")
        return TemplateCapabilities(
            name=name,
            declared=frozenset(declared),
            inferred=frozenset(inferred),
            dependencies=tuple(item.declaration.name for item in graph[1:]),
        )

    def render(
        self,
        spec_or_name: TemplateSpec[Model] | str,
        view: Model | Mapping[str, object],
        *,
        context: RenderContext | None = None,
        mode: RenderMode | None = None,
    ) -> RenderResult:
        if self.environment.is_async:
            raise error(
                "HED-JINJA-0014",
                title="Async Jinja requires render_async",
                explanation="Synchronous Jinja generation can buffer an async template eagerly.",
                remediation="Await HedronJinja.render_async() for an async environment.",
            )
        name, spec, graph, diagnostics, render_mode = self._prepare_render(spec_or_name, view, mode)
        session = self._new_session(name, graph, context, render_mode, diagnostics, spec)
        hdj = self._hdj_context(session)
        token = _ACTIVE_SESSION.set(session)
        chunks: list[str] = []
        size = 0
        try:
            for chunk in self.environment.get_template(name).generate(view=view, hdj=hdj):
                size += len(chunk)
                if size > session.max_output_chars:
                    self._raise_output_limit(session)
                chunks.append(chunk)
        finally:
            _ACTIVE_SESSION.reset(token)
        return self._finish(session, "".join(chunks))

    def two_phase_stream(
        self,
        spec_or_name: TemplateSpec[Model] | str,
        view: Model | Mapping[str, object],
        *,
        context: RenderContext | None = None,
        mode: RenderMode | None = None,
        body_chunk_size: int = 4096,
    ) -> TwoPhaseStream:
        """Render atomically, then expose body chunks for focused streaming (RFC-0032)."""
        result = self.render(spec_or_name, view, context=context, mode=mode)
        body = result.html
        if body_chunk_size < 1:
            raise ValueError("body_chunk_size must be >= 1")
        chunks = tuple(
            body[i : i + body_chunk_size] for i in range(0, len(body), body_chunk_size)
        ) or ("",)
        return TwoPhaseStream(result=result, body_chunks=chunks)

    async def render_async(
        self,
        spec_or_name: TemplateSpec[Model] | str,
        view: Model | Mapping[str, object],
        *,
        context: RenderContext | None = None,
        mode: RenderMode | None = None,
    ) -> RenderResult:
        if not self.environment.is_async:
            raise error(
                "HED-JINJA-0014",
                title="Jinja environment is not async",
                explanation="render_async() requires Environment(enable_async=True).",
                remediation="Enable async Jinja before binding or call render().",
            )
        name, spec, graph, diagnostics, render_mode = self._prepare_render(spec_or_name, view, mode)
        if "jinja.async" not in graph[0].declaration.effective_features:
            raise error(
                "HED-JINJA-0023",
                title="Async rendering is not declared",
                explanation=(
                    f"Template {name!r} does not enable the explicit `jinja.async` feature."
                ),
                remediation="Add `jinja.async` to the root HDJ prologue features.",
            )
        session = self._new_session(name, graph, context, render_mode, diagnostics, spec)
        hdj = self._hdj_context(session)
        token = _ACTIVE_SESSION.set(session)
        chunks: list[str] = []
        size = 0
        try:
            async for chunk in self.environment.get_template(name).generate_async(
                view=view, hdj=hdj
            ):
                size += len(chunk)
                if size > session.max_output_chars:
                    self._raise_output_limit(session)
                chunks.append(chunk)
        finally:
            _ACTIVE_SESSION.reset(token)
        return self._finish(session, "".join(chunks))

    def _prepare_render(
        self,
        spec_or_name: TemplateSpec[Model] | str,
        view: object,
        mode: RenderMode | None,
    ) -> tuple[
        str, TemplateSpec[Model], tuple[ParsedHdjSource, ...], tuple[Diagnostic, ...], RenderMode
    ]:
        self.freeze()
        name, spec = self._resolve(spec_or_name)
        self._validate_view(spec, view)
        graph = self._dependency_graph(name)
        declaration = graph[0].declaration
        self._validate_spec_declaration(spec, declaration)
        render_mode = declaration.kind.render_mode
        if render_mode is None:
            raise error(
                "HED-JINJA-0020",
                title="Library template is not an entry point",
                explanation=f"Template {name!r} is declared as a library.",
                remediation="Import it from a page/fragment or render a page/fragment entry point.",
            )
        for assertion in (spec.mode, mode):
            if assertion is not None and assertion is not render_mode:
                raise error(
                    "HED-JINJA-0020",
                    title="Template kind and render mode disagree",
                    explanation=f"{name!r} declares {declaration.kind.value!r}.",
                    remediation="Fix the application assertion; source kind is authoritative.",
                )
        diagnostics = self._check_graph(graph, spec)
        if diagnostics_have_errors(diagnostics):
            raise HedronError(*diagnostics)
        return name, spec, graph, tuple(diagnostics), render_mode

    def _resolve(self, spec_or_name: TemplateSpec[Model] | str) -> tuple[str, TemplateSpec[Model]]:
        spec = (
            spec_or_name if isinstance(spec_or_name, TemplateSpec) else TemplateSpec(spec_or_name)
        )
        validate_template_name(spec.name)
        if spec.source is TemplateSource.PACKAGE:
            raise error(
                "HED-JINJA-0002",
                title="Package template namespaces are not a format-v1 input",
                explanation="Phase 0.9 accepts application-owned .hdj loader names only.",
                remediation=(
                    "Keep installed-package Jinja in a separate environment until the finite, "
                    "fingerprinted phase 0.11 namespace contract."
                ),
            )
        return spec.name, spec

    def _parsed(self, name: str) -> ParsedHdjSource:
        loader = self.environment.loader
        if not isinstance(loader, HdjLoader):
            raise error(
                "HED-JINJA-0014",
                title="HDJ loader boundary was replaced",
                explanation="The environment loader changed after binding.",
                remediation="Do not mutate the Jinja environment after HDJ binding.",
            )
        return loader.get_parsed_source(self.environment, name)

    def _dependency_graph(self, root: str) -> tuple[ParsedHdjSource, ...]:
        ordered: list[ParsedHdjSource] = []
        visited: set[str] = set()
        active: set[str] = set()

        def walk(name: str, depth: int) -> None:
            if depth > self.max_dependency_depth:
                raise error(
                    "HED-JINJA-0012",
                    title="Template dependency depth exceeded",
                    explanation=f"Dependency graph exceeded {self.max_dependency_depth} levels.",
                    remediation="Reduce inheritance/include depth.",
                )
            if name in active:
                raise error(
                    "HED-JINJA-0022",
                    title="Template dependency cycle",
                    explanation=f"Static dependency cycle reaches {name!r}.",
                    remediation="Break the include/import cycle.",
                )
            if name in visited:
                return
            parsed = self._parsed(name)
            visited.add(name)
            active.add(name)
            ordered.append(parsed)
            for edge in dependency_edges(self.environment, parsed):
                if edge.target is None:
                    raise error(
                        "HED-JINJA-0022",
                        title="Dynamic template dependency is not supported in format v1",
                        explanation=f"{name!r} has a dynamic {edge.relation} expression.",
                        remediation=(
                            "Use a static .hdj template name; bounded dynamic graphs are deferred."
                        ),
                        span=SourceSpan(path=name, start_line=edge.line),
                    )
                validate_template_name(edge.target)
                if not edge.target.endswith(".hdj"):
                    raise error(
                        "HED-JINJA-0022",
                        title="Foreign Jinja dependency is not supported in format v1",
                        explanation=f"Dependency {edge.target!r} is not an .hdj source.",
                        remediation="Convert it to HDJ or keep it in a separate Jinja environment.",
                        span=SourceSpan(path=name, start_line=edge.line),
                    )
                target = self._parsed(edge.target)
                self._validate_composition(parsed, target, edge.relation, edge.line)
                walk(edge.target, depth + 1)
            active.remove(name)

        walk(root, 0)
        return tuple(ordered)

    @staticmethod
    def _validate_composition(
        source: ParsedHdjSource,
        target: ParsedHdjSource,
        relation: str,
        line: int,
    ) -> None:
        source_kind = source.declaration.kind
        target_kind = target.declaration.kind
        valid = False
        if relation == "extends":
            valid = source_kind is target_kind
        elif relation == "include":
            valid = target_kind is TemplateKind.FRAGMENT
        elif relation == "import":
            valid = target_kind is TemplateKind.LIBRARY
        if not valid:
            raise error(
                "HED-JINJA-0020",
                title="Invalid HDJ kind composition",
                explanation=(
                    f"A {source_kind.value} template cannot {relation} a "
                    f"{target_kind.value} template under the format-v1 composition matrix."
                ),
                remediation="Extend the same kind, include a fragment, or import a library.",
                span=SourceSpan(path=source.declaration.name, start_line=line),
            )

    def _check_graph(
        self, graph: tuple[ParsedHdjSource, ...], spec: TemplateSpec[Model]
    ) -> list[Diagnostic]:
        root = graph[0]
        self._validate_spec_declaration(spec, root.declaration)
        diagnostics: list[Diagnostic] = []
        graph_capabilities: set[str] = set()
        graph_requires: set[str] = set()
        for parsed in graph:
            declaration = parsed.declaration
            observed = observed_features(self.environment, parsed)
            missing_features = observed - declaration.effective_features
            for feature in sorted(missing_features):
                diagnostics.append(
                    make_diagnostic(
                        "HED-JINJA-0023",
                        severity=DiagnosticSeverity.ERROR,
                        title="HDJ feature used but not enabled",
                        explanation=(
                            f"{declaration.name!r} uses {feature!r} outside its profile/features."
                        ),
                        remediation="Choose an appropriate profile or add the feature explicitly.",
                        span=SourceSpan(path=declaration.name, start_line=1),
                    )
                )
            for feature in sorted(declaration.declared_features - observed):
                if feature not in EXPLICIT_FEATURES and ".extension:" not in feature:
                    diagnostics.append(
                        make_diagnostic(
                            "HED-JINJA-0023",
                            severity=DiagnosticSeverity.WARNING,
                            title="Explicit HDJ feature is unused",
                            explanation=(
                                f"Explicit feature {feature!r} was not observed in "
                                f"{declaration.name!r}."
                            ),
                            remediation="Remove the explicit addition if it is no longer needed.",
                            span=SourceSpan(path=declaration.name, start_line=1),
                        )
                    )
            diagnostics.extend(self._provider_feature_diagnostics(parsed))
            if self.strict and spec.strict:
                diagnostics.extend(contextual_diagnostics(parsed))
            else:
                # Still reject |safe / autoescape false when strict=False.
                diagnostics.extend(generic_safety_escape_diagnostics(parsed))
            inferred = inferred_capabilities(parsed)
            graph_capabilities.update(inferred)
            graph_requires.update(declaration.requires)
            for asset_id in declaration.assets:
                if asset_id not in self._assets:
                    diagnostics.append(self._unknown_asset_diagnostic(declaration.name, asset_id))
                else:
                    capability = self._registered_asset_capability(asset_id)
                    if capability:
                        graph_capabilities.add(capability)

        if root.declaration.kind is TemplateKind.PAGE and any(
            _CONDITIONAL_ASSET_RE.search(item.body) for item in graph
        ):
            diagnostics.append(
                make_diagnostic(
                    "HED-JINJA-0019",
                    severity=DiagnosticSeverity.ERROR,
                    title="Conditional page asset is not supported in format v1",
                    explanation="Page assets must be known before the document head is emitted.",
                    remediation=(
                        "Move the asset ID to a source prologue or render a fragment with "
                        "registered head management (htmx-ext-head-support / RFC-0032)."
                    ),
                    span=SourceSpan(path=root.declaration.name, start_line=1),
                )
            )
        for asset_id in spec.assets:
            if asset_id not in self._assets:
                diagnostics.append(self._unknown_asset_diagnostic(root.declaration.name, asset_id))
            else:
                capability = self._registered_asset_capability(asset_id)
                if capability:
                    graph_capabilities.add(capability)
        if root.declaration.kind is TemplateKind.FRAGMENT and (
            spec.assets
            or any(item.declaration.assets for item in graph)
            or any(_CONDITIONAL_ASSET_RE.search(item.body) for item in graph)
        ):
            graph_capabilities.add("browser.head-mutation")
        missing_requires = graph_capabilities - graph_requires
        for capability in sorted(missing_requires):
            diagnostics.append(
                make_diagnostic(
                    "HED-JINJA-0024",
                    severity=DiagnosticSeverity.ERROR,
                    title="Deployment capability is under-declared",
                    explanation=f"The template graph requires {capability!r}.",
                    remediation=(
                        "Declare it in `requires` and allow it in application policy, or "
                        "change the source."
                    ),
                    span=SourceSpan(path=root.declaration.name, start_line=1),
                )
            )
        for capability in sorted(graph_requires - graph_capabilities):
            diagnostics.append(
                make_diagnostic(
                    "HED-JINJA-0024",
                    severity=DiagnosticSeverity.WARNING,
                    title="Deployment capability is over-declared",
                    explanation=(
                        f"Declared capability {capability!r} was not inferred from the graph."
                    ),
                    remediation="Remove it if no provider or application contract needs it.",
                    span=SourceSpan(path=root.declaration.name, start_line=1),
                )
            )
        for capability in sorted(graph_capabilities - self.allowed_capabilities):
            diagnostics.append(
                make_diagnostic(
                    "HED-JINJA-0025",
                    severity=DiagnosticSeverity.ERROR,
                    title="Deployment policy denies an HDJ capability",
                    explanation=f"Application policy does not allow {capability!r}.",
                    remediation="Change the source or deliberately allow this precise capability.",
                    span=SourceSpan(path=root.declaration.name, start_line=1),
                )
            )
        return diagnostics

    def _provider_feature_diagnostics(self, parsed: ParsedHdjSource) -> list[Diagnostic]:
        features = parsed.declaration.effective_features
        extension_ids = set(self.environment.extensions)
        missing: list[str] = []
        if "jinja.i18n" in features and not any(
            "InternationalizationExtension" in item for item in extension_ids
        ):
            missing.append("jinja.i18n")
        if "jinja.do" in features and not any(
            "ExprStmtExtension" in item for item in extension_ids
        ):
            missing.append("jinja.do")
        if "jinja.loop-controls" in features and not any(
            "LoopControlExtension" in item for item in extension_ids
        ):
            missing.append("jinja.loop-controls")
        if "jinja.async" in features and not self.environment.is_async:
            missing.append("jinja.async")
        from importlib import import_module

        if "hedron.data" in features:
            try:
                import_module("hedron_data")
            except ImportError:
                missing.append("hedron.data")
        if "hedron.charts" in features:
            try:
                import_module("hedron_charts")
            except ImportError:
                missing.append("hedron.charts")
        return [
            make_diagnostic(
                "HED-JINJA-0023",
                severity=DiagnosticSeverity.ERROR,
                title="Explicit Jinja provider feature is unavailable",
                explanation=f"{feature!r} is not configured on the bound environment.",
                remediation="Configure it before binding or remove the explicit feature.",
                span=SourceSpan(path=parsed.declaration.name, start_line=1),
            )
            for feature in missing
        ]

    @staticmethod
    def _validate_spec_declaration(
        spec: TemplateSpec[Model], declaration: TemplateDeclaration
    ) -> None:
        if spec.mode is not None and spec.mode is not declaration.kind.render_mode:
            raise error(
                "HED-JINJA-0020",
                title="TemplateSpec mode assertion failed",
                explanation=f"{declaration.name!r} declares kind={declaration.kind.value!r}.",
                remediation="Correct the application assertion; it cannot override source kind.",
            )
        if spec.fragment_regions:
            declared = set(declaration.regions)
            provided = set(spec.fragment_regions)
            if declared != provided:
                raise error(
                    "HED-JINJA-0020",
                    title="Template region assertion failed",
                    explanation=(
                        f"{declaration.name!r} declares regions {sorted(declared)!r}, but the "
                        f"application supplied {sorted(provided)!r}."
                    ),
                    remediation=(
                        "Keep source region IDs and application selector definitions exact."
                    ),
                )

    @staticmethod
    def _validate_view(spec: TemplateSpec[Model], view: object) -> None:
        if spec.view_type is not None and not isinstance(view, spec.view_type):
            raise error(
                "HED-JINJA-0008",
                title="Template view contract failed",
                explanation=f"Template {spec.name!r} requires {spec.view_type.__name__}.",
                remediation="Validate and prepare the declared view model in Python.",
            )
        if not (
            isinstance(view, Model) or type(view) is dict or isinstance(view, MappingProxyType)
        ):
            raise error(
                "HED-JINJA-0008",
                title="Invalid template view",
                explanation=(
                    "Templates accept a Hedron Model, plain dict, or immutable mapping proxy."
                ),
                remediation="Materialize a bounded presentation-ready view before rendering.",
            )

    def _new_session(
        self,
        name: str,
        graph: tuple[ParsedHdjSource, ...],
        context: RenderContext | None,
        mode: RenderMode,
        diagnostics: tuple[Diagnostic, ...],
        spec: TemplateSpec[Model],
    ) -> _RenderSession:
        render_context = context or RenderContext.standalone()
        session = _RenderSession(
            binding=self,
            template_name=name,
            logical_id=spec.logical_id or f"application:{name}",
            declaration=graph[0].declaration,
            context=render_context,
            mode=mode,
            core=CoreRenderSession(render_context),
            static_asset_ids=frozenset(
                logical_id for parsed in graph for logical_id in parsed.declaration.assets
            )
            | frozenset(spec.assets),
            max_component_invocations=self.max_component_invocations,
            max_output_chars=self.max_output_chars,
            max_metadata_items=self.max_metadata_items,
            diagnostics=list(diagnostics),
        )
        for parsed in graph:
            for logical_id in parsed.declaration.assets:
                self._add_registered_asset(session, logical_id)
        for logical_id in spec.assets:
            self._add_registered_asset(session, logical_id)
        return session

    def _hdj_context(self, session: _RenderSession) -> HdjContext:
        return HdjContext(
            mode=session.mode,
            locale=session.context.locale,
            theme=session.context.theme,
            _url_builder=self.url_builder,
            _asset_builder=lambda logical_id: self._context_asset_url(session, logical_id),
            _csrf_builder=self.csrf_builder,
        )

    def _session(self) -> _RenderSession:
        session = _ACTIVE_SESSION.get()
        if session is None or session.binding is not self:
            raise error(
                "HED-JINJA-0006",
                title="HDJ bridge used outside its render session",
                explanation="A bare Jinja string cannot retain Hedron metadata.",
                remediation="Use HedronJinja.render() or render_async().",
            )
        return session

    def _render_component(
        self, alias: str, props: dict[str, object], *, caller: _JinjaCaller | None
    ) -> Markup:
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
                remediation="Register it explicitly during startup.",
            )
        key = props.pop("key", None)
        collector = _SlotCollector(alias)
        body = ""
        nesting_depth = len(session.slot_stack)
        if caller is not None:
            session.slot_stack.append(collector)
            try:
                body = str(caller())
            finally:
                session.slot_stack.pop()
        component = factory(**props)  # type: ignore[arg-type]
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
                    remediation="Provide it once or declare cardinality `many`.",
                )
            for value in values:
                component.slot(
                    slot_name,
                    html.raw(
                        TrustedHtml.reviewed(
                            value,
                            source=f"hedron-jinja:{session.template_name}:slot:{slot_name}",
                        )
                    ),
                )
        result = session.core.render(
            component,
            mode=RenderMode.FRAGMENT,
            base_depth=nesting_depth,
        )
        session.merge(result)
        return Markup(result.html)

    def _render_slot(self, name: str, caller: _JinjaCaller) -> Markup:
        session = self._session()
        if not session.slot_stack:
            raise error(
                "HED-JINJA-0007",
                title="Slot outside a component body",
                explanation="A slot tag must be inside `{% hedron ... with body %}`.",
                remediation="Move it into its owning component block.",
            )
        rendered = str(caller())
        session.slot_stack[-1].values.setdefault(name, []).append(rendered)
        return Markup("")

    def _require_asset(self, logical_id: str) -> Markup:
        session = self._session()
        if session.mode is RenderMode.PAGE:
            raise error(
                "HED-JINJA-0019",
                title="Conditional page asset is not supported in format v1",
                explanation="Page assets must be declared before the head is emitted.",
                remediation="Move the ID into the HDJ prologue.",
            )
        self._add_registered_asset(session, logical_id)
        return Markup("")

    def _add_registered_asset(self, session: _RenderSession, logical_id: str) -> None:
        asset = self._assets.get(logical_id)
        if asset is None:
            raise HedronError(self._unknown_asset_diagnostic(session.template_name, logical_id))
        key = (asset.kind, asset.href)
        previous = session.assets.get(key)
        if previous is not None and previous != asset:
            raise error(
                "HED-JINJA-0013",
                title="Conflicting registered asset",
                explanation=f"Asset {asset.href!r} has incompatible definitions.",
                remediation="Register one canonical definition.",
            )
        session.assets[key] = asset
        session.ensure_metadata_budget()

    @staticmethod
    def _unknown_asset_diagnostic(name: str, logical_id: str) -> Diagnostic:
        return make_diagnostic(
            "HED-JINJA-0019",
            severity=DiagnosticSeverity.ERROR,
            title="Unknown HDJ asset",
            explanation=f"Asset ID {logical_id!r} is not registered.",
            remediation="Register it during startup or remove the declaration.",
            span=SourceSpan(path=name, start_line=1),
        )

    def _context_asset_url(self, session: _RenderSession, logical_id: str) -> SafeUrl:
        if logical_id not in session.static_asset_ids:
            raise error(
                "HED-JINJA-0019",
                title="Asset URL is not statically declared",
                explanation=f"Asset ID {logical_id!r} is outside the template's static graph.",
                remediation=(
                    "Declare it in the prologue/TemplateSpec, or use `hedron_asset` for a "
                    "conditional fragment dependency."
                ),
            )
        asset = self._assets.get(logical_id)
        if asset is None:
            raise HedronError(self._unknown_asset_diagnostic("<render>", logical_id))
        self._add_registered_asset(session, logical_id)
        parts = urlsplit(asset.href)
        return SafeUrl.parse(
            asset.href,
            purpose=UrlPurpose.ASSET,
            allow_external=parts.scheme in {"http", "https"},
        )

    def _registered_asset_capability(self, logical_id: str) -> str | None:
        asset = self._assets.get(logical_id)
        if asset is None:
            return None
        parts = urlsplit(asset.href)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            return None
        purpose = self._asset_kind_purpose(asset.kind)
        if purpose is None:
            return None
        return f"network.{purpose}-origin:{parts.scheme.lower()}://{parts.netloc.lower()}"

    @staticmethod
    def _asset_kind_purpose(kind: str) -> str | None:
        lowered = kind.lower()
        if lowered in {"css", "style", "stylesheet"}:
            return "style"
        if lowered in {"script", "module", "javascript"}:
            return "script"
        if lowered in {"image", "img"}:
            return "image"
        if lowered == "font":
            return "font"
        if lowered in {"audio", "video", "media"}:
            return "media"
        return None

    def _finish(self, session: _RenderSession, rendered: str) -> RenderResult:
        session.ensure_metadata_budget()
        if session.mode is RenderMode.PAGE:
            if not _valid_page_shape(rendered):
                raise error(
                    "HED-JINJA-0017",
                    title="Invalid page template shape",
                    explanation="Page templates need one doctype, html, head, and body element.",
                    remediation="Emit one complete document or declare a fragment.",
                )
        elif _document_tokens(rendered):
            raise error(
                "HED-JINJA-0017",
                title="Document element in fragment",
                explanation="Fragment templates cannot emit html, head, or body elements.",
                remediation="Declare a page or remove document-level markup.",
            )
        return RenderResult(
            html=rendered,
            mode=session.mode,
            assets=tuple(session.assets.values()),
            headers=MappingProxyType(dict(session.headers)),
            identity_map=session.core.identity_map,
            diagnostics=tuple(session.diagnostics),
            trace=MappingProxyType(
                {
                    "template": session.template_name,
                    "template_logical_id": session.logical_id,
                    "component_invocations": session.component_invocations,
                    "node_count": session.core.node_count,
                    "components": tuple(session.traces),
                }
            ),
        )

    @staticmethod
    def _raise_output_limit(session: _RenderSession) -> None:
        raise error(
            "HED-JINJA-0012",
            title="Template output limit exceeded",
            explanation=f"Template output exceeds {session.max_output_chars} characters.",
            remediation="Reduce rendered data or split the response into bounded fragments.",
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

    def _fingerprint_environment(self) -> tuple[object, ...]:
        loader = self.environment.loader
        return (
            id(loader),
            tuple(sorted((name, id(value)) for name, value in self.environment.filters.items())),
            tuple(sorted((name, id(value)) for name, value in self.environment.tests.items())),
            tuple(sorted((name, id(value)) for name, value in self.environment.globals.items())),
            tuple(
                sorted((name, type(value)) for name, value in self.environment.extensions.items())
            ),
            self.environment.undefined,
            self.environment.autoescape,
            self.environment.finalize,
            self.environment.is_async,
            tuple(
                sorted(
                    (name, _fingerprint_policy(value))
                    for name, value in self.environment.policies.items()
                )
            ),
            id(self.environment.bytecode_cache),
            self.environment.block_start_string,
            self.environment.block_end_string,
            self.environment.variable_start_string,
            self.environment.variable_end_string,
            self.environment.comment_start_string,
            self.environment.comment_end_string,
            self.environment.line_statement_prefix,
            self.environment.line_comment_prefix,
            self.environment.trim_blocks,
            self.environment.lstrip_blocks,
            self.environment.newline_sequence,
            self.environment.keep_trailing_newline,
        )

    def _assert_environment_unchanged(self) -> None:
        if self._fingerprint_environment() != self._environment_fingerprint:
            raise error(
                "HED-JINJA-0014",
                title="Jinja environment mutated after HDJ binding",
                explanation=(
                    "Loaders, extensions, filters, tests, globals, or safety settings changed."
                ),
                remediation="Fully configure a fresh Environment before constructing HedronJinja.",
            )

    @staticmethod
    def _generic_safe_filter(value: object) -> Markup:
        del value
        raise error(
            "HED-JINJA-0009",
            title="Generic Jinja safe filter rejected",
            explanation=(
                "The generic Jinja `safe` filter is never allowed in HDJ; "
                "use `hedron_trusted` with a reviewed TrustedHtml value."
            ),
            remediation="Create trusted content at a reviewed Python boundary.",
        )

    @staticmethod
    def _trusted_filter(value: object) -> Markup:
        if not isinstance(value, TrustedHtml):
            raise error(
                "HED-JINJA-0009",
                title="TrustedHtml required",
                explanation="`hedron_trusted` accepts only a reviewed TrustedHtml value.",
                remediation="Create trusted content at a reviewed Python boundary.",
            )
        return Markup(value.value)

    @staticmethod
    def _url_for_purpose(value: object, purpose: UrlPurpose, filter_name: str) -> str:
        if not isinstance(value, SafeUrl) or value.purpose is not purpose:
            raise error(
                "HED-JINJA-0010",
                title="Purpose-compatible SafeUrl required",
                explanation=f"`{filter_name}` requires purpose={purpose.value!r}.",
                remediation="Construct or reverse the URL for the destination sink.",
            )
        return value.value

    def _navigation_url_filter(self, value: object) -> str:
        url = self._url_for_purpose(value, UrlPurpose.NAVIGATION, "hedron_nav_url")
        self._reject_external_dynamic_url(url, "hedron_nav_url")
        return url

    def _form_url_filter(self, value: object) -> str:
        url = self._url_for_purpose(value, UrlPurpose.FORM_ACTION, "hedron_form_url")
        self._reject_external_dynamic_url(url, "hedron_form_url")
        return url

    def _asset_url_filter(self, value: object) -> str:
        url = self._url_for_purpose(value, UrlPurpose.ASSET, "hedron_asset_url")
        parts = urlsplit(url)
        if parts.scheme in {"http", "https"}:
            session = self._session()
            if not any(asset.href == url for asset in session.assets.values()):
                raise error(
                    "HED-JINJA-0010",
                    title="External asset URL is not registered for this template",
                    explanation="A dynamic external asset URL has no graph-owned capability proof.",
                    remediation="Declare the registered asset and resolve it with hdj.asset_url().",
                )
        return url

    @staticmethod
    def _reject_external_dynamic_url(url: str, filter_name: str) -> None:
        if urlsplit(url).scheme in {"http", "https"}:
            raise error(
                "HED-JINJA-0010",
                title="Dynamic external URL is not a format-v1 input",
                explanation=f"`{filter_name}` cannot reconcile a runtime origin in phase 0.9.",
                remediation=(
                    "Use a local SafeUrl or trusted literal source; native origin policy is "
                    "scheduled for phase 0.11."
                ),
            )


def _valid_page_shape(rendered: str) -> bool:
    return _PAGE_DOCTYPE_RE.search(rendered) is not None and _document_tokens(rendered) == (
        "html",
        "head",
        "/head",
        "body",
        "/body",
        "/html",
    )


class _DocumentShapeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.tokens: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        lowered = tag.lower()
        if lowered in {"html", "head", "body"}:
            self.tokens.append(lowered)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered in {"html", "head", "body"}:
            self.tokens.append(f"/{lowered}")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)


def _document_tokens(rendered: str) -> tuple[str, ...]:
    parser = _DocumentShapeParser()
    parser.feed(rendered)
    parser.close()
    return tuple(parser.tokens)


def _fingerprint_policy(value: object) -> object:
    if isinstance(value, Mapping):
        return tuple(sorted((str(key), _fingerprint_policy(item)) for key, item in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_fingerprint_policy(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return tuple(sorted(repr(_fingerprint_policy(item)) for item in value))
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    return (type(value).__qualname__, id(value))
