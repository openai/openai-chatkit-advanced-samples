"""
Defines an interactive widget that prompts the user to select a name for the cat.
This widget wires up two client action configs.
"""

from __future__ import annotations

from chatkit.widgets import WidgetRoot, WidgetTemplate
from pydantic import BaseModel, Field


class CatNameSuggestion(BaseModel):
    """Name idea paired with a short blurb describing the cat it fits."""

    name: str
    reason: str | None = None


class CatNameSelectionPayload(BaseModel):
    """Payload sent when the user chooses one of the suggested names."""

    name: str
    options: list[CatNameSuggestion] = Field(default_factory=list)


name_suggestions_widget_template = WidgetTemplate.from_file("cat_name_suggestions.widget")


def build_name_suggestions_widget(
    names: list[CatNameSuggestion],
    selected: str | None = None,
) -> WidgetRoot:
    """Render the selectable list widget for cat name suggestions."""
    print(f"Building name suggestions widget with selected: {selected}")
    print(f"Names: {names}")
    return name_suggestions_widget_template.build(
        data={
            "items": [suggestion.model_dump() for suggestion in names],
            "selected": selected.strip().title() if selected else None,
        }
    )
