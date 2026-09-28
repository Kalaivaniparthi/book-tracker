# How I built this with AI

Ten weeks ago, I couldn't explain what an API was. Today I have a live portfolio with real backend projects.

## What I built
- A FastAPI CRUD API
- A PostgreSQL database in Docker
- Supabase authentication with JWTs
- An AI-powered book tracker (capstone)

## The one thing AI did that I couldn't have done alone
AI helped me debug every dead-end — DNS failures, Docker networking, deprecated models, Git conflicts. I spent 3 months solving problems I'd never seen before, with AI as my pair programmer.

## The one thing that broke
Mid-capstone, Groq retired the Llama model I was using. Every AI call returned `model_not_found`. I spent an hour confused until I ran `client.models.list()` — and saw what was actually available. Switched to Qwen, added `/no_think`, and it worked.

**The lesson:** External APIs change. Don't hardcode — always ask what's available.
