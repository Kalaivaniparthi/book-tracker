-- ==========================================
-- Books table: shared catalogue
-- ==========================================
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    product_url TEXT UNIQUE NOT NULL,
    price_gbp NUMERIC(10, 2),
    rating_text TEXT,
    description TEXT,
    ai_summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==========================================
-- User books table: each user's reading list
-- ==========================================
CREATE TABLE IF NOT EXISTS user_books (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'want',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, book_id)
);

-- ==========================================
-- Index for fast lookups
-- ==========================================
CREATE INDEX IF NOT EXISTS idx_user_books_user_id ON user_books(user_id);
CREATE INDEX IF NOT EXISTS idx_user_books_status ON user_books(user_id, status);
