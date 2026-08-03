# Hedron Architecture & Vision

Hedron is a cross-language, server-driven component platform centered on a canonical component specification, a JSX-like .hdn template language, and a Rust compiler/runtime.

## Vision

- Component platform, not just a UI framework.

- Server-first.

- Standards-based HTML.

- No Node.js requirement.

- Cross-language from day one.

## Core Architecture

- Contracts: Pydantic (or equivalent) models define component APIs.

- Templates: .hdn files provide JSX-like authoring.

- Rust compiler validates and renders.

- HTMX handles server interactions.

- Web Components provide rich client widgets.

## Component Specification

- Language-neutral schema.

- Generated from Pydantic in Python.

- Future Java/Kotlin/TypeScript authoring.

- Drives documentation, code generation, validation and rendering.

## Template Language (.hdn)

- Native HTML syntax.

- Uppercase = Hedron component.

- lowercase = HTML.

- hyphenated = Web Component.

- Expressions, loops, conditionals, slots and safe HTML escaping.

## Rust Core

- Renderer

- Compiler

- AST

- Specification validation

- Streaming SSR

- Code generation

## Language Bindings

- PyO3

- JNI

- napi-rs

- Idiomatic APIs with identical rendering semantics

## Repository

- hedron-spec

- hedron-compiler

- hedron-render

- hedron-python

- hedron-java

- hedron-node

- hedron-cli

- hedron-webcomponents

## Roadmap

- MVP: Rust renderer + Python + FastAPI + HTMX

- .hdn compiler

- Specification-driven code generation

- Java support

- Node support

- Visual tooling

## Mission

- Deliver React-level component ergonomics without requiring a JavaScript build toolchain.

## Example Workflow

1\. Define props with Pydantic.  
2. Author component markup in a .hdn template.  
3. Compile to the Hedron specification.  
4. Rust validates and emits optimized render instructions.  
5. FastAPI (or another backend) renders HTML enhanced by HTMX and Web Components.
