# Hedron Architecture Plan v7

Updated with dual FastAPI integration modes.

## Core Vision

- Python-first, server-first framework.

- FastAPI is the flagship integration.

- Framework-neutral core with Flask and Django adapters.

- Progressive disclosure from beginner to expert.

## Packaging

- hedron → batteries-included FastAPI distribution

- hedron-core → shared engine

- hedron-flask → Flask integration

- hedron-django → Django integration

## Model System

- Public API exposes Props, Model, FormModel, and Field.

- Pydantic is an internal implementation detail.

- Only portable Hedron-supported features are available.

## HDN

- Advanced customization layer.

- JSX-inspired without React runtime semantics.

- Used only when built-in components are insufficient.

## Components as HTTP Resources

- Addressable components expose HTTP resources.

- Developers reference components rather than HTMX URLs.

- Supports refresh, polling, lazy loading, bookmarking, and isolated testing.

## FastAPI Integration

Hedron supports two integration levels.

### 1. Hedron Application (recommended)

Applications built with Hedron() automatically recognize component return values.

app = Hedron()  
  
@app.get("/users/{id}")  
def user(id: int) -\> UserCard:  
return UserCard(user=get_user(id))

Returned components are automatically rendered into HTML responses. Return annotations become HTML contracts, analogous to FastAPI response models for JSON.

### 2. Existing FastAPI Applications

Developers using an unmodified FastAPI() application explicitly wrap component responses.

app = FastAPI()  
  
@app.get("/users/{id}")  
def user(id: int):  
return HTML(  
UserCard(user=get_user(id))  
)

This avoids changing FastAPI's normal response behavior while still allowing Hedron components to be adopted incrementally.

## Guiding Principle

Hedron should feel like a natural extension of FastAPI. JSON endpoints return models. HTML endpoints return components. When using Hedron(), component rendering is automatic. When using plain FastAPI(), rendering is explicit through Hedron's HTML response wrapper.
