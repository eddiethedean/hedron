# Async runtime integration

## Foundation

Hedron relies on FastAPI, Starlette, AnyIO, and Python asyncio. It does not maintain a separate scheduler. Route handlers use FastAPI’s sync thread-pool and async execution semantics.

## Awaitable boundaries

Endpoint factories, actions, data sources, option providers, cache loaders, plugin hooks, and future preparation hooks expose explicit sync or async protocols. Internal invocation uses a single await-if-needed utility that preserves cancellation and contextual errors.

Structured parallel work uses task groups. A helper such as `hedron.gather()` returns named results, cancels siblings on failure unless a partial-failure policy is declared, and binds all work to request scope. Legacy blocking calls may use a documented `run_sync` wrapper; CPU-heavy work is rejected or delegated to jobs.

## Lifetimes

User and Hedron lifespan contexts compose. Yield dependencies remain active through ordinary rendering and response iteration. Timeouts use cancel scopes and convert only at declared component boundaries. Shared single-flight cache loads distinguish waiter cancellation from underlying load ownership.

## Verification

Test sync/async mixtures, task failure, disconnect cancellation, timeout policies, cleanup, nested lifespan order, blocking-operation diagnostics, background-task registration, and absence of leaked tasks.

