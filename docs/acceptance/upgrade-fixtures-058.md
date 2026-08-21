# Upgrade fixtures for phase 0.58

**Source:** Published/Verified in-tree `v0.57.0`  
**Target:** `v0.58.0`  
**Authority:** D-101 / D-102 / RFC-0085

Existing pages, commands, FormBody, handles, effects, features, DataWorkspace overrides, jobs,
auth, uploads, and presentation retain behavior. No app is opted into a facade or rewritten.
`FeatureOverrides` and surface source maps are additive. Flask/Django gain no false decorator
parity, and feature inclusion never implies MCP, Gradio, browser, or other protocol exposure.

Fixtures compare explicit and facade forms for page/screen, command/form_command, DataWorkspace,
JobBackend/Poll/TaskFlow, typed dashboard filters, session/upload helpers, and whole/per-surface
ejection. Optional-package absence must preserve clean imports, startup, explanation, and explicit
APIs.
