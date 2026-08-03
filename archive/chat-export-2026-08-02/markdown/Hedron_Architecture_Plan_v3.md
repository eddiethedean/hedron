# Hedron Architecture Plan (v3)

Vision: Hedron is a server-first, cross-language component platform built around a portable component specification, a JSX-inspired .hdn template language, and a Rust compiler.

## Product Philosophy

- Immediate productivity for beginners.

- Progressive disclosure of advanced concepts.

- One architecture from beginner to expert.

- React familiarity only where it naturally fits.

- HTML-first and language-neutral.

## Beginner Experience

- Users build applications without learning HDN.

- Import components directly from hedron.

- Subclass Hedron's own Props and Model classes.

- Built-in templates power standard components automatically.

## Example

from hedron import Props  
  
class UserCardProps(Props):  
name: str  
email: str  
  
\# Return Page(Card(Button(...))) from FastAPI.

## Progressive Learning

- Use built-in components.

- Configure props and slots.

- Compose components.

- Override templates with .hdn.

- Create custom browser components.

## Hedron Model System

- Pydantic is an internal implementation detail.

- Users import Props, Model and Field from hedron.

- Only portable Hedron-supported features are exposed.

- Models compile into the Hedron Component Specification.

## HDN

- JSX-inspired syntax.

- Lowercase tags = HTML.

- Uppercase tags = Hedron components.

- Hyphenated tags = Web Components.

- Separate contracts from templates.

## Rust Core

- Parser

- AST

- Specification validation

- Renderer

- Streaming SSR

- Code generation

## Runtime

- HTMX for server interaction.

- Web Components for rich client behavior.

- Hedron owns rendering.

## Roadmap

- Python MVP

- HDN compiler

- Java bindings

- Node bindings

- React migration toolkit

- Visual tooling

## Guiding Principle

Every advanced feature should be discoverable gradually. Beginners should never be forced to learn the compiler, HDN, or the specification before becoming productive.
