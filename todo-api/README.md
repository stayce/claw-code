# Todo API

A personal task manager built for both human and AI agent use. Runs locally on your Mac as a persistent REST API. Manage tasks from a browser UI, from Telegram via OpenClaw, or from any HTTP client.

Tasks are scored by importance, urgency, emotional weight, and energy required — so you always know what to do next without thinking about it.

---

## Stack

- **FastAPI** — REST API
- **SQLite** — local database (`todos.db`)
- **SQLModel** — schema, validation, ORM in one
- **uvicorn** — ASGI server
- **OpenClaw** — Telegram agent integration via `SKILL.md`

---

## Setup

```bash
git clone https://github.com/stayce/claw-code.git
git checkout claude/todo-app-priority-system-2oj3q
cp -r todo-api/ ~/todo-api
cd ~/todo-api

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --reload
```

API is now running at `http://localhost:8000`
Swagger UI at `http://localhost:8000/docs`

---

## Frontend

Open `index.html` directly in your browser. No server needed for the HTML itself — it talks to the API at `localhost:8000`.

Features:
- Task list sorted by priority score (red/amber/green)
- Filter by status, category, assignee
- **Next up** button — surfaces highest priority unassigned task
- Add/edit modal with sliders for all 5 scores
- One-click complete, assign to agent, release, delete
- Live API health indicator
- Auto-refreshes every 30 seconds

---

## Run on login (Mac)

Edit `com.todo-api.plist` — replace `YOUR_USER` with your Mac username.

```bash
cp com.todo-api.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.todo-api.plist
```

Logs at `/tmp/todo-api.log` and `/tmp/todo-api.err`.

To stop: `launchctl unload ~/Library/LaunchAgents/com.todo-api.plist`

---

## OpenClaw skill

```bash
mkdir -p ~/.openclaw/skills/todo
cp skills/SKILL.md ~/.openclaw/skills/todo/SKILL.md
```

Then message OpenClaw on Telegram:
- *"remind me to buy cat food"* → creates task
- *"what should I do next"* → highest priority task
- *"show my tasks"* → top 5 open tasks
- *"I finished the dentist call"* → marks done
- *"take care of X"* → agent claims the task

See `AGENTS.md` for the full agent guide.

---

## Priority score

```
score = (importance × 3) + (urgency × 3) + (emotional_weight × 2) + energy_required
```

Max 90. Recomputed automatically on every create or update.

---

## Categories

`household` `renovation` `health` `shopping` `work_projects` `coding` `pets` `cleaning`

---

## API quick reference

| Method | Path | What it does |
|---|---|---|
| GET | /health | Server status |
| POST | /todos | Create task |
| GET | /todos | List tasks |
| GET | /todos/next | Highest-priority unassigned task |
| GET | /todos/{id} | Get one task |
| PATCH | /todos/{id} | Update task |
| DELETE | /todos/{id} | Delete task |
| POST | /todos/{id}/complete | Mark done |
| PATCH | /todos/{id}/assign | Assign or release |
| GET | /tags | List tags |
| POST | /tags | Create tag |
| DELETE | /tags/{id} | Delete tag |

Full interactive docs at `http://localhost:8000/docs` when running locally.

---

## File structure

```
todo-api/
  main.py               # FastAPI app
  models.py             # SQLModel schema + priority scoring
  db.py                 # SQLite engine and session
  requirements.txt
  index.html            # Browser frontend (no build step)
  AGENTS.md             # Full agent integration guide
  com.todo-api.plist    # Mac launchd autostart
  routes/
    todos.py            # CRUD, /next, /assign, /complete
    tags.py
  skills/
    SKILL.md            # OpenClaw skill definition
```

---

## Deploying to Vercel

Coming soon — requires swapping SQLite for Neon (Postgres). The API routes and models stay the same, only the DB connection changes.
