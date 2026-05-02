from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel


class Category(str, Enum):
    household = "household"
    renovation = "renovation"
    health = "health"
    shopping = "shopping"
    work_projects = "work_projects"
    coding = "coding"
    pets = "pets"
    cleaning = "cleaning"


class Status(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    blocked = "blocked"
    done = "done"


class AssigneeType(str, Enum):
    human = "human"
    agent = "agent"
    unassigned = "unassigned"


class LocationType(str, Enum):
    physical = "physical"
    online = "online"


class RecurInterval(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class TodoTag(SQLModel, table=True):
    todo_id: Optional[int] = Field(default=None, foreign_key="todo.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)


class TagBase(SQLModel):
    name: str = Field(index=True, unique=True)


class Tag(TagBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    todos: list["Todo"] = Relationship(back_populates="tags", link_model=TodoTag)


class TagRead(TagBase):
    id: int


class TodoBase(SQLModel):
    title: str
    notes: Optional[str] = None
    category: Category
    status: Status = Status.todo
    importance: int = Field(default=5, ge=1, le=10)
    urgency: int = Field(default=5, ge=1, le=10)
    emotional_weight: int = Field(default=5, ge=1, le=10)
    energy_required: int = Field(default=5, ge=1, le=10)
    complexity: int = Field(default=5, ge=1, le=10)
    due_date: Optional[datetime] = None
    assignee_type: AssigneeType = AssigneeType.unassigned
    assignee_id: Optional[str] = None
    location_type: Optional[LocationType] = None
    location_value: Optional[str] = None
    recurring: bool = False
    recur_interval: Optional[RecurInterval] = None
    parent_id: Optional[int] = Field(default=None, foreign_key="todo.id")


class Todo(TodoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    priority_score: int = Field(default=0)
    tags: list[Tag] = Relationship(back_populates="todos", link_model=TodoTag)


class TodoCreate(TodoBase):
    tag_ids: list[int] = []


class TodoUpdate(SQLModel):
    title: Optional[str] = None
    notes: Optional[str] = None
    category: Optional[Category] = None
    status: Optional[Status] = None
    importance: Optional[int] = Field(default=None, ge=1, le=10)
    urgency: Optional[int] = Field(default=None, ge=1, le=10)
    emotional_weight: Optional[int] = Field(default=None, ge=1, le=10)
    energy_required: Optional[int] = Field(default=None, ge=1, le=10)
    complexity: Optional[int] = Field(default=None, ge=1, le=10)
    due_date: Optional[datetime] = None
    assignee_type: Optional[AssigneeType] = None
    assignee_id: Optional[str] = None
    location_type: Optional[LocationType] = None
    location_value: Optional[str] = None
    recurring: Optional[bool] = None
    recur_interval: Optional[RecurInterval] = None
    tag_ids: Optional[list[int]] = None


class AssignPayload(SQLModel):
    assignee_type: AssigneeType
    assignee_id: Optional[str] = None


class TodoRead(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    priority_score: int
    tags: list[TagRead] = []


def compute_priority(todo: "Todo") -> int:
    return todo.importance * 3 + todo.urgency * 3 + todo.emotional_weight * 2 + todo.energy_required
