from uuid import UUID

from fastapi import HTTPException

from models import Note
from session import notes


def valid_note(note_id: UUID, password: str | None = None) -> Note:
    try:
        note = next(n for n in notes if n.id == note_id)
        if password is not None and note.password != password:
            raise HTTPException(status_code=401, detail="Invalid password")

    except StopIteration as e:
        raise HTTPException(status_code=404, detail="Note not found") from e

    else:
        return note
