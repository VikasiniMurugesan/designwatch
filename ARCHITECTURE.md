# Designwatch — Architecture & Project Explanation

> Written so anyone can read this, understand it, and explain it to their team.

---

## What Is Designwatch?

Designwatch is an **AI-powered design audit tool**. When a developer makes changes to a website's UI, Designwatch automatically looks at screenshots of those changes and tells you:

- Is the design good or bad? *(Level 1)*
- Did this change make things better or worse compared to before? *(Level 2)*
- Did anything visually break on the live website since last time we checked? *(Level 3)*

Think of it as a **robot designer** that reviews your UI so a human designer doesn't have to check every single pull request.

---

## The Three Levels — What Each One Does

### Level 1 — Single Page Design Audit
You upload **one screenshot**. The AI looks at it and checks it against 5 design rules:
1. **Visual Hierarchy** — Is the most important thing on the page easy to spot?
2. **Contrast (WCAG AA)** — Can people with poor eyesight read the text?
3. **Spacing** — Is there enough breathing room between elements?
4. **Alignment** — Are things lined up neatly?
5. **Consistency** — Do buttons, fonts, and colors look the same throughout?

It gives back a list of issues, each with a severity level (critical / high / medium / low), where the problem is on the page, why it matters, and how to fix it.

---

### Level 2 — Before / After Comparison
You upload **two screenshots** — one from before a code change, one from after. The AI compares them and tells you:
- What changed
- Whether each change is an **improvement**, a **regression** (something got worse), or **neutral**
- Whether any accessibility rules were broken (like text becoming harder to read)

This is like asking a designer: *"Did this PR make the UI better or worse?"*

---

### Level 3 — Autonomous Browser Scan
No screenshots needed. Designwatch **opens a real browser automatically**, visits your website, takes its own screenshots of 3 pages, and compares them against screenshots it took last time (called the **baseline**).

- **First run:** Takes and stores the baseline screenshots
- **Every run after:** Compares fresh screenshots to the baseline and reports anything that changed (regressions)
- If regressions are found, it **emails a report** to the team automatically

This is like having a robot that checks your website every time — without anyone having to do it manually.

---

## Why We Chose Each Tool

### Python
Python is the most popular language for AI projects. The Anthropic AI library, the browser automation tool (Playwright), and the web framework (FastAPI) all have excellent Python support. It's also the easiest language to read and learn.

---

### FastAPI — The Backend API
**What is an API?**
An API is like a waiter in a restaurant. You (the Streamlit UI) tell the waiter what you want, the waiter goes to the kitchen (the AI agents), and brings back your food (the results).

**What is FastAPI?**
FastAPI is a Python tool for building APIs. When the Streamlit UI wants to analyze a screenshot, it sends a request to FastAPI. FastAPI receives it, runs the AI analysis, and sends back the results.

**Why FastAPI and not something else?**
- It is very fast (the name gives it away)
- It automatically creates documentation at `http://localhost:8000/docs` so you can test the API in a browser
- It is beginner-friendly — you just write a Python function and add `@router.post(...)` above it
- It handles file uploads, JSON, and errors cleanly

---

### Streamlit — The User Interface
**What is Streamlit?**
Streamlit lets you build a web UI using only Python — no HTML, no CSS, no JavaScript needed. You write `st.button("Click me")` and it creates a real button on the webpage.

**Why Streamlit?**
For a project like this where the goal is to demonstrate the AI agent's capability — not to build a production frontend — Streamlit is the fastest way to get a working, good-looking UI. It takes minutes instead of days.

---

### uv — Dependency Management
**What is a dependency?**
When your Python project uses someone else's code (like the Anthropic library), that's a dependency. You need a tool to install and manage them.

**What is uv?**
`uv` is a modern, extremely fast Python package manager. It replaces `pip` and `venv`. Instead of `pip install`, you run `uv add`.

**Why uv and not pip?**
- `uv` is 10–100x faster than pip
- It automatically creates a virtual environment (an isolated space so your project's packages don't conflict with other projects)
- `uv run python ...` makes sure the right Python and packages are always used

---

### Alembic — Database Migrations
**What is a database migration?**
Imagine you have a database table with 5 columns. Later you need to add a 6th column. A migration is the instruction file that says "add this column". Alembic manages these instruction files so your database structure can evolve safely.

**Why Alembic?**
- It works perfectly with SQLAlchemy (our database library)
- You can run `uv run alembic upgrade head` and it applies all pending changes to the database automatically
- If something goes wrong, you can roll back

---

### SQLite — The Database
**What is SQLite?**
SQLite is a database that lives in a single file (`designwatch.db`) on your computer. There is no server to start, no password to set up. It just works.

**Why SQLite and not PostgreSQL or MySQL?**
For this project, SQLite is perfect because:
- Zero setup — just run the project and the database file is created automatically
- Works on any computer without installing anything extra
- Easy to inspect — you can open the `.db` file with any SQLite viewer

---

### Playwright — Browser Automation
**What is Playwright?**
Playwright is a tool that controls a real web browser (Chrome) from your Python code. You can tell it to open a URL, wait for the page to load, take a screenshot, click buttons — all without a human touching the mouse.

**Why Playwright?**
- It handles modern JavaScript-heavy websites well (waits for the page to fully load)
- Built-in screenshot functionality at a fixed viewport size (so screenshots are always the same size)
- Simple Python API — `page.goto(url)` and `page.screenshot(path=...)` is all you need
- Free and open source

---

### Anthropic Claude — The AI Brain
**What model are we using?**
We use `claude-opus-4-5` — Anthropic's powerful vision model.

**What can it do?**
Claude is a multimodal AI, meaning it can understand both text and images. When we send it a screenshot, it can:
- See the actual visual layout of the page
- Identify design problems
- Compare two images and describe differences
- Give structured, specific feedback — not vague answers

**Why Claude and not GPT-4 or Gemini?**
- Claude is known for precise, detailed analysis
- The Anthropic Python SDK is simple to use
- Claude follows complex instructions reliably — critical for returning structured JSON without hallucinating extra fields

---

## The Layered Architecture — Why We Organized the Code This Way

Imagine a company. There are different departments — HR, Finance, Engineering. Each department has its own job and doesn't interfere with others. Our code is organized the same way.

```
shared/          ← The rulebook everyone reads (config, environment variables)
entities/        ← The data shapes (what a "scan" looks like in the database)
repositories/    ← The filing cabinet (save and fetch scans from the database)
services/        ← The specialists (email team, report team)
features/        ← Reserved for business logic (currently empty, ready to grow)
agents/          ← The AI workers (the ones who actually do the analysis)
api/             ← The reception desk (receives requests, hands to agents, returns results)
ui/              ← The shop window (what the user sees and clicks)
```

**The rule:** Each layer can only talk to the layers below it — never above. This means:
- The AI agents don't know about the UI
- The database layer doesn't know about the API
- Changes in one layer don't break others

This makes the code easy to understand, test, and change.

---

## Complete File-by-File Explanation

### `shared/config.py`
The very first file that runs. It reads your `.env` file and makes all the secret values (API keys, email passwords) available to the rest of the project as simple variables like `ANTHROPIC_API_KEY`. It also creates the `data/`, `data/screenshots/`, `data/baselines/`, and `data/reports/` folders if they don't exist yet.

---

### `entities/models.py`
Defines what a **scan record** looks like in the database. Think of it like a form with fields:
- `id` — unique number for each scan
- `level` — was this a Level 1, 2, or 3 scan?
- `status` — pending, completed, or failed
- `image_path` — where is the uploaded screenshot saved?
- `findings_json` — the AI's findings, stored as JSON text
- `summary` — a one-paragraph summary of the results
- `report_path` — where is the HTML report file saved?
- `created_at` / `completed_at` — timestamps

---

### `migrations/`
Contains Alembic's migration files. The file inside `versions/` is the instruction that creates the `scan_reports` table in the database. Run `uv run alembic upgrade head` to apply it.

---

### `repositories/scan_repository.py`
The only file that talks directly to the database. It has simple functions:
- `create_scan()` — insert a new scan record
- `update_scan()` — save findings and mark it complete
- `get_all_scans()` — fetch all scans for the history page
- `get_scan_by_id()` — fetch one specific scan

No other file in the project writes SQL or touches the database directly — they all go through this file.

---

### `services/email_service.py`
Handles sending emails via Gmail SMTP. The main function `send_report_email()` takes the findings, builds a beautiful HTML email (with colored severity badges, confidence scores, and a gradient header), and sends it to all recipients in `REPORT_RECIPIENTS`. No attachment — everything is in the email body itself.

---

### `services/report_service.py`
Generates an HTML report file saved to `data/reports/`. This is the file users can download from the Streamlit UI. It loops through all findings and creates a styled card for each one with severity color-coding.

---

### `agents/design_audit_agent.py`
The AI brain for **Level 1 and Level 2**.

- `encode_image()` — reads an image file and converts it to base64 (a text format that can be sent to the AI API)
- `run_level1_analysis(image_path)` — sends one image + the Level 1 prompt to Claude, gets back JSON findings
- `run_level2_analysis(baseline_path, current_path)` — sends two images + the Level 2 prompt to Claude, gets back a comparison with improvement/regression/neutral labels

The prompts are carefully written to force Claude to be specific — not vague — and to only report things it can actually see in the image.

---

### `agents/browser_agent.py`
The AI brain for **Level 3** — the autonomous scanner.

- `capture_screenshot()` — launches a headless Chrome browser, opens a URL, waits for it to load, takes a screenshot
- `compare_with_claude()` — sends baseline + current screenshot to Claude and asks it to find regressions
- `scan_single_page()` — combines capture + compare for one page
- `run_level3_scan()` — runs `scan_single_page()` for all 3 pages **at the same time** (in parallel using Python threads), collects results
- `refresh_baseline()` — deletes all stored baselines so the next scan starts fresh

**Parallel scanning:** Instead of scanning page 1, then page 2, then page 3 one by one, we use `ThreadPoolExecutor` to scan all 3 at the same time. This makes the scan ~3x faster.

---

### `api/main.py`
The entry point for the FastAPI server. It creates the app and registers the three route groups:
- `/level1/...` → handled by `api/routes/level1.py`
- `/level2/...` → handled by `api/routes/level2.py`
- `/level3/...` → handled by `api/routes/level3.py`

---

### `api/routes/level1.py`
Handles `POST /level1/analyze`. Steps:
1. Receives the uploaded image file
2. Saves it to `data/screenshots/`
3. Creates a scan record in the database
4. Calls `run_level1_analysis()` from the agent
5. Saves the findings to the database
6. Generates an HTML report
7. Returns the findings as JSON to the UI

---

### `api/routes/level2.py`
Handles `POST /level2/analyze`. Same flow as Level 1 but receives **two** image files (baseline and current) and calls `run_level2_analysis()`.

---

### `api/routes/level3.py`
Handles:
- `POST /level3/scan` — triggers the full autonomous scan, saves results, sends email if regressions found
- `POST /level3/refresh-baseline` — clears stored baselines

---

### `ui/app.py`
The Streamlit app entry point. Sets up the sidebar navigation and loads the correct page based on what the user clicked. Also adds the project root to Python's path so all imports work correctly.

---

### `ui/pages/level1.py`
The Level 1 page in the UI. Shows a file uploader, displays the uploaded image, has an "Analyze Design" button, and shows the results as expandable cards with severity icons and confidence progress bars. Also provides a download button for the HTML report.

---

### `ui/pages/level2.py`
The Level 2 page. Shows two side-by-side uploaders (before and after). After comparison, shows a verdict (IMPROVED / DEGRADED / UNCHANGED), metrics for improvement/regression/neutral counts, and expandable finding cards.

---

### `ui/pages/level3.py`
The Level 3 page. Has a URL input field, a "Run Scan" button, and a "Refresh Baseline" button. Shows which pages were scanned, whether regressions were found, and a download button for the report. Informs the user when an email has been sent.

---

### `ui/pages/history.py`
Shows all past scans from the database in reverse chronological order. Each scan is an expandable card showing level, status, summary, finding count, and a download button for the report.

---

## The Complete Flow — What Happens When You Click "Analyze"

Here is the exact journey of a **Level 1 analysis**:

```
User uploads screenshot in Streamlit (ui/pages/level1.py)
    ↓
Streamlit sends the image to FastAPI via HTTP POST /level1/analyze
    ↓
FastAPI (api/routes/level1.py) receives the image
    ↓
Saves the image to data/screenshots/scan_1.png
    ↓
Creates a scan record in SQLite via scan_repository.py (status: pending)
    ↓
Calls run_level1_analysis() in agents/design_audit_agent.py
    ↓
Agent converts image to base64, sends it to Claude API with the audit prompt
    ↓
Claude (claude-opus-4-5) looks at the image, finds design issues, returns JSON
    ↓
Agent parses the JSON and returns findings to the API route
    ↓
API saves findings to the database (status: completed) via scan_repository.py
    ↓
API calls report_service.py to generate an HTML report → saved to data/reports/
    ↓
API returns the findings as JSON back to Streamlit
    ↓
Streamlit displays the findings as color-coded expandable cards
    ↓
User can download the HTML report
```

For **Level 3**, the flow is the same but:
- Playwright captures the screenshots instead of the user uploading them
- All pages scan in parallel (simultaneously)
- If regressions are found, email_service.py sends a styled HTML email to all recipients

---

## Folder Structure At a Glance

```
designwatch/
├── shared/                  ← Config and environment variables
├── entities/                ← Database table definitions
├── repositories/            ← Database read/write functions
├── services/                ← Email and report generation
├── features/                ← Business logic (ready to grow)
├── agents/                  ← AI analysis (Claude + Playwright)
├── api/
│   ├── main.py              ← FastAPI app entry point
│   └── routes/              ← One file per level
│       ├── level1.py
│       ├── level2.py
│       └── level3.py
├── ui/
│   ├── app.py               ← Streamlit app entry point
│   └── pages/               ← One file per UI page
│       ├── level1.py
│       ├── level2.py
│       ├── level3.py
│       └── history.py
├── migrations/              ← Alembic database migration files
├── data/                    ← Created at runtime (gitignored)
│   ├── screenshots/         ← Uploaded and captured images
│   ├── baselines/           ← Level 3 baseline screenshots
│   └── reports/             ← Generated HTML reports
├── .env                     ← Your secrets (never committed to git)
├── .env.example             ← Template showing what variables are needed
├── pyproject.toml           ← Project metadata and dependencies (managed by uv)
├── alembic.ini              ← Alembic configuration
└── README.md                ← How to run the project
```

---

## How to Run the Project (Quick Reference)

```bash
# 1. Install all dependencies
uv sync
uv run playwright install chromium

# 2. Set up the database
uv run alembic upgrade head

# 3. Start the API (Terminal 1)
uv run uvicorn api.main:app --reload

# 4. Start the UI (Terminal 2)
uv run streamlit run ui/app.py

# 5. For Level 3 — run the frontend app (Terminal 3)
cd ../gpt3-modern-ui
NODE_OPTIONS=--openssl-legacy-provider npm start
```

Then open **http://localhost:8501** in your browser.
