from __future__ import annotations

from typing import Literal

from chatkit.actions import Action
from chatkit.widgets import Icon, ListView, ListViewItem, Row, Text
from pydantic import BaseModel

MealPreferenceOption = Literal["vegetarian", "kosher", "gluten intolerant", "child"]

SET_MEAL_PREFERENCE_ACTION_TYPE = "support.set_meal_preference"


class SetMealPreferencePayload(BaseModel):
    meal: MealPreferenceOption


SetMealPreferenceAction = Action[Literal["support.set_meal_preference"], SetMealPreferencePayload]

_MEAL_PREFERENCE_LABELS: dict[MealPreferenceOption, str] = {
    "vegetarian": "Vegetarian",
    "kosher": "Kosher",
    "gluten intolerant": "Gluten intolerant",
    "child": "Child",
}

MEAL_PREFERENCE_ORDER: tuple[MealPreferenceOption, ...] = (
    "vegetarian",
    "kosher",
    "gluten intolerant",
    "child",
)


def meal_preference_label(value: MealPreferenceOption) -> str:
    return _MEAL_PREFERENCE_LABELS.get(value, value.title())


def build_meal_preference_widget(
    *,
    selected: MealPreferenceOption | None = None,
) -> ListView:
    """Render the meal preference list widget with optional selection state."""

    items: list[ListViewItem] = []
    for value in MEAL_PREFERENCE_ORDER:
        label = meal_preference_label(value)
        emphasized = value == selected
        action_config = (
            SetMealPreferenceAction.create(SetMealPreferencePayload(meal=value))
            if selected is None
            else None
        )
        items.append(
            ListViewItem(
                key=f"meal-{value}",
                onClickAction=None if selected else action_config,
                children=[
                    Row(
                        gap=2,
                        children=[
                            Icon(
                                name="check" if emphasized else "empty-circle",
                                color="secondary",
                            ),
                            Text(
                                value=label,
                                weight="semibold" if emphasized else "medium",
                                color="emphasis" if emphasized else None,
                            ),
                        ],
                    )
                ],
            )
        )

    return ListView(
        key="meal-preference-list",
        children=items,
    )
