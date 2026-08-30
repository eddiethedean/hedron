"""Explicit Edron deployment profiles and bounded production diagnostics.

Deployment inspection is deliberately side-effect free. It reads declared
configuration and local build metadata only; it never imports an application,
contacts a host, discovers infrastructure, or resolves a resource/job backend.
The native Hedron host remains the authority for request handling and startup
enforcement.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast
from urllib.parse import urlsplit

from edron.diagnostics import DiagnosticReport, EdronDiagnostic, finding

DeploymentProfileName = Literal[
    "local",
    "single-process",
    "reverse-proxy",
    "container",
    "orchestrated",
    "workbench",
    "posit-connect",
]
BackendMode = Literal["process-local", "shared", "unknown"]

PROFILE_SCHEMA = "edron.deployment-profile/1"
REPORT_SCHEMA = "edron.deployment-report/1"
ARTIFACT_SCHEMA = "edron.artifact-manifest/1"
PROFILE_NAMES: tuple[DeploymentProfileName, ...] = (
    "local",
    "single-process",
    "reverse-proxy",
    "container",
    "orchestrated",
    "workbench",
    "posit-connect",
)
PROFILE_ALIASES = {
    "development": "local",
    "production": "single-process",
    "proxy": "reverse-proxy",
    "kubernetes": "orchestrated",
    "k8s": "orchestrated",
    "connect": "posit-connect",
}
_SECRET_ENV_NAMES = ("HEDRON_SESSION_SECRET", "EDRON_SESSION_SECRET")
_PROFILE_ENV_NAMES = ("EDRON_DEPLOYMENT_PROFILE", "HEDRON_DEPLOYMENT_PROFILE")
_PROFILE_FIELDS = {
    "production",
    "bind",
    "port",
    "workers",
    "root_path",
    "build_dir",
    "external_url",
    "trust_proxy",
    "state_backend",
    "job_backend",
    "host",
    "allow_external_bind",
}
_MAX_DIAGNOSTICS = 96
_MAX_TRUST_PROXIES = 32
_MAX_ARTIFACTS = 512


class DeploymentError(ValueError):
    """Raised when an explicit deployment profile cannot be constructed."""


def _normalize_profile_name(value: str) -> DeploymentProfileName:
    normalized = value.strip().lower().replace("_", "-")
    normalized = PROFILE_ALIASES.get(normalized, normalized)
    if normalized not in PROFILE_NAMES:
        choices = ", ".join(PROFILE_NAMES)
        raise DeploymentError(f"unknown deployment profile {value!r}; choose from {choices}")
    return normalized  # type: ignore[return-value]


def _normalize_root_path(value: str | None) -> str:
    if value is None or not str(value).strip():
        return ""
    raw = str(value).strip()
    parts = urlsplit(raw)
    if parts.scheme or parts.netloc or parts.query or parts.fragment:
        raise DeploymentError("root_path must be a local path without scheme, query, or fragment")
    if not raw.startswith("/") or "//" in raw or "\\" in raw or ".." in raw.split("/"):
        raise DeploymentError("root_path must be an absolute normalized path")
    return raw.rstrip("/") or "/"


def _normalize_build_dir(value: str | Path | None) -> str:
    raw = ".hedron/build" if value is None else str(value).strip()
    if not raw:
        raise DeploymentError("build_dir must not be empty")
    if "\x00" in raw:
        raise DeploymentError("build_dir contains a NUL byte")
    return raw


def _validate_external_url(value: str | None, *, root_path: str, production: bool) -> str | None:
    if value is None or not str(value).strip():
        return None
    raw = str(value).strip()
    parsed = urlsplit(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise DeploymentError("external_url must be an absolute http(s) URL")
    if parsed.username or parsed.password:
        raise DeploymentError("external_url must not contain credentials")
    if parsed.query or parsed.fragment:
        raise DeploymentError("external_url must not contain a query or fragment")
    if production and parsed.scheme != "https":
        raise DeploymentError("production external_url must use https")
    external_path = parsed.path.rstrip("/") or ""
    expected_path = root_path.rstrip("/") if root_path not in {"", "/"} else ""
    if external_path != expected_path:
        raise DeploymentError(
            f"external_url path {external_path or '/'} must match root_path {root_path or '/'}"
        )
    return raw.rstrip("/")


def _is_external_bind(bind: str) -> bool:
    return bind not in {"127.0.0.1", "localhost", "::1"}


def _validate_backend(value: str, field_name: str) -> BackendMode:
    normalized = value.strip().lower().replace("_", "-")
    if normalized not in {"process-local", "shared", "unknown"}:
        raise DeploymentError(f"{field_name} must be process-local, shared, or unknown")
    return normalized  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class DeploymentProfile:
    """Validated, serializable deployment assumptions.

    The profile describes a launch boundary. It does not start a server or
    grant trust to a proxy. ``state_backend`` and ``job_backend`` are claims
    supplied by the deployer and are intentionally not inferred.
    """

    name: DeploymentProfileName
    production: bool
    bind: str = "127.0.0.1"
    port: int = 8000
    workers: int = 1
    root_path: str = ""
    build_dir: str = ".hedron/build"
    external_url: str | None = None
    trust_proxy: tuple[str, ...] = ()
    state_backend: BackendMode = "process-local"
    job_backend: BackendMode = "process-local"
    host: str = "asgi"
    allow_external_bind: bool = False

    def __post_init__(self) -> None:
        name = _normalize_profile_name(self.name)
        root_path = _normalize_root_path(self.root_path)
        build_dir = _normalize_build_dir(self.build_dir)
        external_url = _validate_external_url(
            self.external_url, root_path=root_path, production=self.production
        )
        raw_bind: object = self.bind
        if not isinstance(cast(Any, raw_bind), str) or not raw_bind.strip():
            raise DeploymentError("bind must be a non-empty host")
        raw_port: object = self.port
        if not isinstance(cast(Any, raw_port), int) or not 1 <= raw_port <= 65_535:
            raise DeploymentError("port must be between 1 and 65535")
        raw_workers: object = self.workers
        if not isinstance(cast(Any, raw_workers), int) or not 1 <= raw_workers <= 256:
            raise DeploymentError("workers must be between 1 and 256")
        if _is_external_bind(self.bind) and not self.allow_external_bind:
            raise DeploymentError(
                "external bind requires allow_external_bind=True; use the platform "
                "boundary explicitly"
            )
        if (
            name in {"local", "single-process", "reverse-proxy", "workbench", "posit-connect"}
            and self.workers != 1
            and name != "reverse-proxy"
        ):
            raise DeploymentError(f"{name} profile defaults to one worker")
        if name in {"workbench", "posit-connect"} and self.host != "asgi":
            raise DeploymentError(f"{name} supports only the ASGI host handoff")
        if len(self.trust_proxy) > _MAX_TRUST_PROXIES:
            raise DeploymentError(f"trust_proxy accepts at most {_MAX_TRUST_PROXIES} entries")
        if any(
            not isinstance(cast(Any, item), str) or not item.strip() for item in self.trust_proxy
        ):
            raise DeploymentError("trust_proxy entries must be non-empty strings")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "root_path", root_path)
        object.__setattr__(self, "build_dir", build_dir)
        object.__setattr__(self, "external_url", external_url)
        object.__setattr__(
            self, "state_backend", _validate_backend(self.state_backend, "state_backend")
        )
        object.__setattr__(self, "job_backend", _validate_backend(self.job_backend, "job_backend"))
        object.__setattr__(self, "trust_proxy", tuple(item.strip() for item in self.trust_proxy))

    @classmethod
    def for_name(cls, name: str | DeploymentProfileName, **overrides: Any) -> DeploymentProfile:
        """Create one named profile with explicit overrides."""
        canonical = _normalize_profile_name(str(name))
        defaults: dict[DeploymentProfileName, dict[str, Any]] = {
            "local": {"production": False},
            "single-process": {"production": True},
            "reverse-proxy": {"production": True, "root_path": "/"},
            "container": {"production": True, "bind": "0.0.0.0", "allow_external_bind": True},
            "orchestrated": {
                "production": True,
                "bind": "0.0.0.0",
                "allow_external_bind": True,
            },
            "workbench": {"production": True},
            "posit-connect": {"production": True},
        }
        values = {**defaults[canonical], **overrides, "name": canonical}
        production = values.get("production", False)
        if not isinstance(production, bool):
            raise DeploymentError("production must be true or false")
        bind = values.get("bind", "127.0.0.1")
        port = values.get("port", 8000)
        workers = values.get("workers", 1)
        if not isinstance(bind, str) or not isinstance(port, int) or not isinstance(workers, int):
            raise DeploymentError("bind, port, and workers must have their declared types")
        trust_proxy = values.get("trust_proxy", ())
        if isinstance(trust_proxy, str):
            trust_proxy = tuple(item.strip() for item in trust_proxy.split(",") if item.strip())
        elif not isinstance(trust_proxy, tuple) or not all(
            isinstance(item, str) for item in cast(tuple[object, ...], trust_proxy)
        ):
            raise DeploymentError("trust_proxy must be a tuple of strings")
        trust_proxy = cast(tuple[str, ...], trust_proxy)
        state_backend = _validate_backend(
            str(values.get("state_backend", "process-local")), "state_backend"
        )
        job_backend = _validate_backend(
            str(values.get("job_backend", "process-local")), "job_backend"
        )
        return cls(
            name=canonical,
            production=production,
            bind=bind,
            port=port,
            workers=workers,
            root_path=str(values.get("root_path", "")),
            build_dir=str(values.get("build_dir", ".hedron/build")),
            external_url=values.get("external_url"),
            trust_proxy=trust_proxy,
            state_backend=state_backend,
            job_backend=job_backend,
            host=str(values.get("host", "asgi")),
            allow_external_bind=bool(values.get("allow_external_bind", False)),
        )

    from_name = for_name

    def to_mapping(self, *, redact_paths: bool = False) -> dict[str, Any]:
        build_dir = self.build_dir
        if redact_paths and Path(build_dir).is_absolute():
            build_dir = "<absolute-path>"
        return {
            "schema": PROFILE_SCHEMA,
            "name": self.name,
            "production": self.production,
            "bind": self.bind,
            "port": self.port,
            "workers": self.workers,
            "root_path": self.root_path,
            "build_dir": build_dir,
            "external_url": self.external_url,
            "trust_proxy": list(self.trust_proxy),
            "state_backend": self.state_backend,
            "job_backend": self.job_backend,
            "host": self.host,
            "allow_external_bind": self.allow_external_bind,
        }


@dataclass(frozen=True, slots=True)
class DeploymentResolution:
    """A profile plus non-throwing resolution findings."""

    profile: DeploymentProfile
    diagnostics: DiagnosticReport = field(default_factory=DiagnosticReport)

    @property
    def ok(self) -> bool:
        return self.diagnostics.ok

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema": REPORT_SCHEMA,
            "ok": self.ok,
            "profile": self.profile.to_mapping(redact_paths=True),
            "diagnostics": self.diagnostics.to_mapping()["diagnostics"],
        }


@dataclass(frozen=True, slots=True)
class DeploymentReport:
    """Bounded deployment profile and local artifact diagnostics."""

    resolution: DeploymentResolution
    diagnostics: DiagnosticReport

    @property
    def profile(self) -> DeploymentProfile:
        return self.resolution.profile

    @property
    def ok(self) -> bool:
        return self.diagnostics.ok

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema": REPORT_SCHEMA,
            "ok": self.ok,
            "profile": self.profile.to_mapping(redact_paths=True),
            "diagnostics": self.diagnostics.to_mapping()["diagnostics"],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_mapping(), indent=2, sort_keys=True) + "\n"

    def to_text(self) -> str:
        header = f"Edron deployment profile: {self.profile.name}"
        return header + "\n\n" + self.diagnostics.to_text()

    def to_sarif(self) -> dict[str, Any]:
        return self.diagnostics.to_sarif()


def _diagnostic(
    code: str,
    severity: Literal["error", "warning", "information"],
    title: str,
    explanation: str,
    remediation: str = "",
    *,
    context: Mapping[str, Any] | None = None,
) -> EdronDiagnostic:
    return finding(
        code,
        severity=severity,
        title=title,
        explanation=explanation,
        remediation=remediation,
        context=context,
    )


def _env_value(environ: Mapping[str, str], *names: str) -> tuple[str | None, str | None]:
    present = [(name, environ[name]) for name in names if name in environ and environ[name].strip()]
    if not present:
        return None, None
    return present[0][1], present[0][0]


def resolve_deployment_profile(
    name: str | DeploymentProfileName | None = None,
    *,
    profile: str | DeploymentProfileName | None = None,
    environ: Mapping[str, str] | None = None,
    cwd: str | Path | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> DeploymentResolution:
    """Resolve a deployment profile without importing or executing an app.

    Explicit values win over environment values only after a conflict finding
    is recorded. This makes precedence observable instead of silently trusting
    a stale launcher or proxy setting.
    """
    del cwd  # Reserved for path checks in the artifact layer; resolution is path-independent.
    env = os.environ if environ is None else environ
    findings: list[EdronDiagnostic] = []
    if name is not None and profile is not None and str(name) != str(profile):
        findings.append(
            _diagnostic(
                "EDR-08-PROFILE-CONFLICT",
                "error",
                "Deployment profile arguments conflict",
                "The name and profile arguments specify different deployment profiles.",
                "Pass one profile name.",
            )
        )
    if name is None:
        name = profile
    env_name, env_name_source = _env_value(env, *_PROFILE_ENV_NAMES)
    selected_name = str(name) if name is not None else env_name
    if selected_name is None:
        selected_name = (
            "single-process"
            if env.get("HEDRON_ENV", "").lower() in {"prod", "production"}
            else "local"
        )
    if name is not None and env_name is not None:
        try:
            if _normalize_profile_name(str(name)) != _normalize_profile_name(env_name):
                findings.append(
                    _diagnostic(
                        "EDR-08-PROFILE-CONFLICT",
                        "error",
                        "Deployment profile conflict",
                        f"explicit profile {name!r} conflicts with {env_name_source}.",
                        "Remove the stale environment profile or pass the same canonical profile.",
                    )
                )
        except DeploymentError:
            pass

    try:
        canonical = _normalize_profile_name(selected_name)
    except DeploymentError as exc:
        findings.append(
            _diagnostic(
                "EDR-08-PROFILE-0001",
                "error",
                "Unknown deployment profile",
                str(exc),
                "Choose a documented profile name.",
            )
        )
        canonical = "local"

    values: dict[str, Any] = {}
    env_fields = {
        "bind": ("EDRON_BIND", "HEDRON_BIND"),
        "port": ("EDRON_PORT", "HEDRON_PORT"),
        "workers": ("EDRON_WORKERS", "WEB_CONCURRENCY"),
        "root_path": ("EDRON_ROOT_PATH", "HEDRON_ROOT_PATH"),
        "build_dir": ("EDRON_BUILD_DIR", "HEDRON_BUILD_DIR"),
        "external_url": ("EDRON_EXTERNAL_URL", "HEDRON_EXTERNAL_BASE_URL"),
        "state_backend": ("EDRON_STATE_BACKEND",),
        "job_backend": ("EDRON_JOB_BACKEND",),
        "host": ("EDRON_HOST",),
    }
    for field_name, names in env_fields.items():
        value, source = _env_value(env, *names)
        if value is None:
            continue
        try:
            if field_name in {"port", "workers"}:
                values[field_name] = int(value)
            elif field_name in {"state_backend", "job_backend"}:
                values[field_name] = _validate_backend(value, field_name)
            elif field_name == "root_path":
                values[field_name] = _normalize_root_path(value)
            else:
                values[field_name] = value
        except (DeploymentError, ValueError) as exc:
            findings.append(
                _diagnostic(
                    "EDR-08-CONFIG-0001",
                    "error",
                    "Invalid deployment environment",
                    f"{source} is invalid: {exc}",
                    "Correct the environment value or remove it and use an explicit profile.",
                    context={"field": field_name, "source": source},
                )
            )

    trust_proxy, trust_source = _env_value(env, "EDRON_TRUST_PROXY", "HEDRON_TRUST_PROXY")
    if trust_proxy is not None:
        values["trust_proxy"] = tuple(
            item.strip() for item in trust_proxy.split(",") if item.strip()
        )
        if not values["trust_proxy"]:
            findings.append(
                _diagnostic(
                    "EDR-08-CONFIG-0002",
                    "error",
                    "Empty proxy trust",
                    f"{trust_source} did not contain a proxy address.",
                    "Use exact proxy IPs/CIDRs or leave forwarded-header trust disabled.",
                )
            )

    explicit = dict(overrides or {})
    profile_overrides = {
        field_name: value for field_name, value in explicit.items() if field_name in _PROFILE_FIELDS
    }
    for field_name, value in profile_overrides.items():
        if value is None:
            continue
        if field_name in values and values[field_name] != value:
            findings.append(
                _diagnostic(
                    "EDR-08-CONFIG-CONFLICT",
                    "error",
                    "Deployment configuration conflict",
                    f"explicit {field_name} conflicts with an environment value.",
                    "Remove one source of configuration so the deployment is deterministic.",
                    context={"field": field_name},
                )
            )
        values[field_name] = value

    try:
        resolved_profile = DeploymentProfile.for_name(canonical, **values)
    except DeploymentError as exc:
        findings.append(
            _diagnostic(
                "EDR-08-PROFILE-0002",
                "error",
                "Deployment profile is invalid",
                str(exc),
                "Adjust the explicit profile values and rerun the deployment check.",
            )
        )
        resolved_profile = DeploymentProfile.for_name("local")
    return DeploymentResolution(
        resolved_profile, DiagnosticReport(tuple(findings[:_MAX_DIAGNOSTICS]))
    )


def _path_for_build_dir(build_dir: str, *, cwd: str | Path | None) -> Path:
    root = Path(cwd or Path.cwd())
    path = Path(build_dir)
    return path if path.is_absolute() else root / path


def _check_build_manifest(
    profile: DeploymentProfile, *, cwd: str | Path | None
) -> list[EdronDiagnostic]:
    if not profile.production:
        return []
    path = _path_for_build_dir(profile.build_dir, cwd=cwd) / "manifest.json"
    if not path.is_file():
        return [
            _diagnostic(
                "EDR-08-BUILD-0001",
                "error",
                "Production build manifest missing",
                "The selected production profile has no local manifest.json.",
                "Run `hedron build` and include the build directory in the deployed artifact.",
                context={"build_dir": profile.build_dir},
            )
        ]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [
            _diagnostic(
                "EDR-08-BUILD-0002",
                "error",
                "Production build manifest invalid",
                f"manifest.json could not be read as a JSON object: {exc}",
                "Run `hedron build` again and deploy the complete build directory.",
            )
        ]
    if not isinstance(payload, dict) or not payload:
        return [
            _diagnostic(
                "EDR-08-BUILD-0003",
                "error",
                "Production build manifest is empty",
                "manifest.json must contain a non-empty JSON object.",
                "Run `hedron build` and verify that the generated manifest is copied into "
                "the image.",
            )
        ]
    return []


def _check_profile_claims(profile: DeploymentProfile) -> list[EdronDiagnostic]:
    findings: list[EdronDiagnostic] = []
    if profile.production and profile.bind in {"127.0.0.1", "localhost", "::1"}:
        findings.append(
            _diagnostic(
                "EDR-08-PROFILE-0003",
                "information",
                "Loopback production bind",
                "The profile expects a local process supervisor or reverse proxy to expose "
                "the application.",
                "Keep the loopback bind only when the platform boundary is explicit.",
            )
        )
    if profile.workers > 1 and profile.state_backend != "shared":
        findings.append(
            _diagnostic(
                "EDR-08-OPS-0001",
                "error",
                "Multi-worker state backend is not shared",
                "Multiple workers cannot safely claim shared session/resource state with this "
                "profile.",
                "Declare a verified shared native backend or use one worker.",
                context={"workers": profile.workers, "state_backend": profile.state_backend},
            )
        )
    if profile.workers > 1 and profile.job_backend != "shared":
        findings.append(
            _diagnostic(
                "EDR-08-OPS-0002",
                "error",
                "Multi-worker job backend is not shared",
                "Multiple workers cannot safely claim durable job coordination with this profile.",
                "Declare a verified shared native job backend or use one worker.",
                context={"workers": profile.workers, "job_backend": profile.job_backend},
            )
        )
    if profile.trust_proxy and any("*" in item for item in profile.trust_proxy):
        findings.append(
            _diagnostic(
                "EDR-08-EDGE-0001",
                "error",
                "Wildcard proxy trust is forbidden",
                "Forwarded headers must not be trusted from every peer.",
                "List exact proxy addresses or bounded CIDRs.",
            )
        )
    if profile.name in {"workbench", "posit-connect"} and not profile.root_path:
        findings.append(
            _diagnostic(
                "EDR-08-HOST-0001",
                "information",
                "Host mount will be supplied at launch",
                "The host profile has no construction-time root path; launch-time handoff must "
                "set it before app import.",
                "Use the native host launcher and verify cookie and URL paths with a mounted "
                "smoke test.",
            )
        )
    return findings


def _check_secret(
    profile: DeploymentProfile, *, environ: Mapping[str, str], overrides: Mapping[str, Any] | None
) -> list[EdronDiagnostic]:
    if not profile.production:
        return []
    declared = (overrides or {}).get("secret_source")
    if declared or any(environ.get(name, "").strip() for name in _SECRET_ENV_NAMES):
        return []
    return [
        _diagnostic(
            "EDR-08-SECURITY-0001",
            "error",
            "Production session secret is not declared",
            "No approved secret source was declared for the production profile.",
            "Inject HEDRON_SESSION_SECRET/EDRON_SESSION_SECRET at runtime or declare the "
            "platform secret reference.",
        )
    ]


def check_deployment(
    name: str | DeploymentProfileName | None = None,
    *,
    profile: str | DeploymentProfileName | None = None,
    environ: Mapping[str, str] | None = None,
    cwd: str | Path | None = None,
    overrides: Mapping[str, Any] | None = None,
    application: Any = None,
) -> DeploymentReport:
    """Check a profile, build manifest, trust boundary, and app metadata.

    ``application`` is optional and is inspected only through inert metadata
    attributes. It is never imported, called, or probed over HTTP.
    """
    env = os.environ if environ is None else environ
    resolution = resolve_deployment_profile(
        name, profile=profile, environ=env, cwd=cwd, overrides=overrides
    )
    findings = list(resolution.diagnostics.diagnostics)
    findings.extend(_check_profile_claims(resolution.profile))
    findings.extend(_check_build_manifest(resolution.profile, cwd=cwd))
    findings.extend(_check_secret(resolution.profile, environ=env, overrides=overrides))

    if application is not None:
        state = getattr(getattr(application, "hedron", None), "state", None)
        actual_production = getattr(state, "hedron_production", None)
        if (
            actual_production is not None
            and bool(actual_production) != resolution.profile.production
        ):
            findings.append(
                _diagnostic(
                    "EDR-08-APP-0001",
                    "error",
                    "Application/profile production mismatch",
                    "The declared profile does not match the native app production mode.",
                    "Use the same production setting for the Edron app and deployment profile.",
                )
            )
        actual_root = getattr(state, "hedron_root_path", None)
        if actual_root and str(actual_root).rstrip("/") != resolution.profile.root_path.rstrip("/"):
            findings.append(
                _diagnostic(
                    "EDR-08-APP-0002",
                    "error",
                    "Application/profile root path mismatch",
                    "The app construction mount differs from the selected deployment mount.",
                    "Set one explicit root path before constructing the Edron app.",
                )
            )

    return DeploymentReport(
        resolution,
        DiagnosticReport(tuple(findings[:_MAX_DIAGNOSTICS]), schema=REPORT_SCHEMA),
    )


def artifact_records(
    paths: Iterable[str | Path], *, root: str | Path | None = None
) -> tuple[dict[str, Any], ...]:
    """Return bounded SHA-256 records for already-built release artifacts."""
    root_path = Path(root or Path.cwd()).resolve()
    records: list[dict[str, Any]] = []
    for value in paths:
        path = Path(value)
        if not path.is_file():
            raise FileNotFoundError(path)
        resolved = path.resolve()
        try:
            source = resolved.relative_to(root_path).as_posix()
        except ValueError as exc:
            raise DeploymentError("artifact path must be beneath the declared root") from exc
        digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
        records.append(
            {
                "name": resolved.name,
                "source": source,
                "sha256": digest,
                "size": resolved.stat().st_size,
            }
        )
        if len(records) >= _MAX_ARTIFACTS:
            break
    return tuple(sorted(records, key=lambda item: (str(item["name"]), str(item["source"]))))


def artifact_manifest(
    paths: Iterable[str | Path],
    *,
    version: str,
    root: str | Path | None = None,
    project: str = "edron",
) -> dict[str, Any]:
    """Build deterministic release metadata without writing or publishing it."""
    if not version.strip():
        raise DeploymentError("artifact manifest version must not be empty")
    records = artifact_records(paths, root=root)
    payload = {
        "schema": ARTIFACT_SCHEMA,
        "project": project,
        "version": version,
        "artifacts": list(records),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["fingerprint"] = hashlib.sha256(encoded).hexdigest()[:32]
    return payload


__all__ = [
    "ARTIFACT_SCHEMA",
    "BackendMode",
    "DeploymentError",
    "DeploymentProfile",
    "DeploymentProfileName",
    "DeploymentReport",
    "DeploymentResolution",
    "PROFILE_NAMES",
    "PROFILE_SCHEMA",
    "artifact_manifest",
    "artifact_records",
    "check_deployment",
    "deployment_report",
    "profile_from_environment",
    "resolve_deployment_profile",
]

deployment_report = check_deployment
profile_from_environment = resolve_deployment_profile
