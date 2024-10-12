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
    creator_id: uuid.UUID
    note: str
    is_encrypted: bool


class GoogleUser(BaseModel):
    email: str
    email_verified: bool
    name: str
    picture: str
    given_name: str
    family_name: str


class User(BaseModel):
    id: Annotated[uuid.UUID, Field(default_factory=uuid.uuid4)] = Field(
        default_factory=uuid.uuid4)
    google_id: str


class Note(NoteOut):
    password: str | None
