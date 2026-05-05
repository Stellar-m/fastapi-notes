from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from create_tables import create_tables
from database import get_db
from models import Note, NoteUpdate, NoteCreate

app = FastAPI()

@app.on_event("startup")
async def startup():
    await create_tables()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/notes/all")
async def get_notes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note))
    notes = result.scalars().all()
    return notes

@app.get("/notes/{note_id}")
async def note(note_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    return note

@app.post("/notes/add")
async def add_note(note: NoteCreate, db: AsyncSession = Depends(get_db)):
    note_obj = Note(**note.__dict__)
    # note_obj = Note(**note.model_dump())
    db.add(note_obj)
    await db.commit()
    return note_obj



@app.put("/notes/update/{note_id}")
async def update_note(note_id: int, data: NoteUpdate, db: AsyncSession = Depends(get_db)):
    note_obj = await db.get(Note, note_id)
    if not note_obj:
        raise HTTPException(status_code=404, detail="Note not found")

    note_obj.title = data.title
    note_obj.content = data.content
    await db.commit()
    return note_obj

@app.delete("/notes/delete/{note_id}")
async def delete_note(note_id: int, db: AsyncSession = Depends(get_db)):
    note_obj = await db.get(Note, note_id)
    if not note_obj:
        raise HTTPException(status_code=404, detail="Note not found")
    await db.delete(note_obj)
    await db.commit()
    return note_obj