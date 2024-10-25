
from typing import Annotated
from uuid import UUID

import uvicorn
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response, responses
from fastapi.middleware.cors import CORSMiddleware
from google.auth.transport import requests
from google.oauth2 import id_token
from sqlmodel import Session, select

from dependencies import require_admin, require_user, valid_note
from lib import is_admin, is_password_encrypted
from models import GoogleUser, Note, NoteInput, User
from session import get_session

app = FastAPI(
    servers=[
        {"url": "https://myapi.nerine.dev"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://notes.nerine.dev",
        "http://localhost:4200",
        "http://localhost",
    ],
    allow_headers=["*"],
    allow_credentials=True,
    allow_methods=["*"],
)


@app.get("/ping")
async def ping() -> str:
    return "pong"


@app.get("/", response_description="Redirects to /docs")
async def docs_redirect() -> responses.RedirectResponse:
    return responses.RedirectResponse(url="/docs")


@app.get("/login")
async def login(google_token: str, response: Response, session: Annotated[Session, Depends(get_session)]) -> User:
    details_raw: dict = id_token.verify_oauth2_token(  # type: ignore
        google_token, requests.Request(),
    )
    details = GoogleUser.model_validate(details_raw)

    user = session.exec(select(User).where(
        User.google_id == details.sub,
    )).first()

    if user is None:
        user = User(
            google_id=details.sub,
            email=details.email,
        )
        user.is_admin = is_admin(user)
        session.add(user)
        session.commit()

    response.set_cookie(key="user_id", value=str(user.id))
    return user


@app.get("/logout")
async def logout(response: Response) -> None:
    response.delete_cookie(key="user_id")

notes_router = APIRouter(prefix="/note", tags=["note"])


@notes_router.get("/note", response_model=list[Note])
async def get_user_notes(
    user: Annotated[User, Depends(require_user)],
    session: Annotated[Session, Depends(get_session)],
) -> list[Note]:
    notes = session.exec(select(Note).where(
        Note.creator_id == user.id)).all()

    if (user.is_admin):
        return list(notes)

    def hide_password(note: Note) -> Note:
        if note.is_encrypted:
            note.note = "encrypted"
        return note

    return list(map(hide_password, notes))


@notes_router.post("/note", response_model=Note)
async def create_note(
        session: Annotated[Session, Depends(get_session)],
        note: NoteInput,

        user: Annotated[User, Depends(require_user)],
) -> Note:
    if user.id is None:
        raise HTTPException(status_code=401, detail="User required")
    new_note = Note(
        note=note.note,
        password=note.password,
        name=note.name,
        is_encrypted=is_password_encrypted(note.password),
        creator_id=user.id,
    )
    session.add(new_note)
    session.commit()
    return new_note


@notes_router.get("/note/all", dependencies=[Depends(require_admin)], response_model=list[Note])
async def get_all_notes(session: Annotated[Session, Depends(get_session)]) -> list[Note]:
    note_list = list(session.exec(select(Note)).all())
    for note in note_list:
        note.is_encrypted = False
    return note_list


@notes_router.get("/note/{note_id}")
async def get_note(note: Annotated[Note, Depends(valid_note)]) -> Note:
    return note


@notes_router.put("/note/{note_id}")
async def update_note(
        session: Annotated[Session, Depends(get_session)],
        note_id: UUID,
        note: NoteInput,
) -> Note:
    new_note = session.get(Note, note_id)
    if new_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    new_note.name = note.name
    new_note.note = note.note
    new_note.password = note.password
    new_note.is_encrypted = is_password_encrypted(note.password)
    session.add(note)
    session.commit()
    return new_note


@notes_router.delete("/note/{note_id}")
async def delete_note(
        session: Annotated[Session, Depends(get_session)],
        user: Annotated[User, Depends(require_user)],
        note: Annotated[Note, Depends(valid_note)],
) -> None:
    if note.creator_id != user.id and not user.is_admin:
        raise HTTPException(status_code=401, detail="Unauthorized")
    session.delete(note)
    session.commit()

user_router = APIRouter(
    prefix="/user", tags=["user"], dependencies=[Depends(require_admin)])


@user_router.get("/users")
async def get_users(session: Annotated[Session, Depends(get_session)]) -> list[User]:
    return list(session.exec(select(User)).all())


@user_router.delete("/user/{query_user_id}")
async def delete_user(session: Annotated[Session, Depends(get_session)], query_user_id: UUID) -> None:
    user = session.get(User, query_user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for note in session.exec(select(Note).where(Note.creator_id == query_user_id)).all():
        session.delete(note)
    session.delete(user)

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)  # noqa: S104
