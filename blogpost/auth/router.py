import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from blogpost.auth import schemas
from blogpost.auth.models import User
from blogpost.auth.utils import JWTRepo, send_user_confirm_email
from blogpost.config.db import get_db

auth_router = APIRouter(prefix="/auth", tags=["Authorization"])
logger = logging.getLogger(__name__)


@auth_router.post("/register/", response_model=schemas.UserResponse, status_code=201)
async def register_user(
    bg_task: BackgroundTasks, user: schemas.UserBase, db: AsyncSession = Depends(get_db)
):
    logger.debug("New user registration started")
    try:
        user_obj = User(**user.model_dump())
        user_obj.hash(user.password)
        user_obj.last_login = func.now()
        db.add(user_obj)
        await db.commit()
        await db.refresh(user_obj)
        logger.debug("New user registration completed")
        bg_task.add_task(send_user_confirm_email, user_obj.id, user_obj.email)
        return user_obj
    except Exception as exc:
        await db.rollback()
        raise HTTPException(400, "An error occurred during user registration") from exc


@auth_router.post("/login/", response_model=schemas.LoginResponse, status_code=200)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    try:
        logger.debug("User login started")
        result = await db.execute(select(User).filter_by(username=form_data.username))
        user = result.scalar_one_or_none()
        if user is None or not user.verify(form_data.password):
            raise HTTPException(401, "Invalid credentials")
        if not user.is_active:
            raise HTTPException(403, "Inactive user")
        if not user.is_confirmed:
            raise HTTPException(403, "Check your email and confirm user")
        user.last_login = func.now()
        await db.commit()
        await db.refresh(user)
        access_token = JWTRepo.create_token(user.id, "access")
        logger.debug("User login completed")
        return {"token_type": "Bearer", "access_token": access_token}
    except Exception as exc:
        await db.rollback()
        raise HTTPException(400, "An error occurred during login") from exc


@auth_router.post("/confirm/{token}", status_code=200)
async def confirm_user(token: str = Path(...), db: AsyncSession = Depends(get_db)):
    try:
        user_id = JWTRepo.decode_token(token, "confirm")
        result = await db.execute(select(User).filter_by(id=user_id))
        user = result.scalar_one_or_none()
        if user is None or not user.is_active:
            raise HTTPException(403, "Invalid user")
        user.is_confirmed = True
        await db.commit()
        await db.refresh(user)
        return "Success"
    except Exception as exc:
        raise HTTPException(400, "User confirmation failed") from exc
