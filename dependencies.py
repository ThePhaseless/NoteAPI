from typing import Annotated
from uuid import UUID

from fastapi import Cookie, HTTPException

from models import Note, User
from session import notes, users


def valid_note(note_id: UUID, password: str | None = None) -> Note:
    try:
        note = next(n for n in notes if n.id == note_id)
        if password is not None and note.password != password:
            raise HTTPException(status_code=401, detail="Invalid password")

    except StopIteration as e:
        raise HTTPException(status_code=404, detail="Note not found") from e

    else:
        return note


def require_user(user_id: Annotated[UUID, Cookie()]) -> User:
    try:
        user = next(u for u in users if u.id == user_id)
    except StopIteration as e:
        raise HTTPException(status_code=401, detail="Invalid user") from e
    else:
        return user
