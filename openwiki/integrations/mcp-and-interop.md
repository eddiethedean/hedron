---
type: reference
title: MCP and Interoperability
description: Deny-by-default MCP resources, tools, transport bounds, and explicit catalog exposure.
tags:
  - mcp
  - interoperability
  - security
verified:
  - by: openwiki/0.5.2
    at: 2026-09-19T19:14:00.347Z
sources:
  - id: openwiki-source-ce4f1fb8920114c2073cb315
    resource: repo://packages/hedron-mcp/src/hedron_mcp/audit.py
  - id: openwiki-source-1b5ef32f79e0a4f970fe451d
    resource: repo://packages/hedron-mcp/src/hedron_mcp/bounds.py
  - id: openwiki-source-e4554433e7fede9a21a051b0
    resource: repo://packages/hedron-mcp/src/hedron_mcp/exposure.py
  - id: openwiki-source-18e031e8ac1884a00dc063eb
    resource: repo://packages/hedron-mcp/src/hedron_mcp/plugin.py
  - id: openwiki-source-03e1c1f6da236609af9b10a6
    resource: repo://packages/hedron-mcp/src/hedron_mcp/server.py
  - id: openwiki-source-dab0a6b2a5fc4192bef964e0
    resource: repo://packages/hedron-mcp/src/hedron_mcp/transport.py
  - id: openwiki-source-ed3a46fb491b70b1e6600bd1
    resource: repo://tests/security/test_mcp_adversarial.py
  - id: openwiki-source-e6566692c194f6d0eef178e2
    resource: repo://tests/unit/test_phase17_mcp.py
generated: { by: "codex", at: "2026-09-19T16:47:17.741Z" }
---

# MCP and Interoperability

The `hedron-mcp` package is an opt-in projection of Hedron capabilities into
the Model Context Protocol. Installing the package does not expose pages,
components, data, or actions. `McpProjection` starts disabled with empty
resource and tool listings, and `mount_mcp()` is a no-op until the application
explicitly enables the projection.

## Registration and catalog boundaries

Resources and tools are registered as typed `McpResource` and `McpTool`
objects. A resource has a canonical `hedron://` URI, metadata, an optional
reader, and an authorization hook. A tool has an input schema, a handler, an
explicit mutation flag, and an optional authorization hook. Catalog discovery
is informational: `consume_catalog()` returns logical IDs and records an audit
event, but it neither enables MCP nor registers an exposure.

`McpExposure` is the explicit bridge from a catalog entry or feature bundle to
the live projection. Applying it requires an enabled projection, a resource
reader or tool handler, and a live authorization callback. Duplicate names are
reported as feature conflicts. This prevents the presence of a package or
catalog entry from becoming ambient authority.

## Identity and authorization

The default principal resolver reads an authenticated session installed by the
host. It does not trust forgeable client headers such as `x-hedron-principal`
or `x-user`; applications can provide an explicit resolver when their host has
another identity mechanism. Every resource read and tool call requires a
principal. Scope claims cannot widen that principal, and optional authorization
and tenant hooks run after the identity check and must fail closed.

Resource URI validation permits only the documented `hedron` scheme. It
decodes percent-encoding repeatedly, rejects control characters, backslashes,
absolute paths, and traversal segments, and therefore does not provide an
arbitrary filesystem or remote-URL projection. Tool arguments are validated
against the advertised JSON Schema before the handler is invoked. Mutating
tools additionally require `allow_mutations=True`; the default keeps them out
of the supported ambient surface.

## Streamable HTTP bounds

`mount_mcp()` attaches the Streamable HTTP endpoint, normally at `/mcp`, only
for an enabled projection. The transport bounds request bodies, concurrent
work, per-principal request rates, deadlines, cancel marks, and sessions using
`McpBounds` (defaults include 64 KiB requests, eight concurrent operations,
120 requests per minute, and bounded session/cancel registries). Browser-origin
requests fail closed unless an allowlist is configured. Server-minted session
IDs are bound to the authenticated principal; a later principal switch is
rejected, and cancellation ownership is scoped to the session or principal.

Structured `McpAuditLog` events are redacted for common secret keys and token
patterns. The default sink is process-local; multi-worker deployments need an
external sink or shared lifecycle store when they require cross-worker audit or
authority coordination.

The adversarial and phase tests exercise confused-deputy prevention, tenant
boundaries, URI traversal and scheme rejection, origin policy, non-finite JSON,
mutation gating, session identity, and the disabled/empty default. See
[Security and Request Boundaries](../security/request-boundaries.md) for the
broader request policy and [Extension Surfaces](../packages/extension-surfaces.md)
for the package integration model.
