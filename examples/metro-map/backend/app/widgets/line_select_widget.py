"""
List widget for picking one of the metro lines.
"""

from __future__ import annotations

from typing import Final, Literal, TypeAlias

from chatkit.actions import Action
from chatkit.widgets import Box, Icon, ListView, ListViewItem, Text
from pydantic import BaseModel
from ..data.metro_map_store import Line

LineSelectActionType: TypeAlias = Literal["line.select"]
LINE_SELECT_ACTION_TYPE: Final[LineSelectActionType] = "line.select"


class LineSelectPayload(BaseModel):
    id: str


LineSelectAction = Action[LineSelectActionType, LineSelectPayload]


def _line_item(line: Line, selected: str | None) -> ListViewItem:
    is_selected = selected is not None and line.id == selected
    return ListViewItem(
        key=line.id,
        gap=5,
        onClickAction=(
            None if selected else LineSelectAction.create(LineSelectPayload(id=line.id))
        ),
        children=[
            Box(
                background=line.color,
                radius="full",
                size=25,
            ),
            Text(
                value=line.name,
                size="sm",
                color="gray-900" if is_selected or selected is None else "gray-600",
            ),
            *([Icon(name="check", color="gray-900", size="2xl")] if is_selected else []),
        ],
    )


def build_line_select_widget(lines: list[Line], selected: str | None = None) -> ListView:
    """Render a line selector widget from the provided line metadata."""

    items = [_line_item(line, selected) for line in lines]
    return ListView(children=items)
