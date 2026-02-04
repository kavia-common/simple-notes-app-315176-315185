"""Pydantic models for Notes API payloads."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    """Shared properties for a note."""

    title: str = Field(..., min_length=1, max_length=200, description="Note title.")
    content: str = Field(..., min_length=0, description="Markdown/plaintext note body.")


class NoteCreate(NoteBase):
    """Request body to create a new note."""


class NoteUpdate(BaseModel):
    """Request body to update an existing note."""

    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Updated title.")
    content: Optional[str] = Field(None, description="Updated content.")


class NoteOut(NoteBase):
    """Response model representing a stored note."""

    id: int = Field(..., description="Note id.")
    created_at: datetime = Field(..., description="Creation timestamp (UTC).")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC).")
