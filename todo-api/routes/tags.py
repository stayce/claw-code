from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db import get_session
from models import Tag, TagBase, TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
def list_tags(session: Session = Depends(get_session)):
    return session.exec(select(Tag).order_by(Tag.name)).all()  # type: ignore[union-attr]


@router.post("", response_model=TagRead, status_code=201)
def create_tag(payload: TagBase, session: Session = Depends(get_session)):
    existing = session.exec(select(Tag).where(Tag.name == payload.name)).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Tag '{payload.name}' already exists")
    tag = Tag.model_validate(payload)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: int, session: Session = Depends(get_session)):
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    session.delete(tag)
    session.commit()
