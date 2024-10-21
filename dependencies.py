from typing import Annotated
from uuid import UUID

from fastapi import Cookie, Depends, HTTPException
from sqlmodel import Session, select

from lib import is_admin
from models import Note, User
from session import get_session


def require_user(session: Annotated[Session, Depends(get_session)], user_id: Annotated[UUID | None, Cookie()] = None) -> User:
    if user_id is None:
        raise HTTPException(status_code=401, detail="User required")

    user = session.exec(select(User).where(
        User.id == user_id,
    )).first()

    if user is None or user.id is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def valid_note(
    user: Annotated[User, Depends(require_user)],
    session: Annotated[Session, Depends(get_session)],
    note_id: UUID,
    password: str | None = None,
) -> Note:
    note = session.exec(select(Note).where(
        Note.id == note_id,
    )).first()

    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    if is_admin(user):
        return note

    if note.creator_id != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if note.is_encrypted:
        if password is None:
            raise HTTPException(status_code=401, detail="Password required")
        if note.password != password:
            raise HTTPException(status_code=401, detail="Wrong password")
    elif password is not None:
        raise HTTPException(status_code=401, detail="Password not required")
    return note


def require_admin(user: Annotated[User, Depends(require_user)]) -> User:
    if is_admin(user):
        raise HTTPException(status_code=401, detail="Not admin")
    return user
