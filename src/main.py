from fastapi import FastAPI, HTTPException

from src import db

app = FastAPI(
    title="Book Tracker API",
    description="An AI-powered book tracker with Supabase auth.",
    version="1.0.0",
)


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
    """Return the full book catalogue with AI summaries."""
    return db.get_all_books()


@app.get("/books/{book_id}", summary="Get one book")
def get_book(book_id: int):
    """Return one book by ID."""
    book = db.get_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=f"Book {book_id} not found")
    return book
