# Designwatch

AI-powered UI/UX design audit agent — analyzes screenshots, detects visual regressions, and delivers automated design feedback via structured reports.

## Features

- **Level 1** — Upload a screenshot, get AI design analysis across 5 principles (Visual Hierarchy, Contrast/WCAG AA, Spacing, Alignment, Consistency)
- **Level 2** — Upload before/after screenshots, get a structured diff with improvement/regression classification
- **Level 3** — Autonomous browser scan of a live website, baseline comparison, regression detection with email reporting

## Setup

### 1. Install dependencies

```bash
uv sync
uv run playwright install chromium
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### 3. Run database migrations

```bash
uv run alembic upgrade head
```

### 4. Start the API server

```bash
uv run uvicorn api.main:app --reload
```

### 5. Start the Streamlit UI

```bash
uv run streamlit run ui/app.py
```

Open http://localhost:8501 in your browser.

## Environment Variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `GMAIL_ADDRESS` | Gmail address to send reports from |
| `GMAIL_APP_PASSWORD` | Gmail App Password (not your login password) |
| `REPORT_RECIPIENTS` | Comma-separated list of email recipients |
| `TARGET_WEBSITE_URL` | Default URL for Level 3 autonomous scans |

## Architecture

```
shared/        → config, environment
entities/      → SQLAlchemy database models
repositories/  → database access layer
services/      → email and report generation
features/      → business logic layer
agents/        → AI agents (design audit, browser scan)
api/           → FastAPI routes
ui/            → Streamlit pages
migrations/    → Alembic database migrations
```
