

import uuid
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class HealthyResponse(BaseModel):
    message: str = "Healthy"


class Player(BaseModel):
    creation_time: datetime = datetime.now()
    id: UUID = uuid.uuid4()
    name: str
    wins: int = 0


class Game(BaseModel):
    start_time: datetime = datetime.now()
    end_time: datetime | None = None
    id: UUID = uuid.uuid4()
    creator_id: UUID = uuid.uuid4()
    players: list[Player] = []
