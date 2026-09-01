"""HTTP-faithful application scenario harness (phase 0.15 / RFC-0036)."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from hedron_core.catalog import CatalogEntry, InteractionCatalog

from hedron_core.interaction import FragmentRegion
from hedron_core.testing.adapters import (
    AdapterAppFixture,
    AdapterResponse,
    assert_dialog_markup,
    assert_fragment_body,
    assert_html_contains,
    assert_htmx_trigger,
    assert_hx_push_url,
    assert_hx_redirect,
    assert_hx_reswap,
    assert_hx_retarget,
    assert_lazy_markup,
    assert_oob_present,
    assert_page_document,
    assert_pagination_markup,
    assert_tabs_markup,
    assert_toast_markup,
)
from hedron_core.testing.htmx_asserts import (
    assert_shell_dual_path,
    assert_ui_targets_subset_of_regions,
    assert_undeclared_target_rejected,
)
from hedron_core.testing.workbench import (
    assert_action_authorized,
    assert_http_fallback_present,
    assert_transform_plan_bounded,
)

__all__ = [
    "AppScenario",
    "ModelDemoScenario",
    "MarkedElement",
    "assert_action_authorized",
    "assert_dialog_markup",
    "assert_fragment_body",
    "assert_html_contains",
    "assert_http_fallback_present",
    "assert_htmx_trigger",
    "assert_hx_push_url",
    "assert_hx_redirect",
    "assert_hx_reswap",
    "assert_hx_retarget",
    "assert_lazy_markup",
    "assert_oob_present",
    "assert_page_document",
    "assert_pagination_markup",
    "assert_shell_dual_path",
    "assert_tabs_markup",
    "assert_toast_markup",
    "assert_transform_plan_bounded",
    "assert_ui_targets_subset_of_regions",
    "assert_undeclared_target_rejected",
    "find_all_marks",
    "find_mark",
]

GetFn = Callable[..., AdapterResponse]
PostFn = Callable[..., AdapterResponse]


@dataclass(frozen=True, slots=True)
class MarkedElement:
    """A rendered element identified by ``data-hedron-mark``."""

    mark: str
    tag: str
    attrs: Mapping[str, str]
    html: str


class _MarkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[MarkedElement] = []
        self._stack: list[tuple[str, dict[str, str], int, str | None]] = []
        self._chunks: list[str] = []
        self._pos = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k: ("" if v is None else v) for k, v in attrs}
        mark = attr_map.get("data-hedron-mark")
        rendered = self.get_starttag_text() or f"<{tag}>"
        start = self._pos
        self._chunks.append(rendered)
        self._pos += len(rendered)
        self._stack.append((tag, attr_map, start, mark))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k: ("" if v is None else v) for k, v in attrs}
        mark = attr_map.get("data-hedron-mark")
        rendered = self.get_starttag_text() or f"<{tag} />"
        self._chunks.append(rendered)
        self._pos += len(rendered)
        if mark is not None:
            self.elements.append(MarkedElement(mark=mark, tag=tag, attrs=attr_map, html=rendered))

    def handle_endtag(self, tag: str) -> None:
        rendered = f"</{tag}>"
        self._chunks.append(rendered)
        self._pos += len(rendered)
        for idx in range(len(self._stack) - 1, -1, -1):
            open_tag, attr_map, start, mark = self._stack[idx]
            if open_tag != tag:
                continue
            self._stack.pop(idx)
            if mark is not None:
                html = "".join(self._chunks)[start : self._pos]
                self.elements.append(MarkedElement(mark=mark, tag=tag, attrs=attr_map, html=html))
            break

    def handle_data(self, data: str) -> None:
        self._chunks.append(data)
        self._pos += len(data)

    def handle_entityref(self, name: str) -> None:
        chunk = f"&{name};"
        self._chunks.append(chunk)
        self._pos += len(chunk)

    def handle_charref(self, name: str) -> None:
        chunk = f"&#{name};"
        self._chunks.append(chunk)
        self._pos += len(chunk)

    def handle_comment(self, data: str) -> None:
        chunk = f"<!--{data}-->"
        self._chunks.append(chunk)
        self._pos += len(chunk)


def find_all_marks(html: str, *, mark: str | None = None) -> list[MarkedElement]:
    """Parse HTML and return elements bearing ``data-hedron-mark``."""
    parser = _MarkCollector()
    parser.feed(html)
    parser.close()
    if mark is None:
        return list(parser.elements)
    return [el for el in parser.elements if el.mark == mark]


def find_mark(html: str, *, mark: str) -> MarkedElement:
    """Return the first marked element or raise ``AssertionError``."""
    matches = find_all_marks(html, mark=mark)
    assert matches, f"no element with data-hedron-mark={mark!r} in {html!r}"
    return matches[0]


@dataclass
class AppScenario:
    """Cookie-retaining HTTP scenario over an :class:`AdapterAppFixture` or callables."""

    _get: GetFn
    _post: PostFn
    _catalog: Callable[[str | None], object] | None = None
    cookies: dict[str, str] = field(default_factory=dict[str, str])
    last_response: AdapterResponse | None = None

    @classmethod
    def from_fixture(cls, fixture: AdapterAppFixture) -> AppScenario:
        catalog_method = getattr(fixture, "catalog", None)
        return cls(
            _get=fixture.get,
            _post=fixture.post,
            _catalog=(
                (lambda app_id: catalog_method(app_id=app_id)) if callable(catalog_method) else None
            ),
        )

    @classmethod
    def from_callables(cls, get: GetFn, post: PostFn) -> AppScenario:
        return cls(_get=get, _post=post)

    def __init__(
        self,
        fixture: AdapterAppFixture | GetFn | None = None,
        post: PostFn | None = None,
        *,
        cookies: Mapping[str, str] | None = None,
        _get: GetFn | None = None,
        _post: PostFn | None = None,
        _catalog: Callable[[str | None], object] | None = None,
    ) -> None:
        if _get is not None and _post is not None:
            resolved_get, resolved_post = _get, _post
        elif post is not None and fixture is not None and callable(fixture):
            resolved_get, resolved_post = fixture, post  # type: ignore[assignment]
        elif fixture is not None and hasattr(fixture, "get") and hasattr(fixture, "post"):
            resolved_get = fixture.get  # type: ignore[union-attr]
            resolved_post = fixture.post  # type: ignore[union-attr]
        else:
            raise TypeError("AppScenario requires an AdapterAppFixture or get/post callables")
        self._get = resolved_get
        self._post = resolved_post
        self._catalog = _catalog
        catalog_method = getattr(fixture, "catalog", None)
        if self._catalog is None and callable(catalog_method):
            self._catalog = lambda app_id: catalog_method(app_id=app_id)
        self.cookies = dict(cookies or {})
        self.last_response = None

    def _merge_cookies(self, response: AdapterResponse) -> AdapterResponse:
        self.cookies.update(dict(response.cookies))
        self.last_response = response
        return response

    def _headers(self, headers: Mapping[str, str] | None) -> dict[str, str]:
        return dict(headers or {})

    def get(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
    ) -> AdapterResponse:
        jar = {**self.cookies, **dict(cookies or {})}
        response = self._get(path, headers=self._headers(headers), cookies=jar)
        return self._merge_cookies(response)

    def post(
        self,
        path: str,
        *,
        data: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
    ) -> AdapterResponse:
        jar = {**self.cookies, **dict(cookies or {})}
        response = self._post(
            path,
            data=dict(data or {}),
            headers=self._headers(headers),
            cookies=jar,
        )
        return self._merge_cookies(response)

    def navigate(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
    ) -> AdapterResponse:
        return self.get(path, headers=headers, cookies=cookies)

    def fragment_get(
        self,
        path: str,
        *,
        target: str | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
    ) -> AdapterResponse:
        hdrs = self._headers(headers)
        hdrs["HX-Request"] = "true"
        if target is not None:
            hdrs["HX-Target"] = target
        return self.get(path, headers=hdrs, cookies=cookies)

    def fragment_post(
        self,
        path: str,
        *,
        data: Mapping[str, str] | None = None,
        target: str | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
    ) -> AdapterResponse:
        hdrs = self._headers(headers)
        hdrs["HX-Request"] = "true"
        if target is not None:
            hdrs["HX-Target"] = target
        return self.post(path, data=data, headers=hdrs, cookies=cookies)

    def submit_model(
        self,
        path: str,
        model: object,
        *,
        target: str | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
    ) -> AdapterResponse:
        """POST a Pydantic/FormBody model as urlencoded fields (no secret echo)."""
        dump = getattr(model, "model_dump", None)
        if not callable(dump):
            raise TypeError("submit_model requires a Pydantic model instance")
        dumped_raw = dump()
        if not isinstance(dumped_raw, Mapping):
            raise TypeError("submit_model requires model_dump() to return a mapping")
        dumped = cast(Mapping[object, object], dumped_raw)
        data = {str(key): "" if value is None else str(value) for key, value in dumped.items()}
        return self.fragment_post(path, data=data, target=target, headers=headers, cookies=cookies)

    def catalog(self, *, app_id: str | None = None) -> InteractionCatalog:
        """Compile the current interaction catalog for test assertions."""
        if self._catalog is not None:
            return cast("InteractionCatalog", self._catalog(app_id))
        from hedron_core.catalog import compile_interaction_catalog

        return compile_interaction_catalog(app_id=app_id)

    def catalog_entry(self, logical_id: str, *, app_id: str | None = None) -> CatalogEntry:
        """Return one required catalog entry or raise its domain diagnostic."""
        return self.catalog(app_id=app_id).require(logical_id)

    def assert_catalog_kind(
        self,
        logical_id: str,
        kind: str,
        *,
        app_id: str | None = None,
    ) -> CatalogEntry:
        """Assert an entry kind and return the matching catalog entry."""
        entry = self.catalog_entry(logical_id, app_id=app_id)
        assert entry.kind == kind, f"{logical_id} kind {entry.kind!r} != {kind!r}"
        return entry

    def field_path_errors(self, payload: Mapping[str, object] | Sequence[object]) -> list[str]:
        """Extract model field paths from a validation error payload."""
        rows: Sequence[object]
        if isinstance(payload, Mapping):
            detail = payload.get("detail", payload.get("errors", ()))
            rows = (
                cast(Sequence[object], detail)
                if isinstance(detail, Sequence) and not isinstance(detail, (str, bytes))
                else ()
            )
        else:
            rows = payload
        paths: list[str] = []
        for item in rows:
            if isinstance(item, Mapping):
                row = cast(Mapping[str, object], item)
                loc = row.get("loc") or row.get("path")
                if isinstance(loc, Sequence) and not isinstance(loc, (str, bytes)):
                    location = cast(Sequence[object], loc)
                    paths.append(".".join(str(part) for part in location if part not in {"body"}))
        return paths

    def _html(self, html: str | None) -> str:
        if html is not None:
            return html
        assert self.last_response is not None, "no response body; pass html= or make a request"
        return self.last_response.body

    def find(self, *, mark: str, html: str | None = None) -> MarkedElement:
        return find_mark(self._html(html), mark=mark)

    def find_all(self, *, mark: str | None = None, html: str | None = None) -> list[MarkedElement]:
        return find_all_marks(self._html(html), mark=mark)

    def assert_html_contains(self, needle: str, *, response: AdapterResponse | None = None) -> None:
        assert_html_contains(response or self._require_response(), needle)

    def assert_page_document(self, response: AdapterResponse | None = None) -> None:
        assert_page_document(response or self._require_response())

    def assert_fragment_body(
        self,
        *,
        contains: str,
        response: AdapterResponse | None = None,
    ) -> None:
        assert_fragment_body(response or self._require_response(), contains=contains)

    def assert_htmx_trigger(self, event: str, *, response: AdapterResponse | None = None) -> None:
        assert_htmx_trigger(response or self._require_response(), event)

    def assert_hx_redirect(self, url: str, *, response: AdapterResponse | None = None) -> None:
        assert_hx_redirect(response or self._require_response(), url)

    def assert_hx_push_url(self, url: str, *, response: AdapterResponse | None = None) -> None:
        assert_hx_push_url(response or self._require_response(), url)

    def assert_hx_retarget(self, selector: str, *, response: AdapterResponse | None = None) -> None:
        assert_hx_retarget(response or self._require_response(), selector)

    def assert_hx_reswap(self, swap: str, *, response: AdapterResponse | None = None) -> None:
        assert_hx_reswap(response or self._require_response(), swap)

    def assert_oob_present(
        self,
        *,
        contains: str | None = None,
        response: AdapterResponse | None = None,
    ) -> None:
        assert_oob_present(response or self._require_response(), contains=contains)

    def assert_toast_markup(
        self,
        *,
        contains: str | None = None,
        response: AdapterResponse | None = None,
    ) -> None:
        assert_toast_markup(response or self._require_response(), contains=contains)

    def assert_dialog_markup(
        self,
        *,
        contains: str | None = None,
        response: AdapterResponse | None = None,
    ) -> None:
        assert_dialog_markup(response or self._require_response(), contains=contains)

    def assert_tabs_markup(
        self,
        *,
        contains: str | None = None,
        response: AdapterResponse | None = None,
    ) -> None:
        assert_tabs_markup(response or self._require_response(), contains=contains)

    def assert_pagination_markup(
        self,
        *,
        contains: str | None = None,
        response: AdapterResponse | None = None,
    ) -> None:
        assert_pagination_markup(response or self._require_response(), contains=contains)

    def assert_lazy_markup(
        self,
        *,
        contains: str | None = None,
        response: AdapterResponse | None = None,
    ) -> None:
        assert_lazy_markup(response or self._require_response(), contains=contains)

    def assert_undeclared_target_rejected(self, response: AdapterResponse | None = None) -> None:
        assert_undeclared_target_rejected(response or self._require_response())

    def assert_ui_targets_subset_of_regions(
        self,
        regions: Sequence[FragmentRegion | str],
        *,
        html: str | None = None,
    ) -> None:
        assert_ui_targets_subset_of_regions(self._html(html), regions)

    def assert_shell_dual_path(
        self,
        fragment_response: AdapterResponse,
        page_response: AdapterResponse,
        *,
        fragment_contains: str | None = None,
    ) -> None:
        assert_shell_dual_path(
            fragment_response,
            page_response,
            fragment_contains=fragment_contains,
        )

    def assert_transform_plan_bounded(self, plan: object, *, max_rows: int) -> None:
        assert_transform_plan_bounded(plan, max_rows=max_rows)

    def assert_action_authorized(
        self, action: Mapping[str, object], *, expect: bool = True
    ) -> None:
        assert_action_authorized(action, expect=expect)

    def assert_http_fallback_present(self, token: str, *, html: str | None = None) -> None:
        assert_http_fallback_present(self._html(html), token=token)

    def refresh(
        self,
        handle: object,
        *,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
    ) -> AdapterResponse:
        path = str(getattr(handle, "path", "") or "")
        selector = str(getattr(handle, "selector", "") or "")
        return self.fragment_get(
            path,
            target=selector.removeprefix("#") or None,
            headers=headers,
            cookies=cookies,
        )

    def run(
        self,
        handle: object,
        *,
        data: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: Mapping[str, str] | None = None,
    ) -> AdapterResponse:
        path = str(getattr(handle, "path", "") or "")
        return self.fragment_post(path, data=data, headers=headers, cookies=cookies)

    def expect(
        self,
        handle: object,
        *,
        contains: str,
        response: AdapterResponse | None = None,
    ) -> None:
        row = response or self._require_response()
        host_id = str(getattr(handle, "dom_id", "") or getattr(handle, "logical_id", ""))
        assert contains in row.body, f"expected {contains!r} in {row.body!r}"
        if host_id:
            assert host_id in row.body or f"#{host_id}" in row.body, row.body

    def expect_refreshes(
        self,
        *handles: object,
        response: AdapterResponse | None = None,
    ) -> None:
        from hedron_core.updates import refresh_event_name

        row = response or self._require_response()
        for handle in handles:
            event = refresh_event_name(str(getattr(handle, "dom_id", "") or ""))
            assert_htmx_trigger(row, event)

    def expect_patch(
        self,
        handle: object,
        *,
        contains: str,
        response: AdapterResponse | None = None,
    ) -> None:
        row = response or self._require_response()
        assert contains in row.body, f"expected patch body {contains!r} in {row.body!r}"
        selector = str(getattr(handle, "selector", "") or "")
        if selector:
            retarget = row.headers.get("HX-Retarget") or row.headers.get("hx-retarget") or ""
            assert selector == retarget or not retarget or selector.removeprefix("#") in retarget

    def _require_response(self) -> AdapterResponse:
        assert self.last_response is not None, "no response recorded; make a request first"
        return self.last_response


@dataclass
class ModelDemoScenario:
    """Scenario kit for model demos (RFC-0047 / SCENARIO-018).

    Supplies synthetic bounded files and model results only — never loads a real
    model or treats generated output as trustworthy test data by default.
    """

    app: AppScenario
    synthetic_files: dict[str, bytes] = field(default_factory=dict[str, bytes])
    synthetic_results: dict[str, Mapping[str, object]] = field(
        default_factory=dict[str, Mapping[str, object]]
    )
    trust_generated_output: bool = False
    max_file_bytes: int = 64_000
    admissions: list[str] = field(default_factory=list[str])
    progress_events: list[Mapping[str, object]] = field(default_factory=list[Mapping[str, object]])
    cancellations: list[str] = field(default_factory=list[str])
    consent_granted: bool = False
    redacted_fields: list[str] = field(default_factory=list[str])
    retained_record_ids: list[str] = field(default_factory=list[str])

    def add_synthetic_file(self, name: str, content: bytes) -> None:
        if len(content) > self.max_file_bytes:
            raise AssertionError(
                f"synthetic file {name!r} exceeds max_file_bytes={self.max_file_bytes}"
            )
        self.synthetic_files[name] = content

    def add_synthetic_result(self, result_id: str, payload: Mapping[str, object]) -> None:
        if self.trust_generated_output:
            raise AssertionError(
                "ModelDemoScenario refuses to treat generated output as trustworthy "
                "test data by default; keep trust_generated_output=False"
            )
        self.synthetic_results[result_id] = dict(payload)

    def record_admission(self, outcome: str) -> None:
        self.admissions.append(outcome)

    def record_progress(self, event: Mapping[str, object]) -> None:
        self.progress_events.append(dict(event))

    def record_cancellation(self, request_id: str) -> None:
        self.cancellations.append(request_id)

    def grant_consent(self) -> None:
        self.consent_granted = True

    def assert_consent_required(self) -> None:
        assert self.consent_granted, "consent was not granted for feedback/demo scenario"

    def assert_redaction(self, *fields: str) -> None:
        missing = [f for f in fields if f not in self.redacted_fields]
        assert not missing, f"expected redacted fields missing: {missing}"

    def mark_redacted(self, *fields: str) -> None:
        self.redacted_fields.extend(fields)

    def retain(self, record_id: str) -> None:
        self.retained_record_ids.append(record_id)

    def assert_retention_deletable(self, record_id: str) -> None:
        assert record_id in self.retained_record_ids
        self.retained_record_ids.remove(record_id)

    def assert_no_real_model_loaded(self) -> None:
        # Synthetic kit never loads models; this documents the contract for suites.
        assert self.trust_generated_output is False
        assert all(isinstance(v, bytes) for v in self.synthetic_files.values())
