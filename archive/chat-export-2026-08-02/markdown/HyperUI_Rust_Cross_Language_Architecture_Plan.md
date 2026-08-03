# HyperUI Architecture Plan

**Vision  **
Build a Rust-first, server-driven UI framework with thin language-native adapters for Python, Java, and Node.js. The framework provides React-like component composition while producing standards-based HTML, HTMX markup, and Web Component integration without requiring a JavaScript build system.

## Goals

- Single Rust rendering engine shared by all language bindings.

- Idiomatic APIs for Python, Java/Kotlin, and TypeScript.

- Native HTMX support as a first-class feature.

- Web Components for rich interactive widgets.

- Zero Node.js requirement for Python users.

- Deterministic HTML rendering and strong type safety.

## Architecture

- Core crates: hyperui-core, hyperui-html, hyperui-htmx, hyperui-components, hyperui-schema.

- Bindings: PyO3, JNI, napi-rs.

- Language adapters convert native objects into the shared Rust component tree.

## Component Model

- Element, Text, Fragment, RawHtml node types.

- Typed attributes with validation.

- Deterministic rendering and escaping.

- Streaming renderer as a future optimization.

## Web Components Strategy

- Render custom elements from Rust like any HTML element.

- Use light DOM by default for HTMX compatibility.

- Use Shadow DOM only for isolated widgets.

- Communicate with HTMX using CustomEvents.

## Schema & Code Generation

- Describe components in YAML.

- Generate Rust, Python, Java, TypeScript wrappers and documentation.

- Single source of truth for component APIs.

## Repository Layout

- crates/hyperui-core

- crates/hyperui-html

- crates/hyperui-htmx

- crates/hyperui-components

- crates/hyperui-schema

- bindings/python

- bindings/java

- bindings/node

- examples/

- docs/

## Roadmap

- Phase 1: Rust renderer and HTML/HTMX primitives.

- Phase 2: Python/FastAPI integration.

- Phase 3: Component schema and code generation.

- Phase 4: Java/Spring support.

- Phase 5: Node/Express support.

- Phase 6: Rich Web Component library (data grid, tree, charts, Monaco wrapper, ontology graph).

## Testing Strategy

- Snapshot rendering tests.

- Cross-language conformance suite.

- Property-based HTML escaping tests.

- Benchmarks and integration tests.

## Future Opportunities

- Streaming SSR.

- Static site generation.

- Design-system tooling.

- Visual component inspector.

- Hot reload for Python.

- Accessibility auditing.

- Incremental DOM diffing.
