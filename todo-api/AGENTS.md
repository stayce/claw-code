# Todo API — Agent Guide

## What this is

A personal task management system built for both human and AI agent use. It runs locally on your Mac as a persistent HTTP server. You interact with it the same way whether you're a person clicking buttons in a browser or an AI agent receiving a Telegram message.

The core idea: tasks have a **priority score** computed from how important, urgent, emotionally heavy, and energy-demanding they are. You never have to manually sort or decide what to do next — just ask for `/todos/next` and the highest-priority unclaimed task comes back.

Tasks can be **assigned** to a human or an agent. When OpenClaw claims a task, it sets `assignee_type: agent, assignee_id: openclaw`. When the human owner claims it, `assignee_type: human, assignee_id: stayce`. Unassigned tasks are in the shared pool.

---

## Priority score

```
priority_score = (importance × 3) + (urgency × 3) + (emotional_weight × 2) + energy_required
```

Max: 90. Higher = do sooner.

| Field | What it means | Example high value |
|---|---|---|
| importance | How much this matters long-term | Major health appointment = 9 |
| urgency | How time-sensitive | Bill due tomorrow = 10 |
| emotional_weight | Dread or emotional effort | Difficult phone call = 8 |
| energy_required | Physical or mental energy | Deep coding session = 9 |
| complexity | Steps or unknowns (not scored, used for filtering) | — |

---

## Categories

`household` `renovation` `health` `shopping` `work_projects` `coding` `pets` `cleaning`

Inference guide:
- "buy", "order", "pick up" → shopping
- "fix", "repair", "install" → renovation or household
- "doctor", "medicine", "exercise" → health
- "code", "PR", "deploy", "debug" → coding
- "meeting", "report", "client" → work_projects
- "vet", "feed", "walk the dog" → pets
- "vacuum", "dishes", "laundry" → cleaning
- "organise", "sort", "tidy" → household

---

## Task lifecycle

```
created (unassigned, status: todo)
    ↓
claimed → PATCH /assign
    ↓
in progress → PATCH /{id} status: in_progress
    ↓
done → POST /{id}/complete
```

Blocked: PATCH status to blocked with a note.
Release: PATCH /assign with assignee_type: unassigned.

---

## Base URL

http://localhost:8000

Check /health first if anything fails.

---

## Endpoints

| Method | Path | What it does |
|---|---|---|
| GET | /health | Server check |
| POST | /todos | Create |
| GET | /todos | List (filterable) |
| GET | /todos/next | Highest-priority unassigned |
| GET | /todos/{id} | Get one |
| PATCH | /todos/{id} | Update |
| DELETE | /todos/{id} | Delete |
| POST | /todos/{id}/complete | Mark done |
| PATCH | /todos/{id}/assign | Assign/release |
| GET | /tags | List tags |
| POST | /tags | Create tag |
| DELETE | /tags/{id} | Delete tag |

---

## Natural language → API

| User says | Action |
|---|---|
| "remind me to X" / "add X" | POST /todos — infer category and scores |
| "what should I do next" | GET /todos/next |
| "show my tasks" | GET /todos?status=todo&limit=5 |
| "show my shopping list" | GET /todos?category=shopping&status=todo |
| "I finished X" | POST /todos/{id}/complete |
| "I'll handle X" | PATCH /todos/{id}/assign → agent |
| "assign to me" | PATCH /todos/{id}/assign → human |
| "X is blocked" | PATCH status: blocked + note |
| "delete X" | DELETE — confirm first |
| "what are you working on" | GET /todos?assignee_type=agent&status=in_progress |

When user refers to a task by name, match by title from the recent list. If ambiguous, ask.

---

## Error handling

| Status | Say |
|---|---|
| 404 | "I couldn't find that task." |
| 409 | "That tag already exists." |
| 422 | "Something looks wrong — [field] must be [constraint]." |
| 500 | "Server error. Check /tmp/todo-api.err on your Mac." |
| connection refused | "Todo server isn't running. Start with: uvicorn main:app" |

---

## Telegram reply format

Surface only: id, title, category, priority_score, status, assignee, due_date (if set), notes (if set). Keep it to 1-2 lines.
