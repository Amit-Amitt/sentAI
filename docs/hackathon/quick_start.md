# Sentinel AI - Quick Start Guide

Want to run Sentinel AI locally? Follow these steps.

## Requirements
- Docker and Docker Compose
- Node.js 20+
- Python 3.13 (or `uv`)
- OpenAI or Gemini API Key

## 1. Environment Setup
Copy the example environments:
```bash
cp .env.example .env
cp apps/api/.env.example apps/api/.env
```
Open both `.env` files and paste your LLM API keys (e.g., `SENTINEL_OPENAI_API_KEY`).

## 2. Start Backend Services
Use Docker Compose to spin up PostgreSQL and Redis:
```bash
docker-compose -f docker-compose.prod.yml up redis db -d
```

Navigate to the API folder, install dependencies, and run:
```bash
cd apps/api
uv sync
uv run alembic upgrade head
uv run uvicorn sentinel_api.app:app --reload
```

## 3. Start Frontend
In a new terminal window:
```bash
cd apps/web
npm ci
npm run dev
```

Visit `http://localhost:3000` to access the application!
