"""ProfileCard widget builder for character profiles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from chatkit.widgets import WidgetRoot

from .widget_template import WidgetTemplate

# Locate the widget file relative to the repo root
WIDGET_PATH = (
    Path(__file__).parent.parent.parent.parent.parent.parent
    / "specs"
    / "cupid-simple"
    / "widgets"
    / "ProfileCard00.widget"
)

# Load the ProfileCard widget template
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
