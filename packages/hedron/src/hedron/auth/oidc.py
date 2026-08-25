"""OIDC conveniences over Authlib without owning identity or sessions.

Host sessions remain authoritative. Hedron does not create an identity database,
infer authorization, or act as an IdP. These helpers cover PKCE/state/nonce,
claim normalization, Explorer-safe redaction, and Authlib-backed URL builders.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
from collections.abc import Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field
from typing import Any, TypedDict
from urllib.parse import urljoin, urlparse

from hedron.auth.oauth import require_authlib
from hedron_core.csrf import redact_secret_like, tokens_match
from hedron_core.htmx_contract import is_local_path

__all__ = [
    "OidcClientConfig",
    "OidcPkcePair",
    "OidcUserClaims",
    "OidcUserClaimsDict",
    "generate_nonce",
    "generate_pkce",
    "generate_state",
    "login_url",
    "logout_url",
    "normalize_claims",
    "redact_claims",
    "store_oidc_handshake",
    "validate_callback_nonce",
    "validate_callback_state",
]

_OIDC_HANDSHAKE_KEY = "hedron_oidc_handshake"
_RESERVED_OIDC_PARAM_KEYS = frozenset(
    {
        "response_type",
        "client_id",
        "redirect_uri",
        "scope",
        "state",
        "nonce",
        "code_challenge",
        "code_challenge_method",
        "id_token_hint",
        "post_logout_redirect_uri",
    }
)
_CLAIM_REDACT_KEYS = frozenset(
    {
        "password",
        "secret",
        "token",
        "access_token",
        "refresh_token",
        "id_token",
        "api_key",
        "authorization",
        "cookie",
        "session",
        "client_secret",
        "code_verifier",
    }
)


class OidcUserClaimsDict(TypedDict, total=False):
    sub: str
    email: str | None
    name: str | None
    raw: dict[str, Any]


@dataclass(frozen=True, slots=True)
class OidcClientConfig:
    """Application-owned OIDC client settings (no Hedron identity store)."""

    issuer: str
    client_id: str
    redirect_uri: str
    client_secret: str | None = None
    scopes: tuple[str, ...] = ("openid", "profile", "email")
    authorize_url: str | None = None
    end_session_url: str | None = None

    def __post_init__(self) -> None:
        if not self.issuer.strip():
            raise ValueError("issuer must be a non-empty string")
        if not self.client_id.strip():
            raise ValueError("client_id must be a non-empty string")
        if not self.redirect_uri.strip():
            raise ValueError("redirect_uri must be a non-empty string")

    def resolved_authorize_url(self) -> str:
        if self.authorize_url:
            return self.authorize_url
        base = self.issuer if self.issuer.endswith("/") else f"{self.issuer}/"
        return urljoin(base, "authorize")

    def resolved_end_session_url(self) -> str:
        if self.end_session_url:
            return self.end_session_url
        base = self.issuer if self.issuer.endswith("/") else f"{self.issuer}/"
        return urljoin(base, "logout")


@dataclass(frozen=True, slots=True)
class OidcPkcePair:
    verifier: str
    challenge: str
    method: str = "S256"


@dataclass(frozen=True, slots=True)
class OidcUserClaims:
    sub: str
    email: str | None = None
    name: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> OidcUserClaimsDict:
        return {
            "sub": self.sub,
            "email": self.email,
            "name": self.name,
            "raw": dict(self.raw),
        }


def generate_state(*, nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)


def generate_nonce(*, nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)


def generate_pkce(*, nbytes: int = 64) -> OidcPkcePair:
    """Generate a PKCE verifier/challenge pair (S256)."""
    verifier = secrets.token_urlsafe(nbytes)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return OidcPkcePair(verifier=verifier, challenge=challenge, method="S256")


def validate_callback_state(*, expected: str, received: str | None) -> None:
    if not expected or not received or not tokens_match(expected, received):
        raise ValueError("OIDC callback state mismatch")


def validate_callback_nonce(*, expected: str, received: str | None) -> None:
    if not expected or not received or not tokens_match(expected, received):
        raise ValueError("OIDC callback nonce mismatch")


def _reject_reserved_extra_params(extra_params: Mapping[str, str]) -> None:
    for key in extra_params:
        if str(key).lower() in _RESERVED_OIDC_PARAM_KEYS:
            raise ValueError(f"OIDC extra_params must not include protocol field {key!r}")


def _validate_post_logout_redirect_uri(uri: str, config: OidcClientConfig) -> None:
    if is_local_path(uri):
        return
    parsed = urlparse(uri)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Invalid post_logout_redirect_uri")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("post_logout_redirect_uri must not contain credentials")
    registered = urlparse(config.redirect_uri)
    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("Invalid post_logout_redirect_uri")
    if parsed.scheme.lower() != (registered.scheme or "").lower():
        raise ValueError("post_logout_redirect_uri scheme must match redirect_uri")
    if parsed.netloc.lower() != registered.netloc.lower():
        raise ValueError("post_logout_redirect_uri host must match redirect_uri")


def store_oidc_handshake(
    session: MutableMapping[str, Any],
    *,
    state: str,
    nonce: str | None = None,
    code_verifier: str | None = None,
) -> None:
    """Persist handshake secrets on the host session (not an identity DB).

    Partial updates merge into any existing handshake so callers can set
    ``state`` / ``nonce`` / ``code_verifier`` across steps without dropping
    previously stored fields (#152).
    """
    existing = session.get(_OIDC_HANDSHAKE_KEY)
    payload: dict[str, str] = {}
    if isinstance(existing, Mapping):
        for key, value in existing.items():
            if isinstance(key, str) and isinstance(value, str):
                payload[key] = value
    payload["state"] = state
    if nonce is not None:
        payload["nonce"] = nonce
    if code_verifier is not None:
        payload["code_verifier"] = code_verifier
    session[_OIDC_HANDSHAKE_KEY] = payload


def normalize_claims(claims: Mapping[str, Any]) -> OidcUserClaims:
    sub = claims.get("sub")
    if not isinstance(sub, str) or not sub.strip():
        raise ValueError("OIDC claims require a non-empty string sub")
    email = claims.get("email")
    name = claims.get("name")
    return OidcUserClaims(
        sub=sub,
        email=email if isinstance(email, str) else None,
        name=name if isinstance(name, str) else None,
        raw=dict(claims),
    )


def _mask_email(email: str) -> str:
    if "@" not in email:
        return "[redacted]"
    local, _, domain = email.partition("@")
    if not local:
        return f"[redacted]@{domain}"
    return f"{local[0]}***@{domain}"


def redact_claims(claims: OidcUserClaims | Mapping[str, Any]) -> dict[str, Any]:
    """Explorer-safe claim view: keep sub, mask email, scrub token-like raw keys."""
    if isinstance(claims, OidcUserClaims):
        data = claims.as_dict()
    else:
        raw_candidate = claims.get("raw", claims)
        raw = dict(raw_candidate) if isinstance(raw_candidate, Mapping) else {}
        data = {
            "sub": claims.get("sub"),
            "email": claims.get("email"),
            "name": claims.get("name"),
            "raw": raw,
        }
    email = data.get("email")
    raw = data.get("raw") if isinstance(data.get("raw"), dict) else {}
    return {
        "sub": data.get("sub"),
        "email": _mask_email(email) if isinstance(email, str) else None,
        "name": data.get("name"),
        "raw": redact_secret_like(raw, keys=_CLAIM_REDACT_KEYS),
    }


def login_url(
    config: OidcClientConfig,
    *,
    state: str,
    nonce: str | None = None,
    code_challenge: str | None = None,
    code_challenge_method: str = "S256",
    extra_params: Mapping[str, str] | None = None,
) -> str:
    """Build an OIDC authorization URL via Authlib URL helpers.

    Raises ``HED-AUTH-0001`` when Authlib is not installed
    (``pip install "hedron[auth]"``).
    """
    require_authlib()
    from authlib.common.urls import add_params_to_uri

    if not state:
        raise ValueError("state is required")
    scopes: Sequence[str] = config.scopes
    params: list[tuple[str, str]] = [
        ("response_type", "code"),
        ("client_id", config.client_id),
        ("redirect_uri", config.redirect_uri),
        ("scope", " ".join(scopes)),
        ("state", state),
    ]
    if nonce:
        params.append(("nonce", nonce))
    if code_challenge:
        params.append(("code_challenge", code_challenge))
        params.append(("code_challenge_method", code_challenge_method))
    if extra_params:
        _reject_reserved_extra_params(extra_params)
        params.extend((str(k), str(v)) for k, v in extra_params.items())
    return add_params_to_uri(config.resolved_authorize_url(), params)


def logout_url(
    config: OidcClientConfig,
    *,
    id_token_hint: str | None = None,
    post_logout_redirect_uri: str | None = None,
    state: str | None = None,
    extra_params: Mapping[str, str] | None = None,
) -> str:
    """Build an OIDC end-session / logout URL via Authlib URL helpers.

    Raises ``HED-AUTH-0001`` when Authlib is not installed
    (``pip install "hedron[auth]"``).
    """
    require_authlib()
    from authlib.common.urls import add_params_to_uri

    params: list[tuple[str, str]] = [("client_id", config.client_id)]
    if id_token_hint:
        params.append(("id_token_hint", id_token_hint))
    if post_logout_redirect_uri:
        _validate_post_logout_redirect_uri(post_logout_redirect_uri, config)
        params.append(("post_logout_redirect_uri", post_logout_redirect_uri))
    if state:
        params.append(("state", state))
    if extra_params:
        _reject_reserved_extra_params(extra_params)
        params.extend((str(k), str(v)) for k, v in extra_params.items())
    return add_params_to_uri(config.resolved_end_session_url(), params)
