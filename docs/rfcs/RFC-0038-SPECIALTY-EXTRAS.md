# RFC-0038: Specialty extras — terminal, robotics/IoT, native shell

**Status:** Draft
**Phase:** 0.16 (`v0.16.0`) (audience-gated; may slip)
**Related:** [NiceGUI feature cross-check](../NICEGUI_FEATURE_CROSSCHECK.md)
(`ui.xterm`, joystick/scene, native mode, WebSerial/ROS2 examples);
RFC-0012, RFC-0014, RFC-0028; non-goals (no second UI runtime)

## Summary

Define **specialty**, opt-in extras for high-risk or niche NiceGUI-shaped capabilities: a bounded
`TerminalView`/PTY console, robotics/IoT helpers (joystick, deep 3D scene controls, device
bridges), and an optional native-desktop shell recipe over the ASGI app. These are not beachhead
for CRUD/admin onboarding and must not introduce a Vue/WebSocket outbox or weaken multi-worker
safety.

## Motivation and background

NiceGUI’s examples (xterm, joystick, 3D scene, WebSerial, ROS2, native window) attract robotics
and lab tooling users. Hedron may serve that audience only behind explicit policy, audit, and
package isolation — default disposition remains recipe/plugin until evidence justifies Supported
extras.

## Proposed design

- **`TerminalView` (optional extra):** command allowlists, authz, audit logs, output budgets,
  timeout/cancel, no implied root shell from markup; a11y limitations documented; distinct from
  0.16 job/log consoles.
- **Robotics/IoT extras:** virtual joystick and device-bridge recipes emitting typed action events
  at bounded rates; deep Three.js scene controls only as extras reusing 0.16 3D model adapters —
  not a NiceGUI `ui.scene` clone in core.
- **Native desktop shell:** packaging recipe (e.g. pywebview + uvicorn) documented under
  deployment guidance; same HTML/HTMX app; not a second renderer or Supported multi-window model.
- All specialty extras disabled/absent by default; capability labels honest (Experimental vs
  Supported).

## Alternatives considered

1. **Reject all specialty surfaces permanently.** Possible, but leaves a documented audience gap;
   this RFC keeps an explicit path.
2. **Port NiceGUI native + socket.io stack.** Deliberate non-parity.
3. **Ship TerminalView in core.** Rejected — command-injection blast radius.

## Security implications

Command injection, PTY escape, device access, and local-file exposure are primary threats.
Allowlists, authn/authz, audit, CSRF for mutating device commands, tenant isolation, and
fail-closed defaults are mandatory. Native shell must not relax CSP or auto-enable DevTools
escape hatches in production recipes.

## Accessibility implications

Terminal and joystick UIs often fail WCAG; extras must document limitations and provide
non-pointer/command-form alternatives where claimed. Native window recipes inherit web a11y
obligations.

## Performance implications

Output rate limits; joystick event coalescing; scene polygon/asset budgets; single-device
assumption documented for bridges.

## Testing strategy

Adversarial command suites; install isolation; explicit “not covered by default a11y gate”
labeling unless alternatives exist; packaging smoke for native recipe on one reference OS
(non-blocking if CI-infeasible — document manual evidence).

## Compatibility and migration

Optional packages only. NiceGUI migration notes state non-parity for Vue scene/joystick runtimes
and map outcomes to these extras/recipes.

## Open questions

1. Is any specialty extra in the 0.16 exit gate, or explicitly Deferred with roadmap owners?
2. PTY backend: local subprocess only vs remote executor interface?
3. WebSerial/ROS2: first-party extra vs external recipe forever?

## Acceptance criteria

- No specialty extra installs with core; manifests and what’s-ready labels are accurate.
- TerminalView (if shipped) fails closed without allowlist/authz and has audit evidence.
- Native shell recipe does not claim a second UI runtime or single-worker-only correctness.
- Deliberate non-parity for Vue outbox / `run_javascript` restated in migration notes.
