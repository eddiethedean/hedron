---
status: shipped
---

# Utility component contracts

**Status:** Accepted

These built-ins capture the low-friction Python workflows learned from Streamlit while preserving normal FastAPI and component architecture.

- `Metric(label, value, delta=...)`: semantic value and change, not color-only meaning.
- `FileUpload(accept=..., maximum_size=...)`: typed upload integrated with forms, limits, CSRF, and application-owned storage. Enforce `maximum_size` in the route with `validate_upload_size` (markup alone is advisory).
- `DownloadButton(href=..., filename=...)` (alias `source=`): link to an authorized download route; pair with `safe_download_response` for path/auth/filename policy.
- `CodeViewer(code, language=...)`: escaped code with optional registered highlighting.
- `JSONViewer(value)`: bounded, escaped structured data with secret redaction.
- `Progress(value, maximum=...)` and `Status(...)`: accessible progress and state announcements.
- `Toast(...)`: non-blocking status message with appropriate live-region behavior.
- `Expander(...)` and `Tabs(...)`: semantic disclosure and tab patterns with keyboard behavior.
- `Sidebar(...)`: explicit complementary/navigation region.
- `Grid(columns=..., children=...)`: explicit responsive layout; it does not return positional mutable column handles.

All components have server-rendered useful fallbacks. Browser enhancement may preserve transient interaction state but cannot become an application-wide store. Uploads/downloads require explicit authorization and resource limits. Viewers never treat displayed content as executable.

