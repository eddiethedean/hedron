"""OIDC conveniences over Authlib without owning identity or sessions.

Host sessions remain authoritative. Hedron does not create an identity database,
infer authorization, or act as an IdP. These helpers cover PKCE/state/nonce,
claim normalization, Explorer-safe redaction, and Authlib-backed URL builders.
"""

from __future__ import annotations

from hedron.auth.oidc import OidcClientConfig as OidcClientConfig
from hedron.auth.oidc import OidcPkcePair as OidcPkcePair
from hedron.auth.oidc import OidcUserClaims as OidcUserClaims
from hedron.auth.oidc import OidcUserClaimsDict as OidcUserClaimsDict
from hedron.auth.oidc import generate_nonce as generate_nonce
from hedron.auth.oidc import generate_pkce as generate_pkce
from hedron.auth.oidc import generate_state as generate_state
from hedron.auth.oidc import login_url as login_url
from hedron.auth.oidc import logout_url as logout_url
from hedron.auth.oidc import normalize_claims as normalize_claims
from hedron.auth.oidc import redact_claims as redact_claims
from hedron.auth.oidc import store_oidc_handshake as store_oidc_handshake
from hedron.auth.oidc import validate_callback_nonce as validate_callback_nonce
from hedron.auth.oidc import validate_callback_state as validate_callback_state

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
