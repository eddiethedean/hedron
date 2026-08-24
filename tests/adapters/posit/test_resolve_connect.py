"""Posit product resolver and Connect fail-closed cookie mode."""

from __future__ import annotations

import pytest
from starlette.requests import Request

from hedron_core.diagnostics import HedronError
from hedron_posit import (
    ConnectConfig,
    ConnectCookieMode,
    HedronPosit,
    PositConfig,
    PositProduct,
    resolve_posit_deployment,
    resolve_product,
)
from hedron_posit.connect import native_connect_base_from_request
from hedron_posit.cookies import require_supported_cookie_mode


def test_resolve_inactive_by_default() -> None:
    product, evidence = resolve_product(environ={})
    assert product is PositProduct.INACTIVE
    assert evidence == "none"


def test_resolve_connect_from_posit_product() -> None:
    product, evidence = resolve_product(environ={"POSIT_PRODUCT": "CONNECT"})
    assert product is PositProduct.CONNECT
    assert evidence == "posit_product"


def test_resolve_connect_deprecated_marker() -> None:
    product, evidence = resolve_product(environ={"RSTUDIO_PRODUCT": "CONNECT"})
    assert product is PositProduct.CONNECT
    assert evidence == "rstudio_product_compat"


def test_resolve_workbench_from_rs_server_url() -> None:
    product, evidence = resolve_product(environ={"RS_SERVER_URL": "https://wb.example/s/x/"})
    assert product is PositProduct.WORKBENCH
    assert evidence == "workbench_env"


def test_conflict_connect_and_workbench() -> None:
    with pytest.raises(HedronError) as exc:
        resolve_product(
            environ={
                "POSIT_PRODUCT": "CONNECT",
                "RS_SERVER_URL": "https://wb.example/s/x/",
            }
        )
    assert "HED-POSIT-0101" in str(exc.value)


def test_explicit_inactive_conflicts_with_connect() -> None:
    with pytest.raises(HedronError):
        resolve_product(
            explicit=PositProduct.INACTIVE,
            environ={"POSIT_PRODUCT": "CONNECT"},
        )


def test_bridge_mode_fails_closed_at_resolve() -> None:
    with pytest.raises(HedronError) as exc:
        resolve_posit_deployment(
            PositConfig(
                connect=ConnectConfig(cookie_mode=ConnectCookieMode.AUTHENTICATED_HEADER_V1)
            )
        )
    assert "HED-POSIT-0401" in str(exc.value)


def test_bridge_mode_fails_closed_helper() -> None:
    with pytest.raises(HedronError) as exc:
        require_supported_cookie_mode(ConnectCookieMode.AUTHENTICATED_HEADER_V1)
    assert "HED-POSIT-0401" in str(exc.value)


def test_hedron_posit_rejects_bridge_at_construction() -> None:
    with pytest.raises(HedronError):
        HedronPosit(
            session_secret="test-secret-not-for-production",
            posit=PositConfig(
                connect=ConnectConfig(cookie_mode=ConnectCookieMode.AUTHENTICATED_HEADER_V1)
            ),
        )


def test_posit_status_inactive() -> None:
    app = HedronPosit(session_secret="test-secret-not-for-production")
    status = app.posit_status()
    assert status.product is PositProduct.INACTIVE
    assert status.bridge_enabled is False
    assert status.cookie_strategy == "native"
    assert status.normalizer_count == 1
    assert "product" in status.as_dict()


def _request(
    *,
    headers: list[tuple[bytes, bytes]],
    root_path: str,
    client: str = "127.0.0.1",
) -> Request:
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "root_path": root_path,
        "headers": headers,
        "client": (client, 12345),
        "server": ("test", 80),
    }
    return Request(scope)


def test_duplicate_connect_base_header_fails() -> None:
    mount = "/content/00000000-0000-4000-8000-000000000001"
    base = f"https://connect.example{mount}"
    req = _request(
        headers=[
            (b"rstudio-connect-app-base-url", base.encode()),
            (b"rstudio-connect-app-base-url", base.encode()),
        ],
        root_path=mount,
    )
    with pytest.raises(HedronError) as exc:
        native_connect_base_from_request(
            req,
            product=PositProduct.CONNECT,
            environ={"POSIT_PRODUCT": "CONNECT"},
        )
    assert "HED-POSIT-0303" in str(exc.value)


def test_connect_base_root_mismatch_fails() -> None:
    mount = "/content/00000000-0000-4000-8000-000000000001"
    req = _request(
        headers=[
            (
                b"rstudio-connect-app-base-url",
                f"https://connect.example{mount}".encode(),
            )
        ],
        root_path="/content/other",
    )
    with pytest.raises(HedronError) as exc:
        native_connect_base_from_request(
            req,
            product=PositProduct.CONNECT,
            environ={"POSIT_PRODUCT": "CONNECT"},
        )
    assert "HED-POSIT-0304" in str(exc.value)


def test_native_connect_accepts_matching_base(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POSIT_PRODUCT", "CONNECT")
    mount = "/content/00000000-0000-4000-8000-000000000001"
    req = _request(
        headers=[
            (
                b"rstudio-connect-app-base-url",
                f"https://connect.example{mount}".encode(),
            )
        ],
        root_path=mount,
    )
    base = native_connect_base_from_request(
        req,
        product=PositProduct.CONNECT,
        environ={"POSIT_PRODUCT": "CONNECT"},
    )
    assert base is not None
    assert base.mount == mount


def test_native_connect_uses_supplied_runtime_environment() -> None:
    mount = "/content/00000000-0000-4000-8000-000000000001"
    req = _request(
        headers=[
            (
                b"rstudio-connect-app-base-url",
                f"https://connect.example{mount}".encode(),
            )
        ],
        root_path=mount,
        client="203.0.113.8",
    )
    base = native_connect_base_from_request(
        req,
        product=PositProduct.CONNECT,
        trusted_peers=("127.0.0.1",),
        environ={"POSIT_PRODUCT": "CONNECT"},
    )
    assert base is not None
    assert base.mount == mount
