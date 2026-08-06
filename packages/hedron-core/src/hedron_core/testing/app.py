"""HTTP-faithful application scenario harness (phase 0.15 / RFC-0036)."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from html.parser import HTMLParser

from hedron_core.interaction import FragmentRegion
from hedron_core.testing.adapters import (
    AdapterAppFixture,
    AdapterResponse,
    assert_fragment_body,
    assert_html_contains,
    assert_htmx_trigger,
    assert_hx_push_url,
    assert_hx_redirect,
    assert_hx_reswap,
    assert_hx_retarget,
    assert_oob_present,
    assert_page_document,
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
    "MarkedElement",
    "assert_action_authorized",
    "assert_fragment_body",
    "assert_html_contains",
    "assert_http_fallback_present",
    "assert_htmx_trigger",
    "assert_hx_push_url",
    "assert_hx_redirect",
    "assert_hx_reswap",
    "assert_hx_retarget",
    "assert_oob_present",
    "assert_page_document",
    "assert_shell_dual_path",
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
    cookies: dict[str, str] = field(default_factory=dict)
    last_response: AdapterResponse | None = None

    @classmethod
    def from_fixture(cls, fixture: AdapterAppFixture) -> AppScenario:
        return cls(_get=fixture.get, _post=fixture.post)

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

    def _require_response(self) -> AdapterResponse:
        assert self.last_response is not None, "no response recorded; make a request first"
        return self.last_response
