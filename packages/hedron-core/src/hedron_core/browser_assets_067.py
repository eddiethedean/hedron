"""Pinned browser supply metadata for the Phase 0.67 CSP lane.

The catalog is deliberately data-only.  It is consumed by manifests, release
checks, and offline build tooling; it never downloads or executes an upstream
package.  The runtime shipped by Hedron remains the local same-origin module.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

__all__ = [
    "ALPINE_067_ARTIFACTS",
    "ALPINE_FILE_INTEGRITY",
    "AlpineArtifact",
    "alpine_artifact_manifest",
]


@dataclass(frozen=True, slots=True)
class AlpineArtifact:
    """One reproducibly resolved Alpine artifact."""

    package: str
    version: str
    integrity: str
    license: str
    source: str
    local_path: str
    maturity: str = "Supported"

    def __post_init__(self) -> None:
        if not self.package or not self.version or not self.integrity.startswith("sha512-"):
            raise ValueError("Alpine artifacts require package, version, and sha512 integrity")
        if self.license != "MIT":
            raise ValueError("Phase 0.67 Alpine artifacts must carry the MIT license")
        if not self.local_path.startswith("/hedron-static/"):
            raise ValueError("Alpine artifacts must be vendored under /hedron-static/")
        if self.maturity not in {"Supported", "Progressive", "Experimental", "Excluded"}:
            raise ValueError("invalid Alpine artifact maturity")

    def to_dict(self) -> dict[str, str]:
        return {
            "package": self.package,
            "version": self.version,
            "integrity": self.integrity,
            "license": self.license,
            "source": self.source,
            "local_path": self.local_path,
            "maturity": self.maturity,
        }


_NPM = "https://registry.npmjs.org"
_GITHUB = "https://github.com/alpinejs/alpine/tree/v3.16.3"

ALPINE_067_ARTIFACTS: Mapping[str, AlpineArtifact] = MappingProxyType(
    {
        "core": AlpineArtifact(
            "@alpinejs/csp", "3.16.3",
            "sha512-eqz6rpWDXuJOGp3YvsXQqZljjBz7ZWAkEmJUt3zTJyK9SEjUcInfOx7sRLzEUlrU+o9r2UhxCVhFBc5eJAUMdA==",
            "MIT", f"{_GITHUB}/packages/csp", "/hedron-static/alpine/csp-3.16.3.js",
        ),
        "anchor": AlpineArtifact(
            "@alpinejs/anchor", "3.16.3",
            "sha512-l53MqW/ZNzR+0jmQ6WhRWEb0K3ZxXhWxgjnLTA+GDX99wCO47lYaD8SIPjxXRARfcrRKPzrpj1llKa0pfwg1kw==",
            "MIT", f"{_NPM}/@alpinejs/anchor", "/hedron-static/alpine/anchor-3.16.3.js",
        ),
        "collapse": AlpineArtifact(
            "@alpinejs/collapse", "3.16.3",
            "sha512-ekH5VBTpMBNnffAfvL+3mqFLIWNW4bUmCExEl+1WdGPewtVYBI2kMWNd2lVOsrvsDRSij7VGmAG0AK5s8WD03g==",
            "MIT", f"{_NPM}/@alpinejs/collapse", "/hedron-static/alpine/collapse-3.16.3.js",
        ),
        "focus": AlpineArtifact(
            "@alpinejs/focus", "3.16.3",
            "sha512-MwEeux0W+/DP4B3FyNHPs+kzqMmgfWRf25WsJLBH1kahBqiVHNLewSJotbO+9345A8WsHz3yx8XkaeNnepDv3Q==",
            "MIT", f"{_NPM}/@alpinejs/focus", "/hedron-static/alpine/focus-3.16.3.js",
        ),
        "intersect": AlpineArtifact(
            "@alpinejs/intersect", "3.16.3",
            "sha512-hGiwxwfuRjiYpxnuZOD5ymQAPhyxspVfhwuSEg/TdJhfqmfacJd4Z42LIKIdXoDE8JaexXvrUeg5MBxzLVgMmQ==",
            "MIT", f"{_NPM}/@alpinejs/intersect", "/hedron-static/alpine/intersect-3.16.3.js",
        ),
        "mask": AlpineArtifact(
            "@alpinejs/mask", "3.16.3",
            "sha512-BKu3IT4kk1GqgH8Lsn8ekV6nrbbMJgjOuI6zC+rJ+m/iPxBstH80ELauD23a7OiJAVQZjdS+lmYFfCVAbk3Rqg==",
            "MIT", f"{_NPM}/@alpinejs/mask", "/hedron-static/alpine/mask-3.16.3.js",
        ),
        "morph": AlpineArtifact(
            "@alpinejs/morph", "3.16.3",
            "sha512-JUrZ9tCXTgdQRoHAIdCDzdrkyEC8ffXwFlynEQ7it0jFy2UW4X0jpcRRBUhvyD94OiMpN6bd82eWhd+3PaqP+g==",
            "MIT", f"{_NPM}/@alpinejs/morph", "/hedron-static/alpine/morph-3.16.3.js",
            "Progressive",
        ),
        "persist": AlpineArtifact(
            "@alpinejs/persist", "3.16.3",
            "sha512-VyhG3C1CKTvGwHQICw1GLfqIuUt++q54oSRGstX+Y30yjj+JK6HrWj50yzAS+C2K8SXnR99ipY6SQevLaHAgog==",
            "MIT", f"{_NPM}/@alpinejs/persist", "/hedron-static/alpine/persist-3.16.3.js",
            "Progressive",
        ),
        "resize": AlpineArtifact(
            "@alpinejs/resize", "3.16.3",
            "sha512-3GG13wnOqdYduvT1DPpdJolY254cT8eHw32bx3Ibay2v9HnPzRTDZ9BiZe4iI+1rEcH4E6IKsM7RsEjAaSO0Og==",
            "MIT", f"{_NPM}/@alpinejs/resize", "/hedron-static/alpine/resize-3.16.3.js",
        ),
        "sort": AlpineArtifact(
            "@alpinejs/sort", "3.16.3",
            "sha512-LEmI3oE+oIrWmAWoA4PhkA0/kvbrlAr5hBrAvreWU63U4oleTDpgp0LS0qzxBMLOzoEJKwupWuq9l2j6fz2erg==",
            "MIT", f"{_NPM}/@alpinejs/sort", "/hedron-static/alpine/sort-3.16.3.js",
            "Progressive",
        ),
        "ui": AlpineArtifact(
            "@alpinejs/ui", "3.16.3",
            "sha512-+XqQcRijbRZopSQLZJsFlmILB73E5k7fmGv4eesk3wOHZ+jAZ3s0IyXASGT+gpH8Qi7+wSNMI2V9QVegB93AQA==",
            "MIT", f"{_GITHUB}/packages/ui", "/hedron-static/alpine/ui-3.16.3.js",
            "Progressive",
        ),
    }
)

ALPINE_FILE_INTEGRITY: Mapping[str, str] = MappingProxyType(
    {
        "/hedron-static/hedron-alpine.mjs": "sha256-YvNtPDjF90uyi2GbohI2OoWyMpaRgSIvBapE44M7LoM=",
        **{
            artifact.local_path: digest
            for artifact, digest in zip(
                ALPINE_067_ARTIFACTS.values(),
                (
                    "sha256-Deia1aYmwCOYLC7XBR71/Ty/oi0BLegfoZAFyBG/rU0=",
                    "sha256-q0kd8m5Tt/9uUC4PpAOxlgznQqHkSY8gnYJH7PPp5IY=",
                    "sha256-x2YdTizwRl481pMZDeu19ZKsctzEz+ZQWBJzdnVYsns=",
                    "sha256-6n4hVET1EQYZVJYhzQdgzt/ic/cIsUTU5lioe3AlVfk=",
                    "sha256-9JmUi0YIXZ3lZUeFpzJUcKwLK6/14YImTL+rRe1Zp24=",
                    "sha256-C+S6dK02tTtK3B3LMsInP5gq0hdcChtUEgykTC14OfY=",
                    "sha256-QHQbbZRunH4BeH2P7+rRwVN6IM9yA3Jr5kjNqdLJ83U=",
                    "sha256-pdzYiHEu+QZjua7bExUVNEz3p4Qs1SDnUkCCSi0QXaQ=",
                    "sha256-mXR2L6neT584cfNLY5/imDq5DKjW1noXys7fhb1yxY4=",
                    "sha256-lPQCzNBTf5qjVrm2pMmz+jRohs/Qfgl5LQBbMGHa26w=",
                    "sha256-sPg+p7gioRl//c21Cli717Zmnc+m75/tiGCbS44/fbo=",
                ),
                strict=True,
            )
        },
    }
)


def alpine_artifact_manifest() -> tuple[dict[str, str], ...]:
    """Return deterministic, JSON-ready supply evidence."""
    return tuple(artifact.to_dict() for _, artifact in sorted(ALPINE_067_ARTIFACTS.items()))
