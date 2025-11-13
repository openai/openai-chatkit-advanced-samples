"""
Defines a widget for the cat's profile card.
This is an example of a static presentation widget.
"""

from __future__ import annotations

from chatkit.widgets import Badge, Box, Caption, Card, Col, Image, Row, Spacer, Text, Title

from .cat_state import CatState


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


def _detail_row(label: str, value: str) -> Row:
    return Row(
        children=[
            Caption(value=label),
            Spacer(),
            Text(value=value, size="sm", textAlign="end"),
        ],
    )


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


def render_profile_card(state: CatState, favorite_toy: str | None = None) -> Card:
    header = Box(
        background={"light": "yellow-50", "dark": "yellow-900"},
        padding={"x": 4, "y": 2},
        children=[
            Row(
                align="center",
                children=[
                    Title(
                        value="C A L I F O R N I A",
                        size="sm",
                        weight="bold",
                        color={"light": "orange-700", "dark": "orange-100"},
                    ),
                    Spacer(),
                    Badge(label="meowing license", color="warning", variant="soft"),
                ],
            )
        ],
    )

    details = Row(
        padding={"x": 5, "top": 2, "bottom": 4},
        gap=4,
        align="start",
        children=[
            Box(
                background="linear-gradient(135deg, #fff6d9 0%, #ceb0fb 100%)",
                radius="3xl",
                align="center",
                justify="center",
                children=[
                    Image(
                        src=_image_src(state),
                        alt=f"{state.name} portrait",
                        width=90,
                        height=110,
                        position="top",
                        radius="3xl",
                    ),
                ],
            ),
            Col(
                gap=2,
                flex="auto",
                children=[
                    Title(value=state.name, size="md"),
                    _detail_row("Age", _format_age_label(state.age)),
                    _detail_row("Color pattern", _format_color_pattern_label(state.color_pattern)),
                    _detail_row("Toy choice", _format_favorite_toy(favorite_toy)),
                ],
            ),
        ],
    )

    return Card(
        key="cat-profile",
        size="sm",
        padding=0,
        children=[header, details],
    )


def profile_widget_copy_text(state: CatState) -> str:
    return f"{state.name}, age {state.age}, is a {state.color_pattern} cat."
