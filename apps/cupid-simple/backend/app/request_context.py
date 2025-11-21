"""Request context for tracking chapter progression and character data."""

from typing import Any, TypedDict


class RequestContext(TypedDict):
    """Context for tracking game state across conversation turns."""

    chapter: int  # 1=mortal profile, 2=match profile, 3+=game scenes
    mortal_data: dict[str, Any]  # Character data from mortal.yaml
    match_data: dict[str, Any]  # Character data from match.yaml
