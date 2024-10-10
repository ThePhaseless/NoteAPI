

import uuid
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class NoPlayerFoundError(Exception):
    pass


class NoGameFoundError(Exception):
    pass


class PlayerChoice(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3


class HealthyResponse(BaseModel):
    message: str = "Healthy"


class Player(BaseModel):
    creation_time: datetime = datetime.now()
    name: str
    wins: int = 0
    current_game_id: UUID | None = None


class Game(BaseModel):
    id: UUID = uuid.uuid4()
    start_time: datetime = datetime.now()
    end_time: datetime | None = None
    winner: Player | None = None
    creator: Player
    players: dict[Player, PlayerChoice] = {}


class PlayerJoined(BaseModel):
    player_name: str


class GameRound(BaseModel):
    round_number: int
    enemy_choice: PlayerChoice
    own_choice: PlayerChoice


class GameStart(BaseModel):
    timer: int
    rounds: int


class GameEnd(BaseModel):
    winner_id: UUID
