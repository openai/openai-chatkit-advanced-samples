"""
Defines a widget for the cat's profile card.
This is an example of a static presentation widget.
"""

from __future__ import annotations

from chatkit.widgets import WidgetRoot, WidgetTemplate

from ..cat_state import CatState

cat_profile_widget_template = WidgetTemplate.from_file("cat_profile.widget")


def _format_age_label(age: int) -> str:
    return "1 year" if age == 1 else f"{age} years"


def _format_color_pattern_label(color_pattern: str | None) -> str:
    if color_pattern is None:
        return "N/A"
    return color_pattern.capitalize()


def _format_favorite_toy(favorite_toy: str | None) -> str:
    if favorite_toy is None:
        return "A laser pointer"
    return favorite_toy.capitalize()


def _image_src(state: CatState) -> str:
    if state.color_pattern == "black":
        return "https://files.catbox.moe/pbkakb.png"
    if state.color_pattern == "calico":
        return "https://files.catbox.moe/p2mj4g.png"
    if state.color_pattern == "colorpoint":
        return "https://files.catbox.moe/nrtexw.png"
    if state.color_pattern == "tabby":
        return "https://files.catbox.moe/zn77bd.png"
    if state.color_pattern == "white":
        return "https://files.catbox.moe/zvkhpo.png"
    return "https://files.catbox.moe/e42tgh.png"


def build_profile_card_widget(state: CatState, favorite_toy: str | None = None) -> WidgetRoot:
    return cat_profile_widget_template.build(
        data={
            "name": state.name,
            "image_src": _image_src(state),
            "age": _format_age_label(state.age),
            "color_pattern": _format_color_pattern_label(state.color_pattern),
            "favorite_toy": _format_favorite_toy(favorite_toy),
        }
    )


def profile_widget_copy_text(state: CatState) -> str:
    return f"{state.name}, age {state.age}, is a {state.color_pattern} cat."
