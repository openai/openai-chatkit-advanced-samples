import inspect
import json
from pathlib import Path
from typing import Any, TypeVar

from chatkit.widgets import WidgetRoot
from jinja2 import Environment, StrictUndefined
from pydantic import BaseModel, TypeAdapter

T = TypeVar("T", bound=BaseModel)
env = Environment(undefined=StrictUndefined)


class WidgetTemplate:
    """Utility for loading and building widgets from a .widget file."""

    adapter: TypeAdapter[WidgetRoot] = TypeAdapter(WidgetRoot)

    def __init__(self, definition: dict[str, Any]):
        self.version = definition["version"]
        if self.version != "1.0":
            raise ValueError(f"Unsupported widget spec version: {self.version}")

        self.name = definition["name"]
        self.template = env.from_string(definition["template"])
        self.data_schema = definition.get("jsonSchema", {})

    @classmethod
    def from_file(cls, file_path: str) -> "WidgetTemplate":
        path = Path(file_path)
        if not path.is_absolute():
            caller_frame = inspect.stack()[1]
            caller_path = Path(caller_frame.filename).resolve()
            path = caller_path.parent / path

        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        return cls(payload)

    def build(self, data: dict[str, Any] | T | None = None) -> WidgetRoot:
        if data is None:
            data = {}
        if isinstance(data, BaseModel):
            data = data.model_dump()
        rendered = self.template.render(**data)
        widget_dict = json.loads(rendered)
        return self.adapter.validate_python(widget_dict)
