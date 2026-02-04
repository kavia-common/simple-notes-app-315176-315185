from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.db import init_db
from src.api.notes import router as notes_router

openapi_tags = [
    {"name": "system", "description": "Service health and meta endpoints."},
    {"name": "notes", "description": "CRUD operations for notes."},
]

app = FastAPI(
    title="Simple Notes API",
    description="FastAPI backend for a simple notes application (SQLite persistence).",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# React dev server default
frontend_origin = "http://localhost:3000"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    """Initialize database schema on application startup."""
    init_db()


@app.get(
    "/",
    tags=["system"],
    summary="Health check",
    description="Verify the service is running.",
    operation_id="health_check",
)
# PUBLIC_INTERFACE
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}


app.include_router(notes_router)
