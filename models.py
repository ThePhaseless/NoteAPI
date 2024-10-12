import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class NoteOut(BaseModel):
    id: Annotated[uuid.UUID, Field(default_factory=uuid.uuid4)] = Field(
        default_factory=uuid.uuid4)
    created_at: Annotated[datetime, Field(default_factory=datetime.now)] = Field(
        default_factory=datetime.now)
    name: str
    note: str
    is_encrypted: bool


class Note(NoteOut):
    password: str | None
