# RFC-0034: Authenticated downloads and ranged media delivery

**Status:** Draft
**Phase:** 0.15 (`v0.15.0`)
**Related:** [NiceGUI feature cross-check](../NICEGUI_FEATURE_CROSSCHECK.md)
(`ui.download`, `app.add_media_files`); RFC-0012, RFC-0021, RFC-0028; roadmap Audio/Video/PdfViewer

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

## Open questions

1. Should download-all archives be core or extras?
2. Unified API across FastAPI/`hedron-flask`/`hedron-django` in 0.15 or FastAPI-first?
3. Signed short-lived URLs vs session-cookie auth for media — which is Supported default?

## Acceptance criteria

- Audio/Video/PdfViewer demos use authorized Range or documented fallback.
- Unauthorized and traversal cases fail closed in the 0.15 gate.
- NiceGUI migration notes map `ui.download` / ranged media to these helpers.
