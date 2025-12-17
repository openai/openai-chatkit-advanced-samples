from __future__ import annotations

from typing import Literal

from chatkit.actions import Action
from chatkit.widgets import WidgetRoot, WidgetTemplate
from pydantic import BaseModel

MealPreferenceOption = Literal[
    "vegetarian",
    "kosher",
    "gluten intolerant",
    "child",
]

SET_MEAL_PREFERENCE_ACTION_TYPE = "support.set_meal_preference"


class SetMealPreferencePayload(BaseModel):
    meal: MealPreferenceOption


SetMealPreferenceAction = Action[Literal["support.set_meal_preference"], SetMealPreferencePayload]
meal_preferences_template = WidgetTemplate.from_file("meal_preferences.widget")

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
) -> WidgetRoot:
    """Render the meal preference list widget with optional selection state."""

    options = [
        {"value": value, "label": meal_preference_label(value)} for value in MEAL_PREFERENCE_ORDER
    ]
    payload = {
        "options": options,
        "selected": selected,
        "actionType": SET_MEAL_PREFERENCE_ACTION_TYPE,
    }
    return meal_preferences_template.build(payload)
