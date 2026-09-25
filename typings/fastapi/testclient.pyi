from collections.abc import Mapping, Sequence

from httpx import Response
from starlette.types import ASGIApp


class TestClient:
    def __init__(
        self,
        app: ASGIApp,
        *,
        base_url: str = ...,
        raise_server_exceptions: bool = ...,
        root_path: str = ...,
        backend: str = ...,
        backend_options: Mapping[str, object] | None = ...,
        follow_redirects: bool = ...,
        cookies: object | None = ...,
        headers: Mapping[str, str] | None = ...,
    ) -> None: ...

    def __enter__(self) -> TestClient: ...

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None: ...

    def get(
        self,
        url: str,
        *,
        params: Mapping[str, object] | None = ...,
        headers: Mapping[str, str] | None = ...,
        cookies: Mapping[str, str] | None = ...,
        follow_redirects: bool | None = ...,
        **kwargs: object,
    ) -> Response: ...

    def post(
        self,
        url: str,
        *,
        content: bytes | str | None = ...,
        data: Mapping[str, str] | Sequence[tuple[str, str]] | None = ...,
        files: object | None = ...,
        json: object | None = ...,
        params: Mapping[str, object] | None = ...,
        headers: Mapping[str, str] | None = ...,
        cookies: Mapping[str, str] | None = ...,
        follow_redirects: bool | None = ...,
        **kwargs: object,
    ) -> Response: ...
