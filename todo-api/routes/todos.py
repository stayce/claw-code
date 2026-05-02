from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from db import get_session
from models import (
    AssignPayload, Category, Status, AssigneeType,
    Todo, TodoCreate, TodoRead, TodoUpdate, TodoTag, Tag,
    compute_priority,
)

router = APIRouter(prefix="/todos", tags=["todos"])


def _attach_tags(todo: Todo, tag_ids: list[int], session: Session):
    session.exec(
        TodoTag.__table__.delete().where(TodoTag.todo_id == todo.id)  # type: ignore[attr-defined]
    )
    for tid in tag_ids:
        tag = session.get(Tag, tid)
        if not tag:
            raise HTTPException(status_code=404, detail=f"Tag {tid} not found")
        session.add(TodoTag(todo_id=todo.id, tag_id=tid))


def _refresh_priority(todo: Todo):
    todo.priority_score = compute_priority(todo)
    todo.updated_at = datetime.utcnow()


@router.post("", response_model=TodoRead, status_code=201)
def create_todo(payload: TodoCreate, session: Session = Depends(get_session)):
    todo = Todo.model_validate(payload.model_dump(exclude={"tag_ids"}))
    _refresh_priority(todo)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    _attach_tags(todo, payload.tag_ids, session)
    session.commit()
    session.refresh(todo)
    return todo


@router.get("", response_model=list[TodoRead])
def list_todos(
    category: Optional[Category] = None,
    status: Optional[Status] = None,
    assignee_type: Optional[AssigneeType] = None,
    assignee_id: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    session: Session = Depends(get_session),
):
    q = select(Todo)
    if category:
        q = q.where(Todo.category == category)
    if status:
        q = q.where(Todo.status == status)
    if assignee_type:
        q = q.where(Todo.assignee_type == assignee_type)
    if assignee_id:
        q = q.where(Todo.assignee_id == assignee_id)
    q = q.order_by(Todo.priority_score.desc()).limit(limit)  # type: ignore[union-attr]
    return session.exec(q).all()


@router.get("/next", response_model=TodoRead)
def next_todo(session: Session = Depends(get_session)):
    todo = session.exec(
        select(Todo)
        .where(Todo.status == Status.todo)
        .where(Todo.assignee_type == AssigneeType.unassigned)
        .order_by(Todo.priority_score.desc())  # type: ignore[union-attr]
        .limit(1)
    ).first()
    if not todo:
        raise HTTPException(status_code=404, detail="No unassigned tasks available")
    return todo


@router.get("/{todo_id}", response_model=TodoRead)
def get_todo(todo_id: int, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: int, payload: TodoUpdate, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    data = payload.model_dump(exclude_unset=True, exclude={"tag_ids"})
    for k, v in data.items():
        setattr(todo, k, v)
    _refresh_priority(todo)
    if payload.tag_ids is not None:
        _attach_tags(todo, payload.tag_ids, session)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(todo)
    session.commit()


@router.post("/{todo_id}/complete", response_model=TodoRead)
def complete_todo(todo_id: int, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.status = Status.done
    todo.completed_at = datetime.utcnow()
    todo.updated_at = datetime.utcnow()
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.patch("/{todo_id}/assign", response_model=TodoRead)
def assign_todo(todo_id: int, payload: AssignPayload, session: Session = Depends(get_session)):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.assignee_type = payload.assignee_type
    todo.assignee_id = payload.assignee_id
    todo.updated_at = datetime.utcnow()
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
