# RFC-0027: Data sources

**Status:** Proposed

## Purpose

Data-source protocols separate components from storage and dataframe implementations. They support synchronous and asynchronous fetch, mutation, option lookup, download, and visualization loading without making Hedron an ORM.

## Contracts

`DataQuery` describes bounded pagination, allowlisted sorting and filtering, projection, and cursor or offset state. `DataPage[T]` returns rows, schema metadata, continuation information, and optional version. `DataChanges[T]` and `DataSaveResult[T]` describe typed mutations, validation failures, and conflicts.

Adapters may support memory, Pandas, Polars, PyArrow, SQLAlchemy, SQLModel, Django QuerySets, or application services. Narwhals is the proposed optional normalization layer for dataframe-like inputs. Lazy sources must not be collected implicitly.

Authorization, transactions, tenant filtering, and business validation remain application responsibilities. Hedron provides hooks and requires safe boundaries but cannot derive the policy.

## Acceptance criteria

- Query sizes and fields are bounded and validated.
- Sync and async implementations expose the same component API.
- Versions support optimistic concurrency without exposing secret data.
- Adapters pass common behavior, error, cancellation, and payload-limit tests.

