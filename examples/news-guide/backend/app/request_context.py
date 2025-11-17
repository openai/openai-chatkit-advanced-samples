from __future__ import annotations

from typing import Annotated

from fastapi import Request
from pydantic import BaseModel, ConfigDict, Field


class RequestContext(BaseModel):
    """Typed request context shared across ChatKit handlers."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    request: Annotated[Request | None, Field(default=None, exclude=True)]
    article_id: str | None = None
