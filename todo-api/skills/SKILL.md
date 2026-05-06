---
name: todo
description: Manage personal todo tasks — create, list, update, complete, and assign tasks. Supports priorities, categories, locations, and agent or human assignees.
metadata: {"openclaw": {"emoji": "✅", "requires": {"bins": ["curl"]}}}
---

## Todo API

Base URL: http://localhost:8000

All responses are JSON. Always relay the relevant fields to the user in a short, friendly message.

---

## Categories

Valid values for `category`: household, renovation, health, shopping, work_projects, coding, pets, cleaning

---

## Create a task

POST /todos

Required fields: `title` (string), `category` (see above)

Optional fields:
- `importance` 1-10 (default 5)
- `urgency` 1-10 (default 5)
- `emotional_weight` 1-10 (default 5)
- `energy_required` 1-10 (default 5)
- `complexity` 1-10 (default 5)
- `notes` — freetext
- `due_date` — ISO 8601
- `assignee_type` — human, agent, unassigned
- `assignee_id` — string
- `location_type` — physical or online
- `location_value` — URL or address
- `recurring` — true/false
- `recur_interval` — daily, weekly, monthly

Example:
```
curl -s -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy cat food", "category": "shopping", "urgency": 8}'
```

Reply: "Created #<id>: <title> [<category>] — priority <priority_score>"

---

## List tasks

GET /todos?status=todo&category=shopping&assignee_type=unassigned&limit=5

Sorted by priority_score descending. Cap Telegram replies at 5.

---

## Next task

GET /todos/next — highest-priority unassigned todo task.

Use when user says: "what should I do next", "what's urgent"

---

## Complete

POST /todos/{id}/complete

Reply: "Done! ✓ #<id>: <title>"

---

## Assign

PATCH /todos/{id}/assign
{"assignee_type": "agent", "assignee_id": "openclaw"}
{"assignee_type": "human", "assignee_id": "stayce"}
{"assignee_type": "unassigned"}

---

## Update

PATCH /todos/{id} — any fields, priority recalculated automatically.

---

## Delete

DELETE /todos/{id}

---

## Tags

GET /tags — list
POST /tags {"name": "string"} — create
DELETE /tags/{id} — delete

---

## Health

GET /health — check before any request if something seems wrong.

---

## Natural language mappings

- "remind me to X" → POST /todos
- "what should I do next" → GET /todos/next
- "show my tasks" → GET /todos?status=todo&limit=5
- "I finished X" → POST /todos/{id}/complete
- "I'll handle X" → PATCH /todos/{id}/assign → agent
- "assign to me" → PATCH /todos/{id}/assign → human
- "what are you working on" → GET /todos?assignee_type=agent&status=in_progress
