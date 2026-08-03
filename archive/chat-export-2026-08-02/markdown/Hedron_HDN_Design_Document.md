# Hedron Design Proposal: The .hdn Template Language

Status: Draft RFC  
  
This document defines the philosophy, syntax, and design goals of the Hedron template language (.hdn). The language is intended to provide a familiar, component-oriented authoring experience for server-rendered applications while remaining language-neutral and independent of JavaScript runtimes.

## 1. Goals

- Feel immediately familiar to developers with React/JSX experience.

- Remain valid HTML-first wherever practical.

- Compile to efficient server-side render programs.

- Be portable across Python, Java, Node.js and future languages.

- Avoid dependence on JavaScript execution.

## 2. Philosophy

HDN intentionally borrows ideas from JSX only where they naturally fit Hedron's server-first architecture. The goal is familiarity, not imitation.

## 3. Core Principles

- Semantic clarity over React compatibility.

- Component composition is a first-class concept.

- HTML is the foundation.

- Templates are declarative.

- Contracts and templates are separate concerns.

- The compiler performs validation before rendering.

## 4. Component Model

> Python:  
> class UserCardProps(BaseModel):  
> name: str  
> email: str  
>   
> Template (UserCard.hdn):  
>   
> \<Card\>  
> \<h2\>{props.name}\</h2\>  
> \<p\>{props.email}\</p\>  
> \</Card\>

## 5. Tag Semantics

- lowercase tags represent native HTML.

- Uppercase tags represent Hedron components.

- Hyphenated tags represent Web Components.

## 6. Expressions

> Supported:  
> {props.name}  
> {props.loading ? \<Spinner /\> : \<Content /\>}  
> {props.show && \<Panel /\>}  
>   
> Expressions are intentionally restricted to a portable subset suitable for compilation.

## 7. Children

> \<Card\>  
> \<Button\>Save\</Button\>  
> \</Card\>  
>   
> Inside Card:  
> \<section class="card"\>  
> {children}  
> \</section\>

## 8. What HDN Intentionally Does NOT Copy from React

- Hooks

- Client-side state management

- Virtual DOM

- Hydration assumptions

- Synthetic events

- JavaScript callback props

## 9. HTMX Integration

- HTMX attributes are first-class HTML attributes.

- Server actions should compile naturally to HTMX.

- No JavaScript build pipeline required.

## 10. Web Components

- Hyphenated elements are preserved.

- HDN configures Web Components declaratively.

- Rich browser behavior belongs inside the Web Component.

## 11. Compilation Pipeline

- Pydantic contract

- .hdn template

- AST generation

- Validation

- Optimization

- Rust renderer

- HTML output

## 12. Design Rule

Adopt React conventions only where they naturally express Hedron's architecture. Never introduce syntax solely for React compatibility.

## 13. Future Work

- Template language grammar

- Expression language specification

- Formatting rules

- Language server

- Syntax highlighting

- Compiler diagnostics
