
import copy
from typing import Annotated

import uvicorn
from fastapi import (
    Depends,
    FastAPI,
    responses,
)
from fastapi.middleware.cors import CORSMiddleware

from dependencies import valid_note
from models import Note, NoteOut
from session import notes

app = FastAPI(
    servers=[
        {"url": "https://api.nerine.dev"},
        {"url": "http://localhost:8000"},
    ],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/", response_description="Redirects to /docs")
async def docs_redirect() -> responses.RedirectResponse:
    return responses.RedirectResponse(url="/docs")


@app.get("/note", response_model=list[NoteOut])
async def get_notes() -> list[Note]:
    ret_notes = copy.deepcopy(notes)
    # Rewrite password if enctrypted
    for note in ret_notes:
        if note.is_encrypted:
            note.note = "encrypted"
    return ret_notes


@app.post("/note", response_model=NoteOut)
async def create_note(name: str, note: str, password: str | None = None) -> Note:
    new_note = Note(note=note, password=password, name=name,
                    is_encrypted=password != "")
    notes.append(new_note)
    return new_note


@app.get("/note/{note_id}")
async def get_note(note: Annotated[Note, Depends(valid_note)]) -> Note:
    return note

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)  # noqa: S104