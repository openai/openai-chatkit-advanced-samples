import inspect
import json
from pathlib import Path
from typing import Any, Literal

from chatkit.widgets import WidgetComponent, WidgetComponentBase, WidgetRoot
from jinja2 import Environment, StrictUndefined
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

env = Environment(undefined=StrictUndefined)


# TODO: import from chatkit.widgets after chatkit-python is bumped
class BasicRoot(WidgetComponentBase):
    model_config = ConfigDict(extra="allow")

    type: Literal["Basic"] = Field(default="Basic", frozen=True)  # pyright: ignore
    children: list[WidgetComponent] | None = None


# TODO: import from chatkit.widgets after chatkit-python is bumped
class WidgetTemplate:
    """Utility for loading and building widgets from a .widget file."""

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

    def build(self, data: dict[str, Any] | BaseModel | None = None) -> WidgetRoot:
        rendered = self.template.render(**self._normalize_data(data))
        widget_dict = json.loads(rendered)
        return TypeAdapter(WidgetRoot).validate_python(widget_dict)

    def build_basic(self, data: dict[str, Any] | BaseModel | None = None) -> BasicRoot:
        rendered = self.template.render(**self._normalize_data(data))
        widget_dict = json.loads(rendered)
        return BasicRoot.model_validate(widget_dict)

    def _normalize_data(self, data: dict[str, Any] | BaseModel | None) -> dict[str, Any]:
        if data is None:
            return {}
        if isinstance(data, BaseModel):
            return data.model_dump()
        return data
