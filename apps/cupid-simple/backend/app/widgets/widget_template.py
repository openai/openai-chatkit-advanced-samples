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
