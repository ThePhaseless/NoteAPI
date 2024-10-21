import uuid
from datetime import datetime
from typing import Annotated

from sqlmodel import Field, Relationship, SQLModel  # type: ignore


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    notes: list["Note"] = Relationship(back_populates="creator")
    email: str = Field(unique=True)
    google_id: str
    is_admin: bool = Field(default=False)


class NoteInput(SQLModel):
    name: str
    note: str
    password: str | None = Field(exclude=True, default=None)


class Note(NoteInput, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: Annotated[datetime, Field(default_factory=datetime.now)] = Field(
        default_factory=datetime.now)
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    creator: User = Relationship(back_populates="notes")
    is_encrypted: bool = Field(index=True)


class GoogleUser(SQLModel):
    sub: str
    email: str
    email_verified: bool
    name: str
    picture: str
    given_name: str
    family_name: str
