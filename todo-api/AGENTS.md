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

Max: 90. Higher = do sooner. The score is recomputed and stored every time a task is created or updated, so it's always queryable and sortable without client-side math.

| Field | What it means | Example high value |
|---|---|---|
| importance | How much this matters long-term | Major health appointment = 9 |
| urgency | How time-sensitive | Bill due tomorrow = 10 |
| emotional_weight | How much dread or effort it carries emotionally | Difficult phone call = 8 |
| energy_required | Physical or mental energy to execute | Deep coding session = 9 |
| complexity | How many steps or unknowns are involved | Used for filtering, not scoring |

---

## Categories

`household` `renovation` `health` `shopping` `work_projects` `coding` `pets` `cleaning`

When inferring category from natural language, use your best judgement:
- "buy", "order", "pick up" → shopping
- "fix", "repair", "install" → renovation or household
- "doctor", "medicine", "exercise" → health
- "code", "PR", "deploy", "debug" → coding
- "meeting", "report", "client" → work_projects
- "vet", "feed", "walk the dog" → pets
- "vacuum", "dishes", "laundry" → cleaning
- "organise", "sort", "tidy" → household

---

## Lifecycle of a task

```
created (unassigned, status: todo)
    ↓
claimed → PATCH /assign (assignee_type: agent or human)
    ↓
in progress → PATCH /{id} (status: in_progress)
    ↓
done → POST /{id}/complete
```

A task can also be:
- `blocked` — set status to blocked, add a note explaining why
- released back to pool — PATCH /assign with assignee_type: unassigned

---

## Base URL

```
http://localhost:8000
```

Always check `/health` first if requests fail. If health returns an error, the server is not running — tell the user and stop.

---

## Endpoints quick reference

| Method | Path | What it does |
|---|---|---|
| GET | /health | Server status check |
| POST | /todos | Create a task |
| GET | /todos | List tasks (filterable) |
| GET | /todos/next | Highest-priority unassigned task |
| GET | /todos/{id} | Get one task |
| PATCH | /todos/{id} | Update any fields |
| DELETE | /todos/{id} | Delete a task |
| POST | /todos/{id}/complete | Mark done |
| PATCH | /todos/{id}/assign | Assign or release |
| GET | /tags | List tags |
| POST | /tags | Create tag |
| DELETE | /tags/{id} | Delete tag |

---

## Creating a task

```bash
curl -s -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Book dentist appointment",
    "category": "health",
    "importance": 7,
    "urgency": 6,
    "emotional_weight": 5,
    "energy_required": 2
  }'
```

Only `title` and `category` are required. All scores default to 5. When a user gives you a casual message like "remind me to buy cat food", infer reasonable defaults — shopping is low importance, urgency depends on context, emotional weight low, energy low. Don't ask for all ten fields.

**Reply format:** `Created #<id>: <title> [<category>] — priority <priority_score>`

---

## Listing tasks

```bash
# Top 5 open tasks
curl -s "http://localhost:8000/todos?status=todo&limit=5"

# Everything in the shopping category
curl -s "http://localhost:8000/todos?category=shopping"

# What the agent currently owns
curl -s "http://localhost:8000/todos?assignee_type=agent&assignee_id=openclaw&status=in_progress"
```

**Reply format:** numbered list, one per line — `#<id>: <title> [<category>] priority:<score>`
Cap list replies at 5 items for Telegram. If there are more, say "...and X more. Ask for a category or full list."

---

## Getting the next task

```bash
curl -s http://localhost:8000/todos/next
```

Returns the single highest-priority task that is `status: todo` and `assignee_type: unassigned`. Use this when the user says "what should I do next", "what's most urgent", "what's at the top of my list".

If 404, reply: "Nothing in the queue right now — all tasks are either assigned or done."

---

## Completing a task

```bash
curl -s -X POST http://localhost:8000/todos/42/complete
```

**Reply format:** `Done! ✓ #<id>: <title>`

---

## Assigning a task

```bash
# Agent takes it
curl -s -X PATCH http://localhost:8000/todos/42/assign \
  -H "Content-Type: application/json" \
  -d '{"assignee_type": "agent", "assignee_id": "openclaw"}'

# Human takes it
curl -s -X PATCH http://localhost:8000/todos/42/assign \
  -H "Content-Type: application/json" \
  -d '{"assignee_type": "human", "assignee_id": "stayce"}'

# Release back to pool
curl -s -X PATCH http://localhost:8000/todos/42/assign \
  -H "Content-Type: application/json" \
  -d '{"assignee_type": "unassigned"}'
```

---

## Updating a task

Send only the fields you want to change. Priority score is recomputed automatically.

```bash
curl -s -X PATCH http://localhost:8000/todos/42 \
  -H "Content-Type: application/json" \
  -d '{"urgency": 9, "notes": "Actually needed by Friday"}'
```

---

## Natural language → API patterns

| User says | Action |
|---|---|
| "remind me to X" / "add X to my list" | POST /todos — infer category, use default scores |
| "what should I do next" / "what's urgent" | GET /todos/next |
| "show my tasks" / "what's on my list" | GET /todos?status=todo&limit=5 |
| "show my shopping list" | GET /todos?category=shopping&status=todo |
| "I finished X" / "mark X as done" | POST /todos/{id}/complete |
| "I'll handle X" / "take care of X" | PATCH /todos/{id}/assign → agent |
| "assign X to me" | PATCH /todos/{id}/assign → human |
| "X is blocked" | PATCH /todos/{id} with status: blocked, add note |
| "update X, it's more urgent now" | PATCH /todos/{id} with urgency bumped |
| "delete X" / "remove X" | DELETE /todos/{id} — confirm first |
| "what are you working on" | GET /todos?assignee_type=agent&status=in_progress |

When the user refers to a task by name rather than ID, search the recent list and match by title. If ambiguous, list the matches and ask which one.

---

## Error handling

| Status | Meaning | What to say |
|---|---|---|
| 404 | Task or tag not found | "I couldn't find that task." |
| 409 | Duplicate tag | "That tag already exists." |
| 422 | Invalid field value | "Something looks wrong with that — [field] must be [constraint]." |
| 500 | Server error | "The todo server hit an error. Check /tmp/todo-api.err on your Mac." |
| connection refused | Server not running | "The todo server isn't running. Start it with: uvicorn main:app (from the todo-api folder)" |

---

## Response fields reference

Every todo response includes:

```json
{
  "id": 42,
  "title": "Buy cat food",
  "category": "shopping",
  "status": "todo",
  "importance": 5,
  "urgency": 8,
  "emotional_weight": 3,
  "energy_required": 2,
  "complexity": 1,
  "priority_score": 54,
  "assignee_type": "unassigned",
  "assignee_id": null,
  "location_type": null,
  "location_value": null,
  "recurring": false,
  "recur_interval": null,
  "due_date": null,
  "notes": null,
  "parent_id": null,
  "tags": [],
  "created_at": "2026-04-24T10:00:00",
  "updated_at": "2026-04-24T10:00:00",
  "completed_at": null
}
```

For Telegram replies, surface only: id, title, category, priority_score, status, assignee, due_date (if set), notes (if set). Keep it short.
