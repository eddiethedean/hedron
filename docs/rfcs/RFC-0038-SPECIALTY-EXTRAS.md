# RFC-0038: Specialty extras — terminal, robotics/IoT, native shell

**Status:** Accepted
**Phase:** 0.16 (`v0.16.0`) (Experimental maturity; not beachhead)
**Related:** [NiceGUI feature cross-check](../NICEGUI_FEATURE_CROSSCHECK.md)
(`ui.xterm`, joystick/scene, native mode, WebSerial/ROS2 examples);
RFC-0012, RFC-0014, RFC-0028; non-goals (no second UI runtime)

## Summary

Define **specialty**, opt-in extras for high-risk or niche NiceGUI-shaped capabilities: a bounded
`TerminalView`/PTY console, robotics/IoT helpers (joystick, device bridges), and an optional
native-desktop shell recipe over the ASGI app. These are not beachhead for CRUD/admin onboarding
and must not introduce a Vue/WebSocket outbox or weaken multi-worker safety.

## Motivation and background

NiceGUI’s examples (xterm, joystick, 3D scene, WebSerial, ROS2, native window) attract robotics
and lab tooling users. Hedron may serve that audience only behind explicit policy, audit, and
package isolation.

## Proposed design

- **`TerminalView` (optional extra):** command allowlists, authz, audit logs, output budgets,
  timeout/cancel, no implied root shell from markup; a11y limitations documented; distinct from
  0.16 job/log consoles. **Fails closed** without authenticated+authorized+audit policy.
- **Robotics/IoT extras:** virtual joystick and device-bridge recipes emitting typed action events
  at bounded rates.
- **Native desktop shell:** packaging recipe (e.g. pywebview + uvicorn) documented under
  deployment guidance; same HTML/HTMX app; not a second renderer or Supported multi-window model.
- All specialty extras disabled/absent by default; capability labels **Experimental**.

## Alternatives considered

1. **Reject all specialty surfaces permanently.** Possible, but leaves a documented audience gap.
2. **Port NiceGUI native + socket.io stack.** Deliberate non-parity.
3. **Ship TerminalView in core.** Rejected — command-injection blast radius.

## Security implications

Command injection, PTY escape, device access, and local-file exposure are primary threats.
Allowlists, authn/authz, audit, CSRF for mutating device commands, tenant isolation, and
fail-closed defaults are mandatory.

## Accessibility implications

Terminal and joystick UIs often fail WCAG; extras must document limitations and provide
non-pointer/command-form alternatives where claimed.

## Performance implications

Output rate limits; joystick event coalescing; single-device assumption documented for bridges.

## Testing strategy

Adversarial command suites; install isolation; packaging smoke for native recipe documented as
manual evidence when CI-infeasible.

## Compatibility and migration

Optional packages only. NiceGUI migration notes state non-parity for Vue scene/joystick runtimes.

## Resolved decisions

1. Specialty ships in 0.16 as **Experimental** with Verified fail-closed evidence (`SPECIALTY-016`).
2. PTY backend contract is local subprocess behind allowlist (remote executor deferred).
3. WebSerial/ROS2 remain external recipe forever in v1; DeviceBridge is the first-party bridge surface.

## Acceptance criteria

- No specialty extra installs with core; manifests and what’s-ready labels are accurate.
- TerminalView fails closed without allowlist/authz and has audit evidence.
- Native shell recipe does not claim a second UI runtime or single-worker-only correctness.
- Deliberate non-parity for Vue outbox / `run_javascript` restated in migration notes.
