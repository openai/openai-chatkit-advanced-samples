# Widget Implementation Guide for ChatKit

This guide documents the patterns and techniques learned while implementing ProfileCard widgets with interactive buttons in the Cupid matchmaking game.

## Table of Contents
1. [Overview](#overview)
2. [Widget Architecture](#widget-architecture)
3. [Step-by-Step Implementation](#step-by-step-implementation)
4. [Widget Action Handlers](#widget-action-handlers)
5. [Common Patterns](#common-patterns)
6. [Troubleshooting](#troubleshooting)

---

## Overview

ChatKit widgets are interactive UI components that can be embedded in chat conversations. They consist of:
- A `.widget` JSON file containing the template, schema, and preview
- A builder function that renders the template with data
- Server-side handlers for interactive actions (button clicks, etc.)

## Widget Architecture

### Components

```
apps/cupid-simple/
├── backend/
│   ├── app/
│   │   ├── server.py                    # Server with action() and respond() methods
│   │   ├── widgets/
│   │   │   ├── widget_template.py       # WidgetTemplate utility class
│   │   │   └── profilecard_widget.py    # ProfileCard builder
│   │   └── data/
│   │       ├── mortal.yaml              # Character data
│   │       └── match.yaml
│   └── pyproject.toml                   # Dependencies (jinja2)
└── specs/
    └── cupid-simple/
        └── widgets/
            └── ProfileCard00.widget     # Widget definition
```

### Key Files

**ProfileCard00.widget** - Widget definition with:
- `template`: Jinja2 template string (JSON structure)
- `jsonSchema`: Schema for data validation
- `outputJsonPreview`: Example output for testing

**widget_template.py** - Utility for loading and rendering widgets:
```python
class WidgetTemplate:
    def __init__(self, definition: dict[str, Any])
    def from_file(cls, file_path: str) -> "WidgetTemplate"
    def build(self, data: dict[str, Any] | T | None = None) -> WidgetRoot
```

**profilecard_widget.py** - Builder function:
```python
def build_profilecard_widget(character_data: dict[str, Any]) -> WidgetRoot
```

---

## Step-by-Step Implementation

### 1. Add jinja2 Dependency

**File:** `backend/pyproject.toml`

```toml
dependencies = [
    "fastapi>=0.114.1,<0.116",
    "uvicorn[standard]>=0.36,<0.37",
    "openai>=1.40",
    "openai-chatkit>=1.1.2,<2",
    "pyyaml>=6.0",
    "jinja2>=3.1",  # Add this line
]
```

Run: `uv sync` to install the dependency.

### 2. Create Widget Template Utility

**File:** `backend/app/widgets/widget_template.py`

```python
"""Utility for loading and building widgets from .widget files."""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any, TypeVar

from chatkit.widgets import WidgetRoot
from jinja2 import Environment
from pydantic import BaseModel, TypeAdapter

T = TypeVar("T", bound=BaseModel)

# Jinja2 environment for rendering templates
env = Environment(autoescape=False, enable_async=False)


class WidgetTemplate:
    """Utility for loading and building widgets from a .widget file."""

    adapter: TypeAdapter[WidgetRoot] = TypeAdapter(WidgetRoot)

    def __init__(self, definition: dict[str, Any]):
        self.version = definition["version"]
        self.name = definition["name"]
        self.template = env.from_string(definition["template"])
        self.data_schema = definition.get("jsonSchema", {})

    @classmethod
    def from_file(cls, file_path: str) -> "WidgetTemplate":
        """Load a widget template from a .widget JSON file."""
        path = Path(file_path)
        if not path.is_absolute():
            # Get the caller's file path and resolve relative to it
            caller_frame = inspect.stack()[1]
            caller_path = Path(caller_frame.filename).resolve()
            path = caller_path.parent / path

        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        return cls(payload)

    def build(self, data: dict[str, Any] | T | None = None) -> WidgetRoot:
        """Build a widget by rendering the template with the provided data."""
        if data is None:
            data = {}
        if isinstance(data, BaseModel):
            data = data.model_dump()

        # Render Jinja2 template
        rendered = self.template.render(**data)

        # Parse JSON and validate
        widget_dict = json.loads(rendered)
        return self.adapter.validate_python(widget_dict)
```

**Key Points:**
- Uses Jinja2 to render widget templates with dynamic data
- Automatically resolves relative paths to `.widget` files
- Validates output against ChatKit's WidgetRoot schema

### 3. Create Widget Builder Function

**File:** `backend/app/widgets/profilecard_widget.py`

```python
"""ProfileCard widget builder for character profiles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from chatkit.widgets import WidgetRoot

from .widget_template import WidgetTemplate

# Locate the widget file relative to the repo root
# Calculate absolute path by going up from the current file
WIDGET_PATH = (
    Path(__file__).parent.parent.parent.parent.parent.parent
    / "specs"
    / "cupid-simple"
    / "widgets"
    / "ProfileCard00.widget"
)

# Load the ProfileCard widget template once at module load
profilecard_template = WidgetTemplate.from_file(str(WIDGET_PATH))


def build_profilecard_widget(character_data: dict[str, Any]) -> WidgetRoot:
    """Build a ProfileCard widget from character data.

    Args:
        character_data: Dictionary with character fields matching the widget schema:
            - name, age, occupation, location, birthdate
            - origin: {city, state, country}
            - astrological_notes: {sun_sign, moon_sign, venus_sign, mars_sign}
            - short_bio

    Returns:
        WidgetRoot ready to be streamed to the frontend
    """
    return profilecard_template.build(character_data)
```

**Key Points:**
- Widget template is loaded once at module initialization (performance optimization)
- Use absolute paths to avoid file not found errors
- Builder function is simple - just passes data to the template

### 4. Stream Widget in Server Response

**File:** `backend/app/server.py`

**Add imports:**
```python
from datetime import datetime
from chatkit.types import (
    ThreadItemDoneEvent,
    WidgetItem,
)
from .widgets.profilecard_widget import build_profilecard_widget
```

**Stream widget after agent response:**
```python
async def respond(
    self,
    thread: ThreadMetadata,
    item: UserMessageItem | None,
    context: RequestContext,
) -> AsyncIterator[ThreadStreamEvent]:
    """Handle conversation turns with chapter-based logic."""

    # ... agent response logic ...

    # After agent completes, stream the ProfileCard widget
    profilecard_widget = build_profilecard_widget(self.mortal_data)

    widget_item = WidgetItem(
        thread_id=thread.id,
        id=f"widget_{thread.id}_{datetime.now().timestamp()}",  # Manual ID generation
        created_at=datetime.now(),
        widget=profilecard_widget,
        copy_text=f"{self.mortal_data['name']}, {self.mortal_data['age']}, {self.mortal_data['occupation']}",
    )

    yield ThreadItemDoneEvent(item=widget_item)
```

**Key Points:**
- Yield `ThreadItemDoneEvent` with a `WidgetItem` to stream widgets
- Use manual ID generation with timestamp: `f"widget_{thread.id}_{datetime.now().timestamp()}"`
- The `copy_text` provides fallback text when widget is copied/pasted

---

## Widget Action Handlers

### Button Action Configuration

In your `.widget` file, configure button actions:

```json
{
  "type": "Button",
  "label": "MATCH",
  "onClickAction": {
    "type": "conversation.message",
    "payload": {
      "text": "yes",
      "role": "user"
    },
    "handler": "server"
  }
}
```

**Action Handler Types:**
- `handler: "server"` - Routes to backend `action()` method
- `handler: "client"` - Handled entirely by frontend (not shown to backend)

### Server-Side Action Handler

**File:** `backend/app/server.py`

```python
from chatkit.types import (
    Action,
    InferenceOptions,
    UserMessageItem,
    UserMessageTextContent,
)

async def action(
    self,
    thread: ThreadMetadata,
    action: Action[str, Any],
    sender: WidgetItem | None,
    context: RequestContext,
) -> AsyncIterator[ThreadStreamEvent]:
    """Handle widget action (MATCH button click)."""

    if action.type == "conversation.message":
        # Get the message text from the payload
        message_text = action.payload.get("text", "yes")

        # Create a user message item with ALL required fields
        user_message = UserMessageItem(
            thread_id=thread.id,
            id=self.store.generate_item_id("message", thread, context),
            created_at=datetime.now(),
            content=[UserMessageTextContent(text=message_text)],
            inference_options=InferenceOptions(),  # REQUIRED field
        )

        # Add the message to the store
        await self.store.add_thread_item(thread.id, user_message, context)

        # Yield the message event
        yield ThreadItemDoneEvent(item=user_message)

        # Call respond to generate the next chapter
        async for event in self.respond(thread, user_message, context):
            yield event

    return
    yield  # Make this an async generator
```

**Critical Requirements:**

1. **Use `UserMessageTextContent`**, not `UserMessageContent` (which is a union type)
2. **Include `inference_options=InferenceOptions()`** - this is a REQUIRED field
3. **Add message to store** before yielding events
4. **Yield the message** using `ThreadItemDoneEvent`
5. **Call `self.respond()`** to trigger agent response and continue conversation
6. **End with `return; yield`** to make it a proper async generator

---

## Common Patterns

### Pattern 1: Update Widget In-Place

Use this when you want to modify an existing widget without adding new messages:

```python
from chatkit.types import ThreadItemUpdated, WidgetRootUpdated

async def action(...) -> AsyncIterator[ThreadStreamEvent]:
    # Rebuild widget with new state
    updated_widget = build_my_widget(new_data)

    # Update the existing widget in-place
    yield ThreadItemUpdated(
        item_id=sender.id,  # ID of the widget that sent the action
        update=WidgetRootUpdated(widget=updated_widget),
    )
```

**Use cases:** Expanding/collapsing details, toggling states, selection

### Pattern 2: Add Message + Continue Conversation

Use this when a button should send a message and trigger agent response:

```python
async def action(...) -> AsyncIterator[ThreadStreamEvent]:
    # Create user message
    user_message = UserMessageItem(
        thread_id=thread.id,
        id=self.store.generate_item_id("message", thread, context),
        created_at=datetime.now(),
        content=[UserMessageTextContent(text="user's choice")],
        inference_options=InferenceOptions(),
    )

    await self.store.add_thread_item(thread.id, user_message, context)
    yield ThreadItemDoneEvent(item=user_message)

    # Trigger agent response
    async for event in self.respond(thread, user_message, context):
        yield event
```

**Use cases:** Confirmations, selections that advance the conversation

### Pattern 3: Hidden Context + Response

Use this when you want to pass information to the agent without showing it to the user:

```python
from chatkit.types import HiddenContextItem

async def action(...) -> AsyncIterator[ThreadStreamEvent]:
    # Store hidden context for agent
    hidden = HiddenContextItem(
        id=self.store.generate_item_id("message", thread, context),
        thread_id=thread.id,
        created_at=datetime.now(),
        content=f"<WIDGET_ACTION widgetId={sender.id}>{action.type}</WIDGET_ACTION>",
    )
    await self.store.add_thread_item(thread.id, hidden, context)

    # Trigger agent with the hidden context
    async for event in self.respond(thread, None, context):
        yield event
```

**Use cases:** Background state changes, internal tracking

---

## Troubleshooting

### Error: FileNotFoundError for .widget file

**Problem:** Relative paths don't resolve correctly.

**Solution:** Use absolute path calculation:
```python
WIDGET_PATH = (
    Path(__file__).parent.parent.parent.parent.parent.parent
    / "specs"
    / "cupid-simple"
    / "widgets"
    / "ProfileCard00.widget"
)
```

### Error: KeyError: 'widget' when generating IDs

**Problem:** `self.store.generate_item_id("widget", ...)` fails because "widget" isn't a registered item type.

**Solution:** Use manual ID generation:
```python
id=f"widget_{thread.id}_{datetime.now().timestamp()}"
```

### Error: TypeError: 'types.UnionType' object is not callable

**Problem:** Trying to instantiate `UserMessageContent` which is a union type.

**Solution:** Use the concrete type `UserMessageTextContent`:
```python
# Wrong:
content=[UserMessageContent(text=message_text)]

# Correct:
content=[UserMessageTextContent(text=message_text)]
```

### Error: ValidationError: Field required [type=missing] for 'inference_options'

**Problem:** `UserMessageItem` requires the `inference_options` field.

**Solution:** Always include it:
```python
from chatkit.types import InferenceOptions

user_message = UserMessageItem(
    thread_id=thread.id,
    id=self.store.generate_item_id("message", thread, context),
    created_at=datetime.now(),
    content=[UserMessageTextContent(text=message_text)],
    inference_options=InferenceOptions(),  # Required!
)
```

### Button shows spinning wheel but doesn't respond

**Problem:** The `action()` method isn't properly handling the action or calling `respond()`.

**Solution:** Ensure your action handler:
1. Creates a proper `UserMessageItem` with all required fields
2. Adds it to the store
3. Yields the message event
4. Calls `self.respond()` to continue the conversation

### Thread not found errors after server reload

**Problem:** In-memory store loses data when server reloads during development.

**Solution:** This is expected behavior with `MemoryStore`. After server reload:
1. Refresh the browser to start a new session
2. Or implement a persistent store (database, file-based, etc.)

---

## Additional Resources

- **ChatKit Examples:** `/Users/johnsteven/GITHUB/CHATKIT/chatkit-dev-00/examples/`
  - `news-guide/` - Event list widget with expandable details
  - `metro-map/` - Widget template pattern origin
  - `customer-support/` - Meal preference widget with state updates

- **Widget Files Location:** `specs/cupid-simple/widgets/`
  - `ProfileCard00.widget` - Full widget definition with template and schema

- **Key Server Methods:**
  - `respond()` - Handle incoming messages and generate responses
  - `action()` - Handle widget button clicks and other actions

---

## Summary

**Widget implementation checklist:**
1. ✅ Add `jinja2` dependency
2. ✅ Create `WidgetTemplate` utility class
3. ✅ Create widget builder function
4. ✅ Load widget template at module initialization
5. ✅ Stream widget using `ThreadItemDoneEvent(item=WidgetItem(...))`
6. ✅ Implement `action()` handler for interactive buttons
7. ✅ Use correct types: `UserMessageTextContent`, `InferenceOptions`
8. ✅ Call `self.respond()` to continue conversation flow

**Common pitfalls to avoid:**
- ❌ Using `UserMessageContent` instead of `UserMessageTextContent`
- ❌ Forgetting `inference_options` field
- ❌ Not calling `self.respond()` in action handlers
- ❌ Using relative paths for widget files
- ❌ Trying to use `generate_item_id("widget", ...)` (use manual IDs)

This pattern is proven to work and follows the established conventions from ChatKit's example applications.
