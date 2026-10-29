"""Public scenario mechanics behind ``hedron.testing.browser_scenario``."""

from __future__ import annotations

import contextlib
import re
import time
import uuid
from collections import deque
from collections.abc import Callable, Generator, Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, cast, final
from urllib.parse import urlsplit

from hedron.testing._ui_testing.contribution import UITestingContribution
from hedron.testing._ui_testing.host import (
    ManagedASGIHost,
    ManagedHostCleanupError,
    ManagedHostError,
    validate_loopback_url,
    validate_origin,
)

if TYPE_CHECKING:
    from playwright.sync_api import (
        BrowserContext,
        ConsoleMessage,
        Frame,
        Locator,
        Page,
        Route,
        WebSocketRoute,
    )

_EVENT_CAPACITY = 256
_ERROR_CAPACITY = 128
_MAX_SCENARIOS = 16
_MANIFEST_EVENT_LIMIT = 256
_TARGET_RE = re.compile(r"[A-Za-z][A-Za-z0-9_.:-]{0,79}\Z")
_BINDING_RE = re.compile(r"__hedron_ui_[0-9a-f]{32}\Z")


class UIHarnessError(RuntimeError):
    """Base error for Hedron browser-scenario setup and observation."""


class UIConfigurationError(UIHarnessError):
    """The requested browser scenario violates the selected test profile."""


class InvalidCheckpointError(UIHarnessError):
    """A checkpoint belongs to another scenario or navigation epoch."""


class ObservationUnavailableError(UIHarnessError):
    """The page does not expose the lifecycle facts required by ``settle``."""


class SettleTimeoutError(UIHarnessError):
    """No matching request completed inside the caller's settle deadline."""


class AmbiguousSettleError(UIHarnessError):
    """More than one observed action request could satisfy a settle call."""


class CleanCheckError(UIHarnessError):
    """Unexpected browser, network, application, or cleanup activity was observed."""


@dataclass(frozen=True, slots=True)
class Checkpoint:
    """Opaque position in one page's observed lifecycle event stream."""

    session_id: str
    navigation_epoch: int
    sequence: int
    document_id: str
    dropped_count: int
    network_sequence: int


@dataclass(frozen=True, slots=True)
class SettleResult:
    """Bounded facts for the matching browser-observed HTMX request."""

    request_id: int
    target: str
    generation: int | None
    status: int | None
    cancelled: bool
    swapped: bool
    settled: bool
    elapsed_seconds: float


@dataclass(frozen=True, slots=True)
class UIEvent:
    """One allowlisted lifecycle fact; arbitrary page and request values are omitted."""

    sequence: int
    navigation_epoch: int
    kind: str
    request_id: int | None = None
    status: int | None = None
    target: str | None = None
    generation: int | None = None


@dataclass(slots=True)
class _ExpectedHTTP:
    method: str
    path: str
    status: int
    count: int
    checkpoint: Checkpoint
    observed: int = 0
    closed: bool = False
    resource_console_observed: bool = False
    htmx_console_observed: bool = False


@dataclass(slots=True)
class _Request:
    method: str
    path: str
    origin: str
    resource_type: str
    epoch: int
    sequence: int
    status: int | None = None
    finished: bool = False
    failed: bool = False


class BrowserScenarioFactory:
    """Create one isolated context-managed browser scenario per pytest test.

    Construct this through the ``hedron_ui`` fixture. Native Playwright owns
    every locator, action, and assertion; Hedron adds hosting and observation.
    """

    def __init__(
        self,
        *,
        new_context: Callable[..., object],
        artifact_writer: Callable[[Mapping[str, object]], None] | None = None,
        context_args: Mapping[str, object] | None = None,
        allowed_origins: Sequence[str] = (),
        startup_timeout: float = 15.0,
        shutdown_timeout: float = 5.0,
        event_capacity: int = _EVENT_CAPACITY,
        capture_profile: Literal["structured", "synthetic"] = "structured",
        synthetic_data_declared: bool = False,
        contributions: Sequence[UITestingContribution] = (),
    ) -> None:
        if event_capacity < 16 or event_capacity > 4096:
            raise ValueError("event_capacity must be between 16 and 4096")
        self._new_context: Callable[..., object] = new_context
        self._artifact_writer: Callable[[Mapping[str, object]], None] | None = artifact_writer
        self._context_args: dict[str, object] = dict(context_args or {})
        self._allowed_origins: tuple[str, ...] = tuple(
            validate_origin(origin) for origin in allowed_origins
        )
        self._startup_timeout: float = startup_timeout
        self._shutdown_timeout: float = shutdown_timeout
        self._event_capacity: int = event_capacity
        if capture_profile not in {"structured", "synthetic"}:
            raise ValueError("capture_profile must be 'structured' or 'synthetic'")
        self._capture_profile: Literal["structured", "synthetic"] = capture_profile
        self._synthetic_data_declared: bool = synthetic_data_declared
        self._contributions: tuple[UITestingContribution, ...] = tuple(contributions)
        self._session_id: str = uuid.uuid4().hex
        self._sessions: list[BrowserScenario] = []
        self._errors: deque[str] = deque(maxlen=_ERROR_CAPACITY)
        self._closed: bool = False

    def from_app(
        self,
        factory: str,
        *,
        config: Mapping[str, object] | None = None,
        root_path: str | None = None,
        allowed_origins: Sequence[str] = (),
        synthetic: bool = False,
    ) -> _ScenarioManager:
        """Run an importable app factory in a spawned child process."""
        return _ScenarioManager(
            owner=self,
            source="managed",
            factory=factory,
            config=config,
            root_path=root_path,
            allowed_origins=allowed_origins,
            synthetic=synthetic,
        )

    def from_url(
        self,
        base_url: str,
        *,
        allowed_origins: Sequence[str] = (),
        synthetic: bool = False,
    ) -> _ScenarioManager:
        """Use a caller-owned HTTP(S) service on a literal loopback address."""
        origin, path = validate_loopback_url(base_url)
        if "?" in path:
            raise ValueError("base_url must not contain query values")
        return _ScenarioManager(
            owner=self,
            source="external",
            base_url=base_url.rstrip("/"),
            base_origin=origin,
            base_path=path,
            allowed_origins=allowed_origins,
            synthetic=synthetic,
        )

    @property
    def sessions(self) -> tuple[BrowserScenario, ...]:
        """Scenarios created by this fixture, including closed scenarios."""
        return tuple(self._sessions)

    @property
    def errors(self) -> tuple[str, ...]:
        """Bounded internal error categories for structured failure evidence."""
        return tuple(self._errors)

    @property
    def contributions(self) -> tuple[Mapping[str, object], ...]:
        """Validated, explicitly loaded package contribution metadata."""
        return tuple(contribution.to_metadata() for contribution in self._contributions)

    def _opened(self, session: BrowserScenario) -> None:
        if self._closed:
            raise UIHarnessError("hedron_ui fixture has already closed")
        if len(self._sessions) >= _MAX_SCENARIOS:
            raise UIHarnessError(f"a test may create at most {_MAX_SCENARIOS} browser scenarios")
        self._sessions.append(session)

    def _lease_context(self) -> object:
        if self._context_args.get("service_workers", "block") != "block":
            raise UIConfigurationError(
                "controlled UI tests require service_workers='block'; adjust browser_context_args"
            )
        # The supported pytest-playwright factory applies upstream options,
        # markers, capture hooks, and its single context finalizer.
        return self._new_context()

    def _record_error(self, category: str) -> None:
        safe = category if re.fullmatch(r"[a-z][a-z0-9_]{0,63}", category) else "harness_error"
        self._errors.append(safe)

    def close_all(
        self,
        *,
        primary_error: BaseException | None = None,
        test_failed: bool = False,
        failure_phases: Sequence[str] = (),
    ) -> None:
        """Close forgotten sessions and perform the fixture's automatic clean check."""
        if self._closed:
            return
        self._closed = True
        cleanup: list[str] = []
        for session in reversed(self._sessions):
            if session.is_open:
                try:
                    session.close(primary_error=primary_error)
                except (Exception, KeyboardInterrupt, SystemExit) as exc:  # noqa: BLE001
                    cleanup.append(_exception_name(exc))
        issues = list(self._errors)
        for session in self._sessions:
            issues.extend(session._clean_categories())  # pyright: ignore[reportPrivateUsage]
        issues.extend(cleanup)
        if test_failed:
            issues.append("test_failure")
        if issues:
            try:
                self._write_failure_manifest(
                    issues,
                    primary_error,
                    test_failed=test_failed,
                    failure_phases=failure_phases,
                )
            except Exception as exc:
                self._record_error("manifest_write_failed")
                if primary_error is not None:
                    primary_error.add_note(
                        f"Hedron UI manifest write failed ({_exception_name(exc)})"
                    )
                elif not test_failed:
                    raise CleanCheckError(
                        f"Hedron UI failure manifest could not be written ({_exception_name(exc)})"
                    ) from exc
            summary = ", ".join(sorted(set(issues)))
            if primary_error is not None:
                primary_error.add_note(f"Hedron UI clean check: {summary}")
                return
            if test_failed:
                return
            raise CleanCheckError(f"Hedron UI clean check failed: {summary}")

    def _write_failure_manifest(
        self,
        issues: Sequence[str],
        primary_error: BaseException | None,
        *,
        test_failed: bool = False,
        failure_phases: Sequence[str] = (),
    ) -> None:
        if self._artifact_writer is None:
            return
        self._artifact_writer(
            {
                "schema_version": 1,
                "session_id": self._session_id,
                "failure_categories": sorted(set(issues))[:_ERROR_CAPACITY],
                "primary_exception_type": (
                    _exception_name(primary_error) if primary_error is not None else None
                ),
                "test_failure_already_reported": test_failed,
                "test_failure_phases": sorted(
                    {phase for phase in failure_phases if phase in {"setup", "call", "teardown"}}
                ),
                "contributions": [
                    contribution.to_metadata() for contribution in self._contributions
                ],
                "sessions": [
                    session._safe_snapshot()  # pyright: ignore[reportPrivateUsage]
                    for session in self._sessions
                ],
            }
        )

    def write_pytest_teardown_failure(self, failure_phases: Sequence[str]) -> None:
        """Write failure evidence after pytest completes all fixture finalizers."""
        issues = list(self._errors)
        for session in self._sessions:
            issues.extend(session._clean_categories())  # pyright: ignore[reportPrivateUsage]
        issues.append("test_failure")
        self._write_failure_manifest(
            issues,
            None,
            test_failed=True,
            failure_phases=failure_phases,
        )


@final
class _ScenarioManager:
    def __init__(
        self,
        *,
        owner: BrowserScenarioFactory,
        source: Literal["managed", "external"],
        factory: str | None = None,
        config: Mapping[str, object] | None = None,
        root_path: str | None = None,
        base_url: str | None = None,
        base_origin: str | None = None,
        base_path: str = "",
        allowed_origins: Sequence[str] = (),
        synthetic: bool = False,
    ) -> None:
        self._owner: BrowserScenarioFactory = owner
        self._source: Literal["managed", "external"] = source
        self._factory: str | None = factory
        self._config: Mapping[str, object] | None = config
        self._root_path: str | None = root_path
        self._external_url: str | None = base_url
        self._external_origin: str | None = base_origin
        self._external_path: str = base_path
        self._allowed_origins: tuple[str, ...] = tuple(
            dict.fromkeys(
                (
                    *owner._allowed_origins,  # pyright: ignore[reportPrivateUsage]
                    *(validate_origin(o) for o in allowed_origins),
                )
            )
        )
        self._synthetic: bool = synthetic
        if owner._capture_profile == "synthetic" and not (  # pyright: ignore[reportPrivateUsage]
            synthetic and owner._synthetic_data_declared  # pyright: ignore[reportPrivateUsage]
        ):
            raise UIConfigurationError("synthetic capture needs explicit synthetic-data consent")
        self._scenario: BrowserScenario | None = None

    def __enter__(self) -> BrowserScenario:
        if self._scenario is not None:
            raise UIHarnessError("a browser scenario manager may only be entered once")
        host: ManagedASGIHost | None = None
        base_url = self._external_url
        origin = self._external_origin
        if self._source == "managed":
            if self._factory is None:
                raise UIConfigurationError("managed scenario requires an importable app factory")
            host = ManagedASGIHost(
                self._factory,
                config=self._config,
                root_path=self._root_path,
                startup_timeout=self._owner._startup_timeout,  # pyright: ignore[reportPrivateUsage]
                shutdown_timeout=self._owner._shutdown_timeout,  # pyright: ignore[reportPrivateUsage]
            )
            try:
                base_url = host.start()
                origin = host.origin
            except (Exception, KeyboardInterrupt, SystemExit):
                with contextlib.suppress(Exception, KeyboardInterrupt, SystemExit):
                    host.close()
                raise
        if base_url is None or origin is None:
            raise UIConfigurationError("scenario base URL is unavailable")
        scenario: BrowserScenario | None = None
        try:
            context = self._owner._lease_context()  # pyright: ignore[reportPrivateUsage]
            scenario = BrowserScenario(
                owner=self._owner,
                source=self._source,
                host=host,
                context=context,
                base_url=base_url,
                base_origin=origin,
                base_path=(
                    self._external_path if self._source == "external" else urlsplit(base_url).path
                ),
                allowed_origins=self._allowed_origins,
                event_capacity=self._owner._event_capacity,  # pyright: ignore[reportPrivateUsage]
                synthetic=self._synthetic,
            )
            scenario._install_observers()  # pyright: ignore[reportPrivateUsage]
            self._owner._opened(scenario)  # pyright: ignore[reportPrivateUsage]
            self._scenario = scenario
            return scenario
        except (Exception, KeyboardInterrupt, SystemExit) as primary:
            if scenario is not None:
                with contextlib.suppress(Exception, KeyboardInterrupt, SystemExit):
                    scenario.close(primary_error=primary)
            elif host is not None:
                try:
                    host.close()
                except (Exception, KeyboardInterrupt, SystemExit) as cleanup:  # noqa: BLE001
                    primary.add_note(f"Managed ASGI cleanup failed: {_exception_name(cleanup)}")
            raise

    def __exit__(self, exc_type: object, exc: BaseException | None, traceback: object) -> bool:
        del exc_type, traceback
        if self._scenario is None:
            return False
        self._scenario.close(primary_error=exc)
        if exc is None:
            self._scenario.assert_clean()
        return False


@final
class BrowserScenario:
    """One scenario's native Playwright objects, host, and observed facts."""

    def __init__(
        self,
        *,
        owner: BrowserScenarioFactory,
        source: Literal["managed", "external"],
        host: ManagedASGIHost | None,
        context: object,
        base_url: str,
        base_origin: str,
        base_path: str,
        allowed_origins: Sequence[str],
        event_capacity: int,
        synthetic: bool,
    ) -> None:
        self._owner: BrowserScenarioFactory = owner
        self._source: Literal["managed", "external"] = source
        self._host: ManagedASGIHost | None = host
        self._context: BrowserContext = cast("BrowserContext", context)
        parsed_base_url = urlsplit(base_url)
        self._base_url: str = base_url.rstrip("/") + ("/" if parsed_base_url.path else "")
        self._base_origin: str = base_origin
        self._base_path: str = base_path
        self._allowed_origins: frozenset[str] = frozenset((base_origin, *allowed_origins))
        self._event_capacity: int = event_capacity
        # Checkpoints identify this page scenario, not only the pytest fixture
        # that may create several independent scenarios.
        self._session_id: str = uuid.uuid4().hex
        self._binding: str = f"__hedron_ui_{uuid.uuid4().hex}"
        self._events: deque[UIEvent] = deque(maxlen=event_capacity)
        self._categories: deque[str] = deque(maxlen=_ERROR_CAPACITY)
        self._observer_leases = contextlib.ExitStack()
        self._pages: list[Page] = []
        self._requests: dict[int, _Request] = {}
        self._network_sequence: int = 0
        self._event_sequence: int = 0
        self._active_expectations: list[_ExpectedHTTP] = []
        self._navigation_epoch: int = 0
        self._primary_page: Page | None = None
        self._open: bool = True
        self._synthetic: bool = synthetic
        self._capabilities: dict[str, bool | str] = {
            "observer": True,
            "htmx_lifecycle": "unavailable",
            "server_exception_channel": "available" if source == "managed" else "unavailable",
            "service_worker_blocking": True,
            "request_origin_policy": True,
            "websockets": "unsupported; blocked",
            "server_sent_events": "unsupported",
            "streaming_responses": "unsupported; routed responses are buffered",
        }

    @property
    def page(self) -> Page:
        """The primary native Playwright Page used in this scenario."""
        if self._primary_page is None:
            raise UIHarnessError("scenario page is not available")
        return self._primary_page

    @property
    def context(self) -> BrowserContext:
        """The plugin-leased native Playwright BrowserContext."""
        return self._context

    @property
    def url(self) -> str:
        """The literal-loopback application base URL."""
        return self._base_url

    @property
    def is_open(self) -> bool:
        return self._open

    @property
    def events(self) -> tuple[UIEvent, ...]:
        """A bounded, allowlisted snapshot of the Python-observed event ring."""
        return tuple(self._events)

    @property
    def capabilities(self) -> Mapping[str, object]:
        """Facts that the current page/host can actually expose to this test."""
        return dict(self._capabilities)

    def url_for(self, path: object) -> str:
        """Join a local path without allowing a test helper to escape its origin."""
        if not isinstance(path, str) or not path or len(path) > 4096:
            raise ValueError("path must be a non-empty local path")
        parsed = urlsplit(path)
        if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or "\\" in path:
            raise ValueError("path must not contain an origin, query, fragment, or backslash")
        if any(part in {".", ".."} for part in path.split("/")):
            raise ValueError("path must not contain dot segments")
        if path.startswith("/"):
            return f"{self._base_origin}{self._base_path.rstrip('/')}{path}"
        prefix = self._base_path.rstrip("/")
        return f"{self._base_origin}{prefix}/{path}"

    def mark(self, name: str) -> Locator:
        """Return a real Playwright locator for an authored ``data-testid`` mark."""
        self._validate_name(name, "mark")
        return self.page.get_by_test_id(name)

    def region(self, name: str) -> Locator:
        """Return a real strict Playwright locator for an element id region."""
        self._validate_name(name, "region")
        return self.page.locator(f'[id="{name}"]')

    def checkpoint(self) -> Checkpoint:
        """Capture the current page document and event sequence before an action."""
        if self._primary_page is None or not self._open:
            raise UIHarnessError("cannot checkpoint a closed scenario")
        try:
            snapshot_raw = _evaluate(
                self.page,
                """(binding) => {
                  const state = window[binding + "_state"];
                  return state ? {sequence: state.sequence, dropped: state.dropped,
                                  documentId: state.documentId,
                                  htmx: Boolean(window.htmx)} : null;
                }""",
                self._binding,
            )
        except Exception as exc:
            raise ObservationUnavailableError("page lifecycle observer is unavailable") from exc
        snapshot = _mapping_object(snapshot_raw)
        if snapshot is None:
            raise ObservationUnavailableError("page lifecycle observer is unavailable")
        document_id = snapshot.get("documentId")
        sequence = snapshot.get("sequence")
        dropped = snapshot.get("dropped")
        if (
            not isinstance(document_id, str)
            or not isinstance(sequence, int)
            or not isinstance(dropped, int)
        ):
            raise ObservationUnavailableError("page lifecycle observer returned invalid data")
        self._capabilities["htmx_lifecycle"] = (
            "available" if snapshot.get("htmx") else "unavailable"
        )
        return Checkpoint(
            self._session_id,
            self._navigation_epoch,
            sequence,
            document_id,
            dropped,
            self._network_sequence,
        )

    def settle(
        self,
        *,
        since: Checkpoint,
        target: str,
        timeout: float = 10.0,
        generation: int | None = None,
        user_action: bool | None = True,
    ) -> SettleResult:
        """Wait for a matching observed request and its actual terminal/swap facts.

        Call :meth:`checkpoint` immediately before the user action. The browser
        keeps a bounded event ring, so fast requests are still observed even if
        they finish before this method is entered.
        """
        self._validate_checkpoint(since)
        self._validate_name(target, "target")
        timeout = _validate_duration(timeout, "timeout")
        if generation is not None and (type(generation) is not int or generation < 0):
            raise ValueError("generation must be a non-negative integer")
        user_action = _validate_user_action_filter(user_action)
        if self._primary_page is None:
            raise UIHarnessError("scenario page is not available")
        capability = _evaluate(
            self.page,
            """(binding) => Boolean(window[binding + "_state"] && window.htmx)""",
            self._binding,
        )
        if capability is not True:
            self._capabilities["htmx_lifecycle"] = "unavailable"
            raise ObservationUnavailableError(
                "HTMX request lifecycle is unavailable; assert the user-visible "
                + "predicate with Playwright"
            )
        started = time.monotonic()
        settle_arg = {
            "sequence": since.sequence,
            "dropped": since.dropped_count,
            "documentId": since.document_id,
            "target": target,
            "generation": generation,
            "userAction": user_action,
            "networkSequence": since.network_sequence,
        }
        deadline = started + timeout
        wait_error: Exception | None = None
        while True:
            try:
                value = _evaluate(self.page, _settle_expression(self._binding), settle_arg)
                wait_error = None
            except Exception as exc:  # noqa: BLE001 — tolerate transient page evaluation failures.
                value = False
                wait_error = exc
            if value is not False:
                break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                try:
                    diagnostic = _evaluate(
                        self.page,
                        _settle_diagnostic_expression(self._binding),
                        settle_arg,
                    )
                except Exception:  # noqa: BLE001 — Playwright errors vary across supported versions.
                    diagnostic = None
                reason = (
                    diagnostic if isinstance(diagnostic, str) else "matching request did not settle"
                )
                raise SettleTimeoutError(f"{reason} (target={target!r})") from wait_error
            self.page.wait_for_timeout(min(0.025, remaining) * 1000)
        value_mapping = _mapping_object(value)
        if value_mapping is None:
            raise ObservationUnavailableError("settle observer returned invalid lifecycle data")
        unavailable = value_mapping.get("unavailable")
        if isinstance(unavailable, str):
            if unavailable == "ambiguous_matching_requests":
                raise AmbiguousSettleError(
                    "multiple matching user-action requests started after the checkpoint; "
                    + "pass generation=... to identify the intended action"
                )
            raise ObservationUnavailableError(
                f"page lifecycle observation became unavailable ({unavailable.replace('_', ' ')})"
            )
        request_id = value_mapping.get("requestId")
        status = value_mapping.get("status")
        observed_generation = value_mapping.get("generation")
        if not isinstance(request_id, int):
            raise ObservationUnavailableError("settle observer did not identify a request")
        if status is not None and not isinstance(status, int):
            raise ObservationUnavailableError("settle observer returned an invalid status")
        if observed_generation is not None and not isinstance(observed_generation, int):
            observed_generation = None
        cancelled = value_mapping.get("cancelled") is True
        swapped = value_mapping.get("swapped") is True
        settled = value_mapping.get("settled") is True
        self._append_event(
            "settle_complete",
            request_id=request_id,
            status=status,
            target=target,
            generation=observed_generation,
        )
        return SettleResult(
            request_id=request_id,
            target=target,
            generation=observed_generation,
            status=status,
            cancelled=cancelled,
            swapped=swapped,
            settled=settled,
            elapsed_seconds=time.monotonic() - started,
        )

    @contextlib.contextmanager
    def expect_http(
        self,
        *,
        method: object,
        path: object,
        status: object,
        count: object = 1,
        since: Checkpoint | None = None,
    ) -> Generator[None, None, None]:
        """Allow an exact method/path/status count inside this action scope."""
        method = _validate_method(method)
        path = _validate_path(path)
        if type(status) is not int or not 100 <= status <= 599:
            raise ValueError("status must be an HTTP status code")
        if type(count) is not int or not 1 <= count <= 100:
            raise ValueError("count must be between 1 and 100")
        status_code = status
        expected_count = count
        checkpoint = since or self.checkpoint()
        self._validate_checkpoint(checkpoint)
        rule = _ExpectedHTTP(method, path, status_code, expected_count, checkpoint)
        self._active_expectations.append(rule)
        try:
            yield
        finally:
            rule.closed = True
            if rule.observed != rule.count:
                self._record_error("expected_http_count_mismatch")

    def assert_clean(self) -> None:
        """Raise if unexpected errors, requests, server exceptions, or policies remain."""
        categories = self._clean_categories()
        if categories:
            raise CleanCheckError(
                "Hedron UI clean check failed: " + ", ".join(sorted(set(categories)))
            )

    def close(self, *, primary_error: BaseException | None = None) -> None:
        """Close page and child resources while preserving an active test failure."""
        if not self._open:
            return
        self._open = False
        errors: list[BaseException] = []
        try:
            self._collect_host_messages()
            pending = self._page_pending_requests()
            if pending:
                self._record_error("unfinished_hedron_request")
            # Keep routing and observers active while pytest-playwright captures
            # traces and screenshots from the still-live pages.
            try:
                self._context.close()
            except Exception as exc:  # noqa: BLE001 — continue cleanup after observer failure.
                errors.append(exc)
                # pytest-playwright removes the context from its own finalizer
                # list before artifact capture. If capture raises, bypass that
                # wrapper and still close the native Playwright context.
                try:
                    from playwright.sync_api import BrowserContext as PlaywrightBrowserContext

                    PlaywrightBrowserContext.close(self._context)
                except Exception as fallback_exc:  # noqa: BLE001 — retain both cleanup failures.
                    errors.append(fallback_exc)
            # Closing the context disposes the routes and bindings. Do not run
            # their unregister callbacks against an already-closed context.
            _ = self._observer_leases.pop_all()
            for page in self._pages:
                for event, callback in (
                    ("pageerror", self._on_page_error),
                    ("crash", self._on_page_crash),
                    ("console", self._on_console),
                    ("framenavigated", self._on_frame_navigated),
                ):
                    try:
                        page.remove_listener(event, callback)
                    except Exception as exc:  # noqa: BLE001 — continue removing owned listeners.
                        errors.append(exc)
            for event, callback in (
                ("request", self._on_request),
                ("response", self._on_response),
                ("requestfinished", self._on_request_finished),
                ("requestfailed", self._on_request_failed),
                ("page", self._attach_page),
            ):
                try:
                    self._context.remove_listener(event, callback)
                except Exception as exc:  # noqa: BLE001 — continue removing owned listeners.
                    errors.append(exc)
            if self._host is not None:
                try:
                    self._host.close()
                except ManagedHostCleanupError as exc:
                    self._record_error("managed_host_forced_shutdown")
                    errors.append(exc)
                except ManagedHostError as exc:
                    self._record_error("managed_host_shutdown_error")
                    errors.append(exc)
                self._collect_host_messages()
        finally:
            self._active_expectations.clear()
        if errors:
            for error in errors:
                if primary_error is not None:
                    primary_error.add_note(f"Hedron UI cleanup failure: {_exception_name(error)}")
                else:
                    self._record_error(_category_for_exception(error))
            if primary_error is None and errors:
                raise CleanCheckError(
                    "Hedron UI cleanup failed: "
                    + ", ".join(_exception_name(error) for error in errors)
                ) from errors[0]
        if primary_error is not None:
            categories = self._clean_categories()
            if categories:
                primary_error.add_note("Hedron UI observed: " + ", ".join(sorted(set(categories))))

    def _append_event(
        self,
        kind: str,
        *,
        request_id: int | None = None,
        status: int | None = None,
        target: str | None = None,
        generation: int | None = None,
        navigation_epoch: int | None = None,
    ) -> None:
        if len(self._events) == self._event_capacity:
            self._record_error("event_ring_truncated")
        self._event_sequence += 1
        self._events.append(
            UIEvent(
                sequence=self._event_sequence,
                navigation_epoch=(
                    self._navigation_epoch if navigation_epoch is None else navigation_epoch
                ),
                kind=kind,
                request_id=request_id,
                status=status,
                target=target,
                generation=generation,
            )
        )

    def _install_observers(self) -> None:
        callback = cast(Callable[[object, object], None], self._on_lifecycle_event)
        _ = self._observer_leases.enter_context(
            self._context.expose_binding(self._binding, callback)  # pyright: ignore[reportUnknownMemberType]
        )
        _ = self._observer_leases.enter_context(
            self._context.add_init_script(_observer_script(self._binding, self._event_capacity))
        )
        _ = self._observer_leases.enter_context(self._context.route("**/*", self._route_request))
        # WebSocket routes are a separate Playwright channel from HTTP routes.
        # Block them before creating any page so they cannot bypass the origin
        # policy while their behavior remains unsupported by this harness.
        self._context.route_web_socket("**/*", self._block_websocket)
        self._context.on("request", self._on_request)
        self._context.on("response", self._on_response)
        self._context.on("requestfinished", self._on_request_finished)
        self._context.on("requestfailed", self._on_request_failed)
        self._context.on("page", self._attach_page)
        page = self._context.new_page()
        self._primary_page = page
        self._attach_page(page)
        self._capabilities = {
            "observer": True,
            "htmx_lifecycle": "available when the page loads HTMX",
            "server_exception_channel": "available" if self._source == "managed" else "unavailable",
            "service_worker_blocking": True,
            "request_origin_policy": True,
            "websockets": "unsupported; blocked",
            "server_sent_events": "unsupported",
            "streaming_responses": "unsupported; routed responses are buffered",
        }

    def _block_websocket(self, route: WebSocketRoute) -> None:
        self._record_error("websocket_unsupported")
        try:
            route.close(code=1008, reason="WebSockets are unsupported in Hedron UI scenarios")
        except Exception:  # noqa: BLE001 — report a routing failure if teardown races.
            self._record_error("request_policy_failure")

    def _attach_page(self, page: Page) -> None:
        if page in self._pages:
            return
        self._pages.append(page)
        page.on("pageerror", self._on_page_error)
        page.on("crash", self._on_page_crash)
        page.on("console", self._on_console)
        page.on("framenavigated", self._on_frame_navigated)

    def _on_lifecycle_event(self, source: object, payload: object) -> None:
        del source
        payload_mapping = _mapping_object(payload)
        if payload_mapping is None:
            self._record_error("invalid_lifecycle_event")
            return
        kind = payload_mapping.get("kind")
        if kind not in {
            "request_start",
            "request_done",
            "request_error",
            "transport_error",
            "request_abort",
            "swap_decision",
            "swap",
            "settle",
        }:
            self._record_error("invalid_lifecycle_event")
            return
        request_id = payload_mapping.get("requestId")
        status = payload_mapping.get("status")
        target = payload_mapping.get("target")
        generation = payload_mapping.get("generation")
        self._append_event(
            cast(str, kind),
            request_id=request_id if isinstance(request_id, int) else None,
            status=status if isinstance(status, int) else None,
            target=target if isinstance(target, str) and _TARGET_RE.fullmatch(target) else None,
            generation=generation if isinstance(generation, int) and generation >= 0 else None,
        )

    def _route_request(self, route: Route) -> None:
        request = route.request
        url = _string_attr(request, "url")
        origin = _origin_from_url(url)
        if origin is None or origin not in self._allowed_origins:
            self._record_error("blocked_external_request")
            try:
                route.abort("blockedbyclient")
            except Exception:  # noqa: BLE001 — route failure is recorded as a policy failure.
                self._record_error("request_policy_failure")
            return
        try:
            accept = request.header_value("accept") or ""
        except Exception:  # noqa: BLE001 — request metadata varies by Playwright version.
            accept = ""
        if "text/event-stream" in accept.lower():
            self._record_error("streaming_response_unsupported")
            try:
                route.abort("blockedbyclient")
            except Exception:  # noqa: BLE001 — fail the request even if routing teardown races.
                self._record_error("request_policy_failure")
            return
        response = None
        try:
            # Playwright does not invoke route handlers for redirect hops.
            # Fetch only the first response so Location cannot bypass the
            # allowlist without another policy check.
            response = route.fetch(max_redirects=0)
            status = _int_attr(response, "status")
            if status is not None and 300 <= status < 400:
                self._record_error("redirect_blocked")
                route.abort("blockedbyclient")
                return
            route.fulfill(response=response)
        except Exception:  # noqa: BLE001 — route failure is recorded as a policy failure.
            self._record_error("request_policy_failure")
            with contextlib.suppress(Exception):
                route.abort("blockedbyclient")
        finally:
            if response is not None:
                with contextlib.suppress(Exception):
                    response.dispose()

    def _on_request(self, request_obj: object) -> None:
        url = _string_attr(request_obj, "url")
        method = _safe_method(_string_attr(request_obj, "method"))
        resource = _safe_resource(_string_attr(request_obj, "resource_type"))
        self._network_sequence += 1
        if len(self._requests) >= 512:
            self._record_error("active_request_limit_exceeded")
            return
        self._requests[id(request_obj)] = _Request(
            method=method,
            path=urlsplit(url).path,
            origin=_origin_from_url(url) or "unavailable",
            resource_type=resource,
            epoch=self._navigation_epoch,
            sequence=self._network_sequence,
        )
        self._append_event("network_request", navigation_epoch=self._navigation_epoch)

    def _on_response(self, response_obj: object) -> None:
        request_obj = _attr(response_obj, "request")
        request = self._requests.get(id(request_obj))
        status = _int_attr(response_obj, "status")
        if request is None or status is None:
            self._record_error("unmatched_response_event")
            return
        request.status = status
        expected = self._match_expected(request, status)
        if status >= 400 and not expected:
            self._record_error("unexpected_http_error")
        self._append_event("http_response", status=status, navigation_epoch=request.epoch)

    def _on_request_finished(self, request_obj: object) -> None:
        request = self._requests.pop(id(request_obj), None)
        if request is not None:
            request.finished = True

    def _on_request_failed(self, request_obj: object) -> None:
        request = self._requests.pop(id(request_obj), None)
        if request is None:
            self._record_error("unmatched_request_failure")
            return
        request.failed = True
        failure = _string_attr(request_obj, "failure")
        if "ERR_ABORTED" in failure:
            self._append_event("network_abort", navigation_epoch=request.epoch)
            return
        if request.resource_type in {"script", "stylesheet", "font"}:
            self._record_error("required_resource_failure")
        else:
            self._record_error("request_failed")

    def _on_page_error(self, error: object) -> None:
        del error
        self._record_error("page_error")

    def _on_page_crash(self, *args: object) -> None:
        del args
        self._record_error("page_crash")

    def _on_console(self, message: ConsoleMessage) -> None:
        if _string_attr(message, "type") == "error":
            if self._is_expected_http_console(message):
                self._append_event("expected_http_console")
                return
            self._record_error("console_error")

    def _is_expected_http_console(self, message: object) -> bool:
        """Allow only the browser/HTMX status lines caused by an active exact rule."""
        text = _string_attr(message, "text")
        location = _mapping_object(_attr(message, "location"))
        if location is None:
            return False
        source_url = location.get("url")
        if (
            not isinstance(source_url, str)
            or _origin_from_url(source_url) not in self._allowed_origins
        ):
            return False
        source_path = urlsplit(source_url).path

        resource_match = re.fullmatch(r"Failed to load resource: .*?\b(\d{3})\b(?:[^0-9].*)?", text)
        htmx_match = re.fullmatch(
            r"Response Status Error Code (\d{3}) from ([^,\s]+), \[object HTML[A-Za-z]*Element\]",
            text,
        )
        status_match = resource_match or htmx_match
        if status_match is None:
            return False
        try:
            status = int(status_match.group(1))
        except ValueError:
            return False
        if status < 400:
            return False
        htmx_status_line = htmx_match is not None
        reported_path = urlsplit(htmx_match.group(2)).path if htmx_match else source_path
        if htmx_status_line and not source_path.endswith("/hedron-static/htmx.min.js"):
            return False

        for expectation in reversed(self._active_expectations):
            if (
                expectation.closed
                or expectation.observed <= 0
                or expectation.status != status
                or expectation.path != reported_path
            ):
                continue
            if htmx_status_line:
                if expectation.htmx_console_observed:
                    continue
                expectation.htmx_console_observed = True
            else:
                if expectation.resource_console_observed:
                    continue
                expectation.resource_console_observed = True
            return True
        return False

    def _on_frame_navigated(self, frame: Frame) -> None:
        if self._primary_page is None:
            return
        try:
            if frame == self._primary_page.main_frame:
                self._navigation_epoch += 1
                self._append_event("navigation", navigation_epoch=self._navigation_epoch)
        except Exception:  # noqa: BLE001 — callbacks must not throw into Playwright dispatch.
            self._record_error("navigation_observer_failure")

    def _match_expected(self, request: _Request, status: int) -> bool:
        for expectation in self._active_expectations:
            if expectation.closed or expectation.observed >= expectation.count:
                continue
            if expectation.checkpoint.navigation_epoch != request.epoch:
                continue
            if request.sequence <= expectation.checkpoint.network_sequence:
                continue
            if (
                expectation.method == request.method
                and expectation.path == request.path
                and expectation.status == status
            ):
                expectation.observed += 1
                self._append_event("expected_http", status=status, navigation_epoch=request.epoch)
                return True
        return False

    def _validate_checkpoint(self, checkpoint: Checkpoint) -> None:
        if type(checkpoint) is not Checkpoint or checkpoint.session_id != self._session_id:
            raise InvalidCheckpointError("checkpoint belongs to a different browser scenario")
        if checkpoint.navigation_epoch != self._navigation_epoch:
            raise InvalidCheckpointError("checkpoint belongs to an earlier page navigation")

    def _page_pending_requests(self) -> tuple[int, ...]:
        try:
            pending = _evaluate(
                self.page,
                """(binding) => {
              const state = window[binding + "_state"];
              if (!state) return [];
              const open = new Set();
              for (const event of state.events) {
                if (event.kind === "request_start") open.add(event.requestId);
                if (["request_done", "request_error", "request_abort"].includes(event.kind)) {
                  open.delete(event.requestId);
                }
              }
              return [...open].slice(0, 64);
            }""",
                self._binding,
            )
        except Exception:  # noqa: BLE001 — preserve cleanup if the page is already gone.
            self._record_error("lifecycle_observer_unavailable")
            return ()
        if not isinstance(pending, list):
            return ()
        pending_values = cast(list[object], pending)
        return tuple(value for value in pending_values if isinstance(value, int))

    def _collect_host_messages(self) -> None:
        if self._host is None:
            return
        for message in self._host.drain_messages():
            kind = message.get("kind")
            if kind == "server_exception":
                self._record_error("managed_server_exception")
            elif kind == "lifespan_shutdown_failed":
                self._record_error("managed_lifespan_shutdown_failed")

    def _record_error(self, category: str) -> None:
        safe = category if re.fullmatch(r"[a-z][a-z0-9_]{0,63}", category) else "harness_error"
        if safe not in self._categories:
            self._categories.append(safe)
        self._owner._record_error(safe)  # pyright: ignore[reportPrivateUsage]

    def _clean_categories(self) -> tuple[str, ...]:
        self._collect_host_messages()
        pending = [
            request
            for request in self._requests.values()
            if not request.finished and not request.failed
        ]
        if pending:
            self._record_error("unfinished_network_request")
        for expectation in self._active_expectations:
            if expectation.closed and expectation.observed != expectation.count:
                self._record_error("expected_http_count_mismatch")
        return tuple(self._categories)

    def _safe_snapshot(self) -> dict[str, object]:
        events = tuple(self._events)
        retained_events = events[-_MANIFEST_EVENT_LIMIT:]
        return {
            "source": self._source,
            "server_exception_channel": "available" if self._source == "managed" else "unavailable",
            "navigation_epoch": self._navigation_epoch,
            "event_count": len(self._events),
            "event_capacity": self._event_capacity,
            "events_truncated": "event_ring_truncated" in self._categories,
            "manifest_events_truncated": len(retained_events) < len(events),
            "error_categories": sorted(set(self._categories)),
            "origin_policy": "exact_loopback_allowlist",
            "browser": self._browser_provenance(),
            "capabilities": dict(self._capabilities),
            "capture_profile": self._owner._capture_profile,  # pyright: ignore[reportPrivateUsage]
            "capture_label": (
                "unredacted"
                if self._synthetic and self._owner._capture_profile == "synthetic"  # pyright: ignore[reportPrivateUsage]
                else None
            ),
            # Region ids can be application data. Keep them available to the
            # running test, but omit them from the default persisted manifest.
            "events": [
                {
                    "sequence": event.sequence,
                    "navigation_epoch": event.navigation_epoch,
                    "kind": event.kind,
                    "request_id": event.request_id,
                    "status": event.status,
                    "generation": event.generation,
                }
                for event in retained_events
            ],
        }

    def _browser_provenance(self) -> dict[str, str]:
        browser = self._context.browser
        if browser is None:
            return {"engine": "unavailable", "version": "unavailable"}
        engine = browser.browser_type.name
        version = browser.version
        if engine not in {"chromium", "firefox", "webkit"}:
            engine = "unavailable"
        if not re.fullmatch(r"[A-Za-z0-9.+_-]{1,64}", version):
            version = "unavailable"
        return {"engine": engine, "version": version}

    @staticmethod
    def _validate_name(name: object, label: str) -> None:
        if not isinstance(name, str) or not _TARGET_RE.fullmatch(name):
            raise ValueError(f"{label} must be a short, stable identifier")


def _observer_script(binding: str, capacity: int) -> str:
    if not _BINDING_RE.fullmatch(binding):
        raise ValueError("invalid private browser observer binding")
    return f"""
(() => {{
  const binding = "{binding}";
  const capacity = {capacity};
  const stateName = binding + "_state";
  const documentId = (() => {{
    try {{
      const cryptoApi = globalThis.crypto;
      if (cryptoApi && typeof cryptoApi.randomUUID === "function") return cryptoApi.randomUUID();
      const words = new Uint32Array(4);
      if (cryptoApi && typeof cryptoApi.getRandomValues === "function") {{
        cryptoApi.getRandomValues(words);
      }} else {{
        for (let i = 0; i < words.length; i++) {{
          words[i] = Math.floor(Math.random() * 0x100000000);
        }}
      }}
      return Date.now().toString(36) + "-" +
        Array.from(words, word => word.toString(16).padStart(8, "0")).join("");
    }} catch (_) {{
      return Date.now().toString(36) + "-" + Math.random().toString(36).slice(2);
    }}
  }})();
  const state = {{documentId, sequence: 0, requestSequence: 0, events: []}};
  state.dropped = 0;
  const requestIds = new WeakMap();
  const safeId = (value) => typeof value === "string" &&
    /^[A-Za-z][A-Za-z0-9_.:-]{{0,79}}$/.test(value) ? value : null;
  const safeGeneration = (value) => {{
    const number = Number(value);
    return Number.isInteger(number) && number >= 0 && number <= 1000000000 ? number : null;
  }};
  const targetId = (value) => {{
    if (value instanceof Element) return safeId(value.id);
    if (typeof value === "string" &&
        /^#[A-Za-z][A-Za-z0-9_.:-]{{0,79}}$/.test(value)) return value.slice(1);
    return null;
  }};
  const emit = (kind, event) => {{
    const detail = event && event.detail && typeof event.detail === "object" ? event.detail : {{}};
    const xhr = detail.xhr;
    let requestId = null;
    if (xhr && typeof xhr === "object") {{
      requestId = requestIds.get(xhr);
      if (!requestId && kind === "request_start") {{
        requestId = ++state.requestSequence;
        requestIds.set(xhr, requestId);
      }}
    }}
    const source = detail.requestConfig?.elt || detail.elt || event?.target;
    const triggeringEvent = detail.requestConfig?.triggeringEvent || detail.triggeringEvent;
    const marked = source instanceof Element
      ? source.closest("[data-hedron-action-generation]") : null;
    const payload = {{
      sequence: ++state.sequence,
      documentId: state.documentId,
      kind,
      requestId,
      status: xhr && Number.isInteger(xhr.status) ? xhr.status : null,
      target: targetId(detail.target) || targetId(source?.getAttribute?.("hx-target")) ||
        targetId(source?.getAttribute?.("data-hx-target")),
      generation: marked
        ? safeGeneration(marked.getAttribute("data-hedron-action-generation")) : null,
      userAction: triggeringEvent?.isTrusted === true,
    shouldSwap: kind === "swap_decision" ? detail.shouldSwap === true : null,
    }};
    state.events.push(payload);
    if (state.events.length > capacity) {{ state.events.shift(); state.dropped += 1; }}
    const notify = window[binding];
    if (typeof notify === "function") Promise.resolve(notify(payload)).catch(() => {{}});
  }};
  const events = {{
    "htmx:beforeRequest": "request_start",
    "htmx:afterRequest": "request_done",
    "htmx:responseError": "request_error",
    "htmx:sendError": "transport_error",
    "htmx:timeout": "transport_error",
    "htmx:sendAbort": "request_abort",
    "htmx:beforeSwap": "swap_decision",
    "htmx:afterSwap": "swap",
    "htmx:afterSettle": "settle",
  }};
  for (const [name, kind] of Object.entries(events)) {{
    document.addEventListener(name, (event) => {{
      if (kind === "swap_decision") queueMicrotask(() => emit(kind, event));
      else emit(kind, event);
    }});
  }}
  Object.defineProperty(window, stateName, {{value: state, configurable: false, writable: false}});
}})();
"""


def _settle_expression(binding: str) -> str:
    return f"""(cursor) => {{
      const state = window["{binding}_state"];
      if (!state || state.documentId !== cursor.documentId || !window.htmx) return false;
      if (state.dropped > cursor.dropped) return {{unavailable: "event_buffer_truncated"}};
      const matchTarget = (value) => value === cursor.target;
      const events = state.events.filter((event) => event.sequence > cursor.sequence);
      const starts = events.filter((event) => event.kind === "request_start" &&
        matchTarget(event.target) &&
        (cursor.generation === null || event.generation === cursor.generation) &&
        (cursor.userAction === null || event.userAction === cursor.userAction));
      if (!starts.length) return false;
      if (starts.length > 1) return {{unavailable: "ambiguous_matching_requests"}};
      // Polls and other non-user-triggered requests are excluded by default.
      // A generation further scopes overlapping user actions that share a target.
      const start = starts[0];
      const terminals = events.filter((event) => event.requestId === start.requestId &&
        ["request_done", "request_error", "transport_error", "request_abort"].includes(event.kind));
      const terminal = terminals[terminals.length - 1];
      if (!terminal) return false;
      const cancelled = terminals.some((event) => event.kind === "request_abort");
      const requestError = terminals.some((event) =>
        ["request_error", "transport_error"].includes(event.kind));
      const transportError = terminals.some((event) => event.kind === "transport_error");
      const status = terminal.status;
      const swap = events.some((event) => event.requestId === start.requestId &&
        event.kind === "swap" && matchTarget(event.target));
      const requestFinished = terminals.some((event) => event.kind === "request_done");
      const swapDecision = events.find((event) => event.requestId === start.requestId &&
        event.kind === "swap_decision");
      const noSwap = cancelled || status === 204 ||
        (transportError && requestFinished) ||
        (requestError && requestFinished && swapDecision && swapDecision.shouldSwap === false);
      const settled = events.some((event) => event.requestId === start.requestId &&
        event.kind === "settle" && matchTarget(event.target));
      if (!noSwap && !settled) return false;
      return {{
        requestId: start.requestId, status, cancelled, swapped: swap, settled,
        generation: start.generation, requestError}};
    }}"""


def _settle_diagnostic_expression(binding: str) -> str:
    return f"""(cursor) => {{
      const state = window["{binding}_state"];
      if (!state) return "page lifecycle observer unavailable";
      if (state.documentId !== cursor.documentId) return "checkpoint invalidated by navigation";
      if (!window.htmx) return "HTMX lifecycle capability unavailable";
      if (state.dropped > cursor.dropped) return "browser lifecycle event buffer was truncated";
      const starts = state.events.filter((event) => event.sequence > cursor.sequence &&
        event.kind === "request_start" && event.target === cursor.target &&
        (cursor.generation === null || event.generation === cursor.generation) &&
        (cursor.userAction === null || event.userAction === cursor.userAction));
      if (starts.length > 1) {{
        return "multiple matching user-action requests started; pass generation to disambiguate";
      }}
      return starts.length ? "matching request started but did not reach a terminal settle phase" :
        "no matching request start observed after checkpoint";
    }}"""


def _origin_from_url(url: str) -> str | None:
    try:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https", "ws", "wss"} or not parsed.hostname:
            return None
        port = parsed.port
        scheme = {"ws": "http", "wss": "https"}.get(parsed.scheme, parsed.scheme)
        suffix = f":{port}" if port is not None else ""
        hostname = f"[{parsed.hostname}]" if ":" in parsed.hostname else parsed.hostname
        return validate_origin(f"{scheme}://{hostname}{suffix}")
    except ValueError:
        return None


def _validate_duration(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a finite positive number")
    result = float(value)
    if not 0.05 <= result <= 300:
        raise ValueError(f"{name} must be between 0.05 and 300 seconds")
    return result


def _validate_user_action_filter(value: object) -> bool | None:
    if value is None:
        return None
    if type(value) is not bool:
        raise TypeError("user_action must be a boolean or None")
    return value


def _validate_method(method: object) -> str:
    if not isinstance(method, str) or not re.fullmatch(r"[A-Za-z]{1,16}", method):
        raise ValueError("method must be an HTTP token")
    return method.upper()


def _validate_path(path: object) -> str:
    if not isinstance(path, str) or not path.startswith("/") or len(path) > 2048:
        raise ValueError("path must be an exact absolute HTTP path")
    if (
        "?" in path
        or "#" in path
        or "\\" in path
        or any(part in {".", ".."} for part in path.split("/"))
    ):
        raise ValueError("path must not contain a query, fragment, backslash, or dot segment")
    return path


def _safe_method(value: str) -> str:
    return value.upper() if re.fullmatch(r"[A-Za-z]{1,16}", value) else "OTHER"


def _safe_resource(value: str) -> str:
    known = {"document", "stylesheet", "image", "media", "font", "script", "xhr", "fetch"}
    return value if value in known else "other"


def _string_attr(value: object, name: str) -> str:
    attribute: object = getattr(value, name, None)
    return attribute if isinstance(attribute, str) else ""


def _int_attr(value: object, name: str) -> int | None:
    attribute: object = getattr(value, name, None)
    return attribute if isinstance(attribute, int) and not isinstance(attribute, bool) else None


def _attr(value: object, name: str) -> object:
    attribute: object = getattr(value, name, None)
    if callable(attribute):
        result: object = attribute()
        return result
    return attribute


def _mapping_object(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return cast(dict[str, object], value)


def _evaluate(page: Page, expression: str, argument: object) -> object:
    return cast(object, page.evaluate(expression, argument))


def _exception_name(error: BaseException | None) -> str:
    if error is None:
        return ""
    name = type(error).__name__
    return name if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]{0,63}", name) else "Exception"


def _category_for_exception(error: BaseException) -> str:
    if isinstance(error, ManagedHostCleanupError):
        return "managed_host_forced_shutdown"
    return "cleanup_error"
