from __future__ import annotations

from typing import Any, Literal, Mapping, Sequence

from chatkit.actions import Action as WidgetAction
from chatkit.widgets import Button, Col, Icon, ListView, ListViewItem, Row, Text
from pydantic import BaseModel, Field

SELECT_CAT_NAME_ACTION_TYPE = "cats.select_name"
REQUEST_MORE_CAT_NAMES_ACTION_TYPE = "cats.more_names"


class CatNameSuggestion(BaseModel):
    """Name idea paired with a short blurb describing the cat it fits."""

    name: str
    reason: str | None = None


class CatNameSelectionPayload(BaseModel):
    """Payload sent when the user chooses one of the suggested names."""

    name: str
    options: list[CatNameSuggestion] = Field(default_factory=list)


class RequestMoreCatNamesPayload(BaseModel):
    """Payload for requesting another batch of name suggestions."""

    refresh: bool = True


SelectCatNameAction = WidgetAction[Literal[SELECT_CAT_NAME_ACTION_TYPE], CatNameSelectionPayload]
RequestMoreNamesAction = WidgetAction[
    Literal[REQUEST_MORE_CAT_NAMES_ACTION_TYPE], RequestMoreCatNamesPayload
]


def _name_suggestion_item(
    names: list[CatNameSuggestion], suggestion: CatNameSuggestion, selected: str | None = None
) -> ListViewItem:
    name = suggestion.name
    is_selected = selected == name.lower()
    has_selected = selected is not None
    text_color = "emphasis" if is_selected else "tertiary" if has_selected else None
    reason_text = (
        Text(value=suggestion.reason, color="tertiary", size="sm") if suggestion.reason else None
    )
    icon = (
        Icon(name="check", color="success", size="xl")
        if is_selected
        else Icon(name="dot", color="gray-300" if not has_selected else "gray-200", size="xl")
    )
    item = ListViewItem(
        onClickAction=SelectCatNameAction.create(
            CatNameSelectionPayload(name=name, options=names),
            handler="client",
        )
        if not has_selected
        else None,
        children=[
            Row(
                gap=3,
                align="center",
                children=[
                    icon,
                    Col(
                        gap=1,
                        children=[
                            Text(value=name, weight="semibold", color=text_color),
                            *([reason_text] if reason_text else []),
                        ],
                    ),
                ],
            )
        ],
    )
    return item


def _request_more_names_item(disabled: bool) -> ListViewItem:
    return ListViewItem(
        children=[
            Button(
                onClickAction=RequestMoreNamesAction.create(
                    RequestMoreCatNamesPayload(),
                    handler="client",
                ),
                variant="outline",
                color="discovery",
                size="lg",
                pill=True,
                block=True,
                align="center",
                label="Suggest more names",
                iconEnd="sparkle",
                disabled=disabled,
            )
        ],
    )


def build_name_suggestions_widget(
    names: Sequence[str | CatNameSuggestion | Mapping[str, Any]],
    *,
    selected: str | None = None,
) -> ListView:
    """Render the selectable list widget for cat name suggestions."""

    normalized_selected = selected.strip().lower() if selected else None

    items: list[ListViewItem] = [
        _name_suggestion_item(names, suggestion, normalized_selected) for suggestion in names
    ]
    items.append(_request_more_names_item(disabled=selected is not None))

    return ListView(children=items)
