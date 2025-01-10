import logging

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import select

from ..auth import User, current_user
from ..config import get_db
from . import schemas
from .models import Post

post_router = APIRouter(prefix="/blog", tags=["Blog"])
logger = logging.getLogger(__name__)


@post_router.get("/", response_model=list[schemas.PostList], status_code=200)
async def list_posts(
    skip: int = Query(0),
    limit: int = Query(10),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Post).offset(skip).limit(limit))
    posts = result.scalars().all()
    return posts


@post_router.get("/{blog_id}", response_model=schemas.PostResponse, status_code=200)
async def detail_post(
    blog_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Post).options(selectinload(Post.author)).filter_by(id=blog_id)
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(404, f"Post with id: {blog_id} not found")
    return post


@post_router.post("/", response_model=schemas.PostResponse, status_code=200)
async def create_post(
    post: schemas.PostIn = Body(...),
    db: AsyncSession = Depends(get_db),
    auth_user: User = Depends(current_user),
):
    try:
        db_post = Post(**post.model_dump())
        db_post.user_id = auth_user.id
        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)
        result = await db.execute(
            select(Post).options(selectinload(Post.author)).filter_by(id=db_post.id)
        )
        db_post = result.scalar_one()
        return db_post
    except Exception as exc:
        logger.error(f"{auth_user.full_name} failed to create a post : {str(exc)}")


@post_router.patch("/{blog_id}", response_model=schemas.PostDetail, status_code=200)
async def update_post(
    blog_id: int = Path(...),
    post: schemas.PostIn = Body(...),
    db: AsyncSession = Depends(get_db),
    auth_user: User = Depends(current_user),
):
    try:
        result = await db.execute(select(Post).filter_by(id=blog_id))
        db_post = result.scalar_one_or_none()
        if db_post is None:
            logger.error(f"Post with id: {blog_id} not found")
            raise HTTPException(404, f"Post with id: {blog_id} not found")
        if db_post.user_id != auth_user.id:
            logger.error(
                f"Unauthorized update of the Post with id : {blog_id} "
                + f"tried by user with id : {auth_user.id}",
            )
            raise HTTPException(401, "Unauthorized update of the Post")
        db_post.body = post.body
        await db.commit()
        await db.refresh(db_post)
        result = await db.execute(
            select(Post).options(selectinload(Post.author)).filter_by(id=db_post.id)
        )
        db_post = result.scalar_one()
        return db_post
    except Exception as exc:
        await db.rollback()
        logger.error(f"Post could not be updated : {str(exc)}")
        raise HTTPException(401, "Post could not be updated")


@post_router.delete("/{blog_id}", status_code=204)
async def delete_post(
    blog_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
    auth_user: User = Depends(current_user),
):
    try:
        result = await db.execute(select(Post).filter_by(id=blog_id))
        db_post = result.scalar_one_or_none()
        if db_post is None:
            logger.error(f"Post with id: {blog_id} not found")
            raise HTTPException(404, f"Post with id: {blog_id} not found")
        if db_post.user_id != auth_user.id:
            logger.error(
                f"Unauthorized delete of the Post with id : {blog_id} "
                + f"tried by user with id : {auth_user.id}",
            )
            raise HTTPException(401, "Unauthorized delete of the Post")
        await db.delete(db_post)
        await db.commit()
        return
    except Exception as exc:
        await db.rollback()
        logger.error(f"Post could not be deleted : {str(exc)}")
        raise HTTPException(401, "Post could not be deleted")
