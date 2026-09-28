# Book Tracker API

An AI-powered book tracker: scrapes 60 books, generates 1-sentence AI summaries, and lets authenticated users build private reading lists.

Built with FastAPI, PostgreSQL, Docker, Supabase Auth, and Groq.

---

## Why This Exists

A portfolio project that combines everything from the FlyRank Backend AI Engineering track:
- CRUD APIs (Week 2)
- PostgreSQL + Docker (Week 3)
- Supabase Auth with JWT (Week 4)
- Web scraping (Week 5)
- AI integration (Groq)

The goal: prove I can take an idea and ship a real, multi-user backend.

---

## Features

- 60 books scraped from Books to Scrape
- AI-generated 1-sentence summaries for each book (Groq / Qwen)
- Supabase Auth: users sign up, log in, get JWTs
- Private reading lists: each user only sees their own
- Reading status: want / reading / read
- Swagger UI with Bearer token authorization
- Docker Compose: app + Postgres with one command

---

## Architecture

```
Client
  │
  ├──► Supabase (auth, issues JWT)
  │
  └──► FastAPI ──► PostgreSQL (books, user_books)
                     ▲
                     │
              Seeded by scraper + Groq
```

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Framework | FastAPI |
| Database | PostgreSQL 15 (Docker) |
| Auth | Supabase |
| AI | Groq (qwen/qwen3.8-27b) |
| Scraper | requests + BeautifulSoup |
| Container | Docker Compose |

---

## Setup

### 1. Clone

```bash
git clone https://github.com/Kalaivaniparthi/book-tracker.git
cd book-tracker
```

### 2. Create `.env`

Copy `.env.example` → `.env` and fill in:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
GROQ_API_KEY=gsk_...
DATABASE_URL=postgresql://user:password@db:5432/books_db
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=books_db
```

Get Supabase keys from Supabase Dashboard → Settings → API.
Get Groq key (free) from console.groq.com.

### 3. Start Postgres + app

```bash
docker compose up --build
```

### 4. Seed the database (once)

In a second terminal:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/seed_books.py
```

This scrapes 60 books and calls Groq for AI summaries (~10-15 min).

### 5. Open the API

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| GET | `/` | ❌ | API info |
| GET | `/health` | ❌ | Health check |
| GET | `/books` | ❌ | List all books with AI summaries |
| GET | `/books/{id}` | ❌ | One book's details |
| GET | `/my-list` | ✅ | Your reading list |
| POST | `/my-list` | ✅ | Add a book to your list |
| PUT | `/my-list/{id}` | ✅ | Update status |
| DELETE | `/my-list/{id}` | ✅ | Remove from list |

---

## Testing with Auth

1. Sign up in Supabase (Authentication → Users → Add user, check "Auto Confirm")
2. Get a JWT (login via Supabase API or your old auth server)
3. In Swagger, click **Authorize** 🔒 and paste the token
4. Now `/my-list` endpoints work

Without a token, `/my-list` returns 401.

---

## The Hardest Thing That Broke

**Groq deprecated the Llama models mid-build.** Every model I tried (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `llama-4-scout`) returned `model_not_found`.

**The fix:** Listed available models with `client.models.list()`, switched to `qwen/qwen3.8-27b`, and added `/no_think` to the prompt to prevent the model from outputting empty content (a quirk of reasoning models).

**Lesson:** External APIs change. Always list what's actually available instead of hardcoding model names.

---

## What's Next

- **Frontend:** A simple React app that consumes this API
- **Deploy:** Push to Render or Railway with Supabase + a managed Postgres
- **Better AI:** Cache summaries, batch requests, or use a local model
- **Features:** Book recommendations, reading stats, share lists

---

## Limitations (Honest)

- The scraper only handles the first 3 catalogue pages (60 books). Expanding to 50 pages is a one-line change.
- AI summaries are generated once during seeding, not regenerated on price changes.
- No frontend — this is API-only. Swagger is the interface.
- No rate limiting on the AI calls during seeding (fine for 60 books, not for 10,000).

---

## Author

**Kalaivani Parthi** — FlyRank Backend AI Engineering Capstone
