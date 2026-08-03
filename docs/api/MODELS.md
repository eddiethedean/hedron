# `Model`, `Props`, `FormModel`, and `EventPayload`

**Status:** Proposed

Hedron exposes purpose-specific model bases backed initially by Pydantic.

```python
from hedron import Field, FormModel, Model, Props

class User(Model):
    id: int
    name: str

class UserCardProps(Props):
    user: User
    compact: bool = False

class CreateUser(FormModel):
    name: str = Field(min_length=1)
```

## Roles

- `Model`: portable domain data used by UI contracts.
- `Props`: component construction input; never automatically exposed as HTTP input.
- `FormModel`: client-submitted form or action input with field presentation metadata.
- `EventPayload`: typed custom-event data crossing a browser/server boundary.

The supported baseline includes primitives, enums, literals, optionals, lists, string-keyed mappings, nested Hedron models, date/URL-like Hedron types, and component-node types where declared. Extra fields are forbidden by default.

Arbitrary objects, callbacks as props, framework request objects, unrestricted serializers, and uninspectable validators fail at class definition. Pydantic-specific configuration is not part of the portable public contract.

