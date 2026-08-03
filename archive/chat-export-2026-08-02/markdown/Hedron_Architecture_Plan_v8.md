# Hedron Architecture Plan v8

Comprehensive architecture and product vision emphasizing a Python-first, FastAPI-first experience with progressive disclosure and HTMX-native components.

## Core Principles

- Beginner-first with progressive disclosure.

- FastAPI is the flagship experience.

- Framework-neutral core with Flask and Django adapters.

- HTML-first, server-first.

- Components are the primary abstraction.

- Framework mechanics should be inferred when intent is explicit.

## Packaging

- hedron -\> batteries-included FastAPI distribution.

- hedron-core -\> framework-neutral engine.

- hedron-flask -\> Flask integration.

- hedron-django -\> Django integration.

## Model System

- Users import Props, Model, FormModel and Field from Hedron.

- Pydantic remains an implementation detail.

- Restricted portable feature set with early validation.

## Learning Path

- 1\. Built-in components.

- 2\. Props, slots and themes.

- 3\. Component composition.

- 4\. HDN templates.

- 5\. Browser components and advanced integrations.

## HDN

- Advanced customization layer.

- JSX-inspired without React runtime semantics.

- Lowercase tags = HTML.

- Uppercase tags = Hedron components.

- Hyphenated tags = Web Components.

## Components as HTTP Resources

- Addressable components automatically expose HTTP resources.

- Developers reference components rather than HTMX URLs.

- Supports refresh, polling, lazy loading, bookmarking and isolated testing.

- Separate Renderable Components and Addressable Components.

## FastAPI Integration

Hedron provides two integration modes. Hedron() automatically renders returned components into HTML. Existing FastAPI applications explicitly wrap components using Hedron's HTML response helper.

app = Hedron()  
  
@app.get("/users/{id}")  
def user(id:int) -\> UserCard:  
return UserCard(user=get_user(id))

app = FastAPI()  
  
@app.get("/users/{id}")  
def user(id:int):  
return HTML(UserCard(user=get_user(id)))

## Automatic Behaviors

- Automatic full-page vs HTMX fragment rendering.

- Return annotations become HTML contracts.

- Automatic registration of addressable components.

- Component references instead of endpoint strings.

- Self-refreshing components.

- Stable generated component identities.

- Sensible HTMX defaults.

- Typed actions instead of manual URLs.

- Automatic forms from FormModel.

- Automatic validation-error rendering.

- Automatic loading and skeleton states.

- Layout inference.

- Automatic page metadata.

- Automatic static asset serving.

- Development component explorer.

- Component-aware error pages.

- Convention-based project discovery.

- FastAPI dependency injection for addressable components.

- Component-local folder conventions.

- Component-aware testing helpers.

## Future Roadmap

- React migration toolkit.

- Optional Rust acceleration only after profiling demonstrates value.

- Cross-language support after Python API stabilizes.

- Visual component studio.

## Guiding Philosophy

JSON endpoints return models. HTML endpoints return components. Hedron should feel like a natural extension of FastAPI while remaining portable to Flask and Django through dedicated adapters. Beginners should become productive without learning HDN, while advanced users can progressively unlock deeper customization.
