
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CheckPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    check_id: UUID
    check_name: str
    old_status: str
    new_status: Literal["down"]
    reason: str


class CheckDownEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: UUID
    type: Literal["healthchecks.check.down"]
    version: Literal["1.0"]
    occurred_at: datetime
    request_id: UUID
    payload: CheckPayload
