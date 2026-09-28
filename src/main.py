from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from src import db
from src.auth import get_current_user

app = FastAPI(
    title="Book Tracker API",
    description="An AI-powered book tracker with Supabase auth.",
    version="1.0.0",
)


# ==========================================
# REQUEST MODELS
# ==========================================
class AddBookRequest(BaseModel):
    book_id: int
    status: str = "want"  # want | reading | read


class UpdateStatusRequest(BaseModel):
    status: str  # want | reading | read


# ==========================================
# PUBLIC ROUTES
# ==========================================

@app.get("/", summary="API info")
def root():
    return {
        "name": "Book Tracker API",
        "version": "1.0.0",
        "endpoints": {
            "public": ["/books", "/books/{id}"],
            "protected": ["/my-list"],
        },
    }


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/books", summary="List all books")
def list_books():
    return db.get_all_books()


@app.get("/books/{book_id}", summary="Get one book")
def get_book(book_id: int):
    book = db.get_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
    return book


# ==========================================
# PROTECTED ROUTES (require JWT)
# ==========================================

@app.get("/my-list", summary="Get your reading list")
def get_my_list(user = Depends(get_current_user)):
    """Return the authenticated user's reading list."""
    return db.get_user_list(str(user.id))


@app.post("/my-list", status_code=201, summary="Add a book to your list")
def add_book_to_list(
    body: AddBookRequest,
    user = Depends(get_current_user),
):
    """Add a book to the authenticated user's reading list."""
    # Check the book exists
    book = db.get_book(body.book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book {body.book_id} not found")

    # Validate status
    if body.status not in ("want", "reading", "read"):
        raise HTTPException(
            status_code=400,
            detail="status must be one of: want, reading, read",
        )

    return db.add_to_user_list(str(user.id), body.book_id, body.status)


@app.put("/my-list/{entry_id}", summary="Update a book's status")
def update_entry(
    entry_id: int,
    body: UpdateStatusRequest,
    user = Depends(get_current_user),
):
    """Update the status of a book in the authenticated user's list."""
    if body.status not in ("want", "reading", "read"):
        raise HTTPException(
            status_code=400,
            detail="status must be one of: want, reading, read",
        )

    result = db.update_user_book(str(user.id), entry_id, body.status)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Entry {entry_id} not found")
    return result


@app.delete("/my-list/{entry_id}", status_code=204, summary="Remove a book from your list")
def delete_entry(
    entry_id: int,
    user = Depends(get_current_user),
):
    """Remove a book from the authenticated user's reading list."""
    if not db.remove_from_user_list(str(user.id), entry_id):
        raise HTTPException(status_code=404, detail=f"Entry {entry_id} not found")
    return None
