from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from ..auth import User, current_user
from ..config import get_db
from . import schemas
from .models import Draft

draft_router = APIRouter(prefix="/draft", tags=["Draft"])


@draft_router.get("/", response_model=list[schemas.DraftResponse], status_code=200)
async def list_drafts(
    skip: int = Query(0),
    limit: int = Query(10),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(
        select(Draft).offset(skip).limit(limit).filter_by(user_id=user.id)
    )
    drafts = result.scalars().all()
    return drafts


@draft_router.get("/{draft_id}", response_model=schemas.DraftDetail, status_code=200)
async def detail_draft(
    draft_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    result = await db.execute(select(Draft).filter_by(id=draft_id, user_id=user.id))
    draft = result.scalar_one_or_none()
    if draft is None:
        raise HTTPException(404, f"Draft with id: {draft_id} not found")
    return draft


@draft_router.post("/", response_model=schemas.DraftResponse, status_code=200)
async def create_draft(
    draft: schemas.DraftIn = Body(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    try:
        db_draft = Draft(**draft.model_dump())
        db_draft.user_id = user.id
        db.add(db_draft)
        await db.commit()
        await db.refresh(db_draft)
        return db_draft
    except Exception as exc:
        await db.rollback()
        raise HTTPException(401, f"Draft could not be created") from exc


@draft_router.patch("/{draft_id}", response_model=schemas.DraftDetail, status_code=200)
async def update_draft(
    draft_id: int = Path(...),
    draft: schemas.DraftIn = Body(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    try:
        result = await db.execute(select(Draft).filter_by(id=draft_id, user_id=user.id))
        db_draft = result.scalar_one_or_none()
        if db_draft is None:
            raise HTTPException(404, f"Draft with id: {draft_id} not found")
        db_draft.title = draft.title or db_draft.title
        db_draft.body = draft.body or db_draft.body
        await db.commit()
        await db.refresh(db_draft)
        return db_draft
    except Exception as exc:
        await db.rollback()
        raise HTTPException(401, "draft could not be updated") from exc


@draft_router.delete("/{draft_id}", status_code=204)
async def delete_draft(
    draft_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    try:
        result = await db.execute(select(Draft).filter_by(id=draft_id, user_id=user.id))
        db_draft = result.scalar_one_or_none()
        if db_draft is None:
            raise HTTPException(404, f"Draft with id: {draft_id} not found")
        await db.delete(db_draft)
        await db.commit()
        return
    except Exception as exc:
        await db.rollback()
        raise HTTPException(401, "Draft could not be deleted") from exc
