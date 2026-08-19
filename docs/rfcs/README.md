# Hedron RFCs

RFCs define what Hedron is building and why. Implementation specifications define how accepted RFCs are built.

## Status lifecycle

`Draft` → `Proposed` → `Accepted` → `Implemented` → `Deprecated` or `Superseded`

An RFC may be rejected without entering the implementation. Material changes to an Accepted RFC require a decision-log entry and a superseding RFC or revision.

`Accepted` selects a design; it does not mean the feature is implemented. The roadmap phase and acceptance suite determine when that design becomes available.

## Required review areas

New RFCs and material revisions must address public behavior, alternatives, security, accessibility, performance, testing, compatibility, migration, open questions, and acceptance criteria. “Not applicable” must include a reason. The phase 0.0 bootstrap RFC set records its compact design in the RFCs and supplies cross-cutting review through [traceability](https://github.com/eddiethedean/hedron/blob/main/docs/TRACEABILITY.md), the linked implementation specifications, and the acceptance-suite specifications; revisions use the full [template](TEMPLATE.md).

## Index

| RFC | Title | Status |
|---|---|---|
| [0001](RFC-0001-VISION.md) | Vision | Accepted |
| [0002](RFC-0002-CORE-ARCHITECTURE.md) | Core architecture | Accepted |
| [0003](RFC-0003-COMPONENT-MODEL.md) | Component model | Accepted |
| [0004](RFC-0004-FASTAPI-INTEGRATION.md) | FastAPI integration | Accepted |
| [0005](RFC-0005-HDN-LANGUAGE.md) | HDN language (removed in 0.9) | Historical |
| [0006](RFC-0006-SCOPED-STYLES.md) | Scoped styles | Accepted |
| [0007](RFC-0007-COMPONENT-EXPLORER.md) | Component Explorer | Accepted |
| [0008](RFC-0008-ADDRESSABLE-COMPONENTS.md) | Addressable components | Accepted |
| [0009](RFC-0009-HTMX-INTEGRATION.md) | HTMX integration | Accepted |
| [0010](RFC-0010-DATA-COMPONENTS.md) | Data components | Accepted |
| [0011](RFC-0011-VISUALIZATION.md) | Visualization | Accepted |
| [0012](RFC-0012-SECURITY.md) | Security | Accepted |
| [0013](RFC-0013-ASYNC.md) | Async architecture | Accepted |
| [0014](RFC-0014-PLUGIN-ARCHITECTURE.md) | Plugin architecture | Accepted |
| [0015](RFC-0015-ROUTING.md) | Routing | Accepted |
| [0016](RFC-0016-OPENAPI.md) | OpenAPI | Accepted |
| [0017](RFC-0017-CLI.md) | CLI | Accepted |
| [0018](RFC-0018-PACKAGING.md) | Packaging | Accepted |
| [0019](RFC-0019-TESTING.md) | Testing | Accepted |
| [0020](RFC-0020-PERFORMANCE.md) | Performance | Accepted |
| [0021](RFC-0021-BROWSER-RUNTIME.md) | Browser runtime | Accepted |
| [0022](RFC-0022-THEMING.md) | Theming | Accepted |
| [0023](RFC-0023-ACCESSIBILITY.md) | Accessibility | Accepted |
| [0024](RFC-0024-DEVELOPER-EXPERIENCE.md) | Developer experience | Accepted |
| [0025](RFC-0025-COMPONENT-LIFECYCLE.md) | Component lifecycle | Accepted |
| [0026](RFC-0026-STATE-MANAGEMENT.md) | State management | Accepted |
| [0027](RFC-0027-DATA-SOURCES.md) | Data sources | Accepted |
| [0028](RFC-0028-DEPLOYMENT.md) | Deployment | Accepted |
| [0029](RFC-0029-ROADMAP-TO-1.0.md) | Capability roadmap | Accepted |
| [0030](RFC-0030-DECLARATIVE-AUTHORING-RESET.md) | Declarative authoring reset | Superseded |
| [0031](RFC-0031-JINJA-INTEGRATION.md) | Explicit `.hdj` format, standards-first authoring, and immediate HDN replacement | Implementing |
| [0032](RFC-0032-LIVE-TRANSPORT.md) | Live transport, focused streaming, and navigation preload | Accepted |
| [0033](RFC-0033-MAP-GEOJSON.md) | Map and GeoJSON presentation | Implemented |
| [0034](RFC-0034-MEDIA-DOWNLOAD-RANGE.md) | Authenticated downloads and ranged media delivery | Implemented |
| [0035](RFC-0035-SURFACE-CHROME.md) | Surface chrome — carousel, timeline, context menu, chips, progress | Implemented |
| [0036](RFC-0036-SCENARIO-MARKS.md) | AppScenario identity marks and filter asserts | Implemented |
| [0037](RFC-0037-CODE-EDITOR-EXTRAS.md) | CodeEditor and interactive extras | Implemented |
| [0038](RFC-0038-SPECIALTY-EXTRAS.md) | Specialty extras — terminal, robotics/IoT, native shell | Implemented |
| [0039](RFC-0039-INTERACTION-ERGONOMICS.md) | Interaction authoring ergonomics (`region`, `swap`, diagnostics) | Implemented |
| [0040](RFC-0040-INTERACTION-GRAPH.md) | Dashboard interaction graph and TriggerContext | Implemented |
| [0041](RFC-0041-PROPERTY-COLLECTION-PATCH.md) | PropertyPatch, CollectionPatch, and structured collections | Implemented |
| [0042](RFC-0042-NOTEBOOK-PREVIEW.md) | Server-side notebook preview (`hedron-notebook`) | Implemented |
| [0043](RFC-0043-MCP-PROJECTION.md) | Optional MCP projection (`hedron-mcp`) | Implemented |
| [0044](RFC-0044-SHELL-INTERACTION-RESULT.md) | HTMX shell primitives and public InteractionResult rendering | Implemented |
| [0045](RFC-0045-INFERENCE-INTERFACE.md) | InferenceInterface and ModelDemo | Accepted |
| [0046](RFC-0046-MODEL-DEMO-PRESENTATION.md) | Model-demo presentation and PredictionFeedback | Accepted |
| [0047](RFC-0047-INFERENCE-POLICY.md) | InferencePolicy over JobBackend | Accepted |
| [0048](RFC-0048-INTERACTION-RECORDER.md) | Redacted interaction and API recorder | Accepted |
| [0049](RFC-0049-GRADIO-ADAPTER.md) | Optional hedron-gradio protocol adapter | Accepted |
| [0050](RFC-0050-INFERENCE-WORKFLOW.md) | Versioned permissioned inference workflows | Accepted |
| [0051](RFC-0051-ACCESSIBILITY-CONTRACT.md) | AccessibilityContract schema and catalog | Accepted |
| [0052](RFC-0052-A11Y-EXPLORER-SCENARIO.md) | Explorer a11y workspace and AccessibilityScenario | Accepted |
| [0053](RFC-0053-PROGRESSIVE-ENHANCEMENT.md) | Progressive enhancement, landmarks, Page scripts | Accepted |
| [0054](RFC-0054-ATAG-AUTHORING.md) | ATAG-oriented authoring assistance | Accepted |
| [0055](RFC-0055-A11Y-GOVERNANCE.md) | A11y evidence governance and AT matrix | Accepted |
| [0056](RFC-0056-PRODUCTION-QUALITY.md) | Production-quality maturity program | Accepted |
| [0057](RFC-0057-PRODUCTION-GRADE-CORE.md) | Production-grade core, FastAPI flagship, and Explorer | Accepted |
| [0058](RFC-0058-PRODUCTION-GRADE-SATELLITES.md) | Production-grade adapters, data, HDJ, and curated extras | Accepted |
| [0059](RFC-0059-PRODUCTION-GRADE-CHARTS-NATIVE.md) | Production-grade charts and optional native acceleration | Accepted |
| [0060](RFC-0060-WEB-COMPONENT-PLATFORM.md) | Web Component platform program | Accepted |
| [0061](RFC-0061-STREAMLIT-AST-MIGRATOR.md) | Reviewable Streamlit AST migration assistant | Proposed |
| [0062](RFC-0062-POSIT-WORKBENCH-ADAPTER.md) | Production-grade Posit Workbench deployment adapter | Accepted |
| [0063](RFC-0063-FASTAPI-WORKBENCH-EXTRACTION.md) | Standalone FastAPI Workbench extraction | Accepted |
| [0064](RFC-0064-PRODUCTION-GRADE-TOOLING.md) | Production-grade developer and portable conformance tooling | Accepted |
| [0065](RFC-0065-PRODUCTION-GRADE-MCP.md) | Production-grade deny-by-default MCP projection | Accepted |
| [0066](RFC-0066-HEDRON-POSIT.md) | Unified `hedron-posit` Workbench and Connect deployment adapter | Accepted |
| [0067](RFC-0067-PRODUCTION-GRADE-GRADIO.md) | Production-grade Gradio client interoperability | Accepted |
| [0068](RFC-0068-WHOLE-FLEET-CLOSURE.md) | Whole-fleet production-grade closure | Accepted |
| [0069](RFC-0069-HIGH-FIDELITY-CHARTS.md) | High-fidelity declarative charts | Accepted |
| [0070](RFC-0070-REFRESHABLE-VIEWS.md) | Refreshable views, commands, and typed updates | Accepted |
| [0071](RFC-0071-TYPE-DRIVEN-AUTHORING.md) | Type-driven authoring and schema-derived interactions | Accepted |
| [0072](RFC-0072-TYPED-INTERACTION-ECOSYSTEM.md) | Typed interaction ecosystem convergence | Accepted |
| [0073](RFC-0073-PACKAGE-NATIVE-WORKFLOWS.md) | Package-native typed workflows | Accepted |
| [0074](RFC-0074-FIRST-CLASS-MAPS.md) | First-class maps and offline geospatial presentation | Accepted |
| [0075](RFC-0075-HTMX-EXTENSION-INTEGRATION.md) | First-class HTMX extension integration | Accepted |
| [0076](RFC-0076-FASTAPI-PYDANTIC-CONVERGENCE.md) | FastAPI and Pydantic convergence | Accepted (D-081; Stage 0 refined by D-084; [#380](https://github.com/eddiethedean/hedron/issues/380)) |
| [0077](RFC-0077-EXPLORER-ARCHITECTURE.md) | Explorer architecture and operator-grade development tooling | Accepted (D-085; Stage 1 shipped in-tree `v0.50.0`; D-086; [#501](https://github.com/eddiethedean/hedron/issues/501) stays open until publish assets) |
| [0078](RFC-0078-CURATED-EXTRAS-LIFECYCLE.md) | Curated extras depth and lifecycle closure | Accepted (D-087; D-088; Stage 1 in-tree `v0.51.0`; [#507](https://github.com/eddiethedean/hedron/issues/507) stays open until publish assets; companion [#504](https://github.com/eddiethedean/hedron/issues/504)–[#506](https://github.com/eddiethedean/hedron/issues/506)) |
