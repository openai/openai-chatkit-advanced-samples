from __future__ import annotations

from typing import Annotated

from fastapi import Request
from pydantic import BaseModel, ConfigDict, Field


class RequestContext(BaseModel):
    """
    Typed request context shared across ChatKit handlers.

    The map_id is included so future multi-map scenarios can be distinguished,
    but the demo currently serves a single reference map.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    request: Annotated[Request | None, Field(default=None, exclude=True)]
    map_id: str = "solstice-metro"
