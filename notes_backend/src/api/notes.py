"""Notes CRUD routes."""

from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Response, status

from src.api.db import get_connection
from src.api.models import NoteCreate, NoteOut, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


def _row_to_note(row) -> NoteOut:
    # SQLite CURRENT_TIMESTAMP returns 'YYYY-MM-DD HH:MM:SS'
    created = datetime.fromisoformat(row["created_at"].replace(" ", "T"))
    updated = datetime.fromisoformat(row["updated_at"].replace(" ", "T"))
    return NoteOut(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        created_at=created,
        updated_at=updated,
    )


@router.get(
    "",
    response_model=List[NoteOut],
    summary="List notes",
    description="Return all notes ordered by updated_at desc.",
    operation_id="list_notes",
)
# PUBLIC_INTERFACE
def list_notes() -> List[NoteOut]:
    """List all notes."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM notes ORDER BY updated_at DESC, id DESC"
        ).fetchall()
        return [_row_to_note(r) for r in rows]
    finally:
        conn.close()


@router.get(
    "/{note_id}",
    response_model=NoteOut,
    summary="Get note",
    description="Fetch a single note by id.",
    operation_id="get_note",
)
# PUBLIC_INTERFACE
def get_note(note_id: int) -> NoteOut:
    """Get a note by id."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Note not found")
        return _row_to_note(row)
    finally:
        conn.close()


@router.post(
    "",
    response_model=NoteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create note",
    description="Create a new note.",
    operation_id="create_note",
)
# PUBLIC_INTERFACE
def create_note(payload: NoteCreate) -> NoteOut:
    """Create a new note."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)",
            (payload.title, payload.content),
        )
        note_id = cur.lastrowid
        conn.commit()

        row = conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()
        return _row_to_note(row)
    finally:
        conn.close()


@router.put(
    "/{note_id}",
    response_model=NoteOut,
    summary="Update note",
    description="Update title/content of a note by id.",
    operation_id="update_note",
)
# PUBLIC_INTERFACE
def update_note(note_id: int, payload: NoteUpdate) -> NoteOut:
    """Update an existing note."""
    if payload.title is None and payload.content is None:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Note not found")

        # Build dynamic update while keeping it simple and safe.
        fields = []
        values = []
        if payload.title is not None:
            fields.append("title = ?")
            values.append(payload.title)
        if payload.content is not None:
            fields.append("content = ?")
            values.append(payload.content)
        values.append(note_id)

        conn.execute(f"UPDATE notes SET {', '.join(fields)} WHERE id = ?", tuple(values))
        conn.commit()

        row = conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()
        return _row_to_note(row)
    finally:
        conn.close()


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete note",
    description="Delete a note by id.",
    operation_id="delete_note",
)
# PUBLIC_INTERFACE
def delete_note(note_id: int) -> Response:
    """Delete a note."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Note not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    finally:
        conn.close()
