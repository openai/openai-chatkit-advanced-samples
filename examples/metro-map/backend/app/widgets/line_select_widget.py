"""
List widget for picking one of the metro lines.
"""

from __future__ import annotations

from chatkit.widgets import WidgetRoot

from ..data.metro_map_store import Line
from .widget_template import WidgetTemplate

line_select_widget_template = WidgetTemplate.from_file("line_select.widget")


def build_line_select_widget(lines: list[Line], selected: str | None = None) -> WidgetRoot:
    """Render a line selector widget from the provided line metadata."""
    return line_select_widget_template.build(
        data={
            "items": lines,
            "selected": selected,
        }
    )
