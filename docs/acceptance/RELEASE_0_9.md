# Hedron `v0.9.0` native-framework acceptance

Phase 0.9 deepens Flask and Django integration and may promote the currently deferred QuerySet data
source. Every new claim requires an accepted contract, native-framework evidence, package isolation,
and published-artifact upgrade/rollback proof. Evidence is indexed by
[`release-gate-0.9.toml`](release-gate-0.9.toml).

## Flask application integration

- [ ] Blueprint and application-factory usage works through a small `init_app`-style layer without
  hidden process-global state or a FastAPI dependency. *(`FRM-FLK-09-001`)*
- [ ] Existing constructor-based 0.8 applications remain supported or have an automated, documented
  migration with deprecation diagnostics. *(`MIG-09-001`)*
- [ ] Native routing, `url_for`, sessions, CSRF, errors, assets, lifecycle, WSGI deployment, and
  multiple-app isolation pass the Supported matrix. *(`FRM-FLK-09-001`)*

## Django reusable application

- [ ] `AppConfig`, namespaced URL inclusion, middleware-aware setup, and system checks integrate
  without hidden settings mutation or import-time application access. *(`FRM-DJG-09-001`)*
- [ ] WSGI and ASGI profiles pass routing, reverse URLs, sessions, CSRF, errors, assets, lifecycle,
  deployment-prefix, and multiple-site isolation evidence. *(`FRM-DJG-09-001`)*
- [ ] Any Django-native forms bridge preserves authoritative Django validation and the portable
  interaction/error contract without claiming Pydantic parity. *(`FORM-DJG-09-001`)*
- [ ] A newer Django major line is promoted only after upstream support and the full native matrix
  are recorded; dependency metadata alone does not create a Supported claim. *(`COMPAT-09-001`)*

## QuerySet data source

- [ ] QuerySet paging, ordering, filtering, and projection execute as bounded database operations;
  implicit collection and unbounded counts are rejected or diagnosed. *(`DATA-DJG-09-001`)*
- [ ] Field allowlists, tenant/authorization hooks, transaction ownership, sync/async behavior,
  cancellation, and error mapping are explicit and pass adversarial tests. *(`DATA-DJG-09-001`)*
- [ ] Query-count and plan evidence covers empty, large, filtered, ordered, concurrent, and degraded
  cases without leaking model fields or query details. *(`DATA-DJG-09-001`)*

## Optional job bridges

- [ ] Any Celery or RQ bridge implements the existing `JobBackend` state/idempotency/auth/retention/
  cancellation contract and leaves broker/result-backend ownership to the application.
  *(`JOB-09-001`)*
- [ ] Bounded polling remains the portable fallback; adding a broker does not imply SSE or another
  live transport before phase 0.10. *(`JOB-09-001`)*

## Release proof

- [ ] New distributions/extras install without FastAPI leakage, preserve the dependency graph, and
  report accurate capability/stability metadata. *(`PKG-09-001`)*
- [ ] Published `0.9.0` artifacts pass clean install, upgrade from supported `0.8.x`, native
  reference deployments, documentation examples, rollback, SBOM/license/provenance, and supported
  Python/framework matrices. *(`PKG-09-001`, `MIG-09-001`)*
- [ ] Every completed requirement links to a command or retained artifact; Deferred items name an
  owner, rationale, destination phase, and stability impact.

## Exit

All advertised 0.9 capabilities are `Verified` or explicitly owned `Deferred`. The native
convenience layers remain thin framework integrations, QuerySet operations remain bounded and
authorization-aware, and existing 0.8 application shapes have tested migrations.
