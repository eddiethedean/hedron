# RFC-0034: Authenticated downloads and ranged media delivery

**Status:** Implemented
**Phase:** 0.15 (`v0.15.0`)
**Related:** [NiceGUI feature cross-check](../NICEGUI_FEATURE_CROSSCHECK.md)

## Summary

Define typed download helpers and authorized HTTP Range/streaming responses for media players,
PDF, and file delivery so 0.15 media components have a secure, multi-worker-safe delivery path —
inspired by NiceGUI’s download and ranged media helpers, without implying a global media CDN.

## Motivation and background

`Audio`, `Video`, and `PdfViewer` require Range requests, correct `Content-Disposition`, size/type
limits, and authorization. NiceGUI exposes `ui.download` and ranged `add_media_files`; Hedron needs
the same outcomes over ordinary FastAPI/Flask/Django responses and host auth.

## Proposed design

- Typed helpers (names TBD): e.g. `FileDownload`, `media_file_response`, or router utilities that
  set disposition, content type, cache policy, and authz checks.
- Range (`bytes`) support for eligible media with 206/416 semantics, bounded concurrent ranges, and
  explicit rejection when the backing store cannot satisfy Range safely.
- Gallery `download` / `download-all` compose the same helpers; zip/archive bundling is optional and
  budgeted.
- Responses remain ordinary HTTP; no long-lived Python-held file handles across workers without a
  durable store.
- Private/authenticated cache defaults align with existing security profiles.

## Alternatives considered

1. **Static mount only.** Insufficient for per-principal authz and disposition control.
2. **NiceGUI-style in-process media registry keyed by client connection.** Rejected — single-worker
   coupling.
3. **Always full-file download (no Range).** Rejected for Video/Audio UX; keep as fallback when
   Range is unsupported.

## Security implications

Authorization before bytes; path traversal and symlink checks; content-type sniffing policy;
disposition filename sanitization; no open redirects; rate/size limits; secret redaction in
diagnostics; CSRF irrelevant for safe GET downloads but unsafe upload/delete remain protected.

## Accessibility implications

Download controls need accessible names; players that depend on Range must degrade to full download
or documented limitation without silent failure.

## Performance implications

Streaming vs buffering budgets; max file size; Range amplification limits; observability for 416
and partial-content rates.

## Testing strategy

Unit (Range parsing, disposition), integration (authz allow/deny, 206/416), browser (Video/Audio
seek where applicable), adversarial (traversal, huge ranges, content-type confusion), adapter notes
for Flask/Django.

## Compatibility and migration

Additive APIs. Existing `DownloadButton`/file responses gain documented composition paths; breaking
changes require COMPATIBILITY entries.

## Accepted decisions (0.15)

1. **Download-all archives:** optional, budgeted helpers in the same FastAPI response module (not a
   separate extras package for v1).
2. **Host adapters:** FastAPI is the Supported path in 0.15; Flask/Django receive documented
   composition notes without requiring identical helper APIs on day one.
3. **Auth default:** session-cookie + existing authz hooks; signed short-lived URLs remain an
   application recipe, not the Supported default.

## Acceptance criteria

- Audio/Video/PdfViewer demos use authorized Range or documented fallback.
- Unauthorized and traversal cases fail closed in the 0.15 gate.
- NiceGUI migration notes map `ui.download` / ranged media to these helpers.
