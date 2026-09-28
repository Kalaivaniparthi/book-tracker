import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """Create a new database connection."""
    return psycopg2.connect(DATABASE_URL)


# ==========================================
# BOOKS
# ==========================================
def get_all_books():
    """Return every book in the catalogue."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM books ORDER BY id")
    books = cur.fetchall()
    cur.close()
    conn.close()
    return books


def get_book(book_id):
    """Return one book by ID."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cur.fetchone()
    cur.close()
    conn.close()
    return book


def upsert_book(book):
    """Insert a book or update if URL already exists."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        INSERT INTO books (title, product_url, price_gbp, rating_text, description, ai_summary)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (product_url) DO UPDATE
        SET price_gbp = EXCLUDED.price_gbp,
            ai_summary = EXCLUDED.ai_summary
        RETURNING *
        """,
        (
            book["title"],
            book["product_url"],
            book["price_gbp"],
            book["rating_text"],
            book["description"],
            book.get("ai_summary"),
        ),
    )
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result


# ==========================================
# USER READING LISTS
# ==========================================
def get_user_list(user_id):
    """Return all books in a user's reading list."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT ub.id, ub.status, ub.created_at, b.*
        FROM user_books ub
        JOIN books b ON b.id = ub.book_id
        WHERE ub.user_id = %s
        ORDER BY ub.created_at DESC
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def add_to_user_list(user_id, book_id, status="want"):
    """Add a book to a user's reading list."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        INSERT INTO user_books (user_id, book_id, status)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, book_id) DO UPDATE
        SET status = EXCLUDED.status
        RETURNING *
        """,
        (user_id, book_id, status),
    )
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result


def update_user_book(user_id, entry_id, status):
    """Update the status of a book in a user's list."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        UPDATE user_books
        SET status = %s
        WHERE id = %s AND user_id = %s
        RETURNING *
        """,
        (status, entry_id, user_id),
    )
    result = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return result


def remove_from_user_list(user_id, entry_id):
    """Remove a book from a user's reading list. Returns True if deleted."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM user_books WHERE id = %s AND user_id = %s",
        (entry_id, user_id),
    )
    deleted = cur.rowcount > 0
    conn.commit()
    cur.close()
    conn.close()
    return deleted
