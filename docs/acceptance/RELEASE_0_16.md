# Hedron `v0.16` curated extras and analysis workbenches acceptance

Phase 0.16 delivers an optional `hedron-extras` toolkit for specialized data-app
interactions and analysis workbenches — including CodeEditor, composition UI,
image tools, browser-Python sandbox, and Experimental specialty extras — without
expanding the core runtime or adopting Streamlit-style reruns or a Vue/WebSocket
client. Evidence is indexed by [`release-gate-0.16.toml`](release-gate-0.16.toml).
**Zero Deferred:** every 0.16-owned gate row must be Verified at cut.

## Spec packet

- [x] ROADMAP §0.16 scope accepted; Streamlit-extras and NiceGUI cross-checks refreshed.
- [x] RFC-0037 and RFC-0038 Accepted with locked decisions (CM6; Experimental specialty).
- [x] Entry gate: 0.15 evidence remains closed; 0.16 gate TOML owns Verified rows only.

## Package and testing

- [x] Optional `hedron-extras` + FeatureManifest + install isolation. *(`EXTRAS-PKG-016`)*
- [x] Workbench-flow AppScenario helpers and fixtures. *(`WORKBENCH-TEST-016`)*

## Surfaces

- [x] Composition UI (ChoiceCards, TreeView, Steps, Split, FAB, shortcuts). *(`COMPOSITION-016`)*
- [x] Analysis workbenches (DataExplorer, JSON/Code editors, ChartWorkbench, callable forms).
  *(`WORKBENCH-016`)*
- [x] Image compare/crop/region/annotations. *(`IMAGE-016`)*
- [x] Calendar / signature / typeahead extras. *(`EDITOR-EXTRAS-016`)*
- [x] Log console and presentation recipes. *(`DISPLAY-016`)*
- [x] Browser-Python sandbox. *(`SANDBOX-016`)*
- [x] Experimental TerminalView / joystick / device bridge (+ native-shell docs).
  *(`SPECIALTY-016`)*

## Packaging

- [x] Coordinated package verify (`scripts/verify_pkg_16.py`). *(`PKG-016`)*

## Exit

- [x] Full regression suite. *(`REGRESS-016`)*

**Exit met** as coordinated `0.16.0` (`v0.16.0`) when every gate row is Verified and the
release tag is cut (implemented pending cut).
