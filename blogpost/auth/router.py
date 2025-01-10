import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from ..config import get_db
from . import schemas
from .models import User
from .utils import JWTRepo, send_forgot_password_email, send_user_confirm_email

auth_router = APIRouter(prefix="/user", tags=["Authorization"])
logger = logging.getLogger(__name__)


@auth_router.post("/register/", response_model=schemas.UserResponse, status_code=201)
async def register_user(
    bg_task: BackgroundTasks, user: schemas.UserBase, db: AsyncSession = Depends(get_db)
):
    logger.debug("New user registration started")
    try:
        user_obj = User(**user.model_dump())
        user_obj.hash(user.password)
        db.add(user_obj)
        await db.commit()
        await db.refresh(user_obj)
        logger.debug("New user registration completed")
        bg_task.add_task(send_user_confirm_email, user_obj)
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
            raise HTTPException(403, "Activate account by confirming email")
        user.last_login = func.now()
        await db.commit()
        await db.refresh(user)
        access_token = JWTRepo.create_token(user.id, "access")
        refresh_token = JWTRepo.create_token(user.id, "refresh", 1440)
        logger.debug("User login completed")
        return {
            "token_type": "Bearer",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    except Exception as exc:
        await db.rollback()
        raise HTTPException(400, "An error occurred during login") from exc


@auth_router.get("/confirm-email/{token}", response_model=schemas.Success, status_code=200)
async def confirm_user_email(
    token: str = Path(...), db: AsyncSession = Depends(get_db)
):
    try:
        user_id = JWTRepo.decode_token(token, "confirm")
        result = await db.execute(select(User).filter_by(id=user_id))
        user = result.scalar_one_or_none()
        if user is None or not user.is_active:
            raise HTTPException(403, "Invalid user")
        user.is_confirmed = True
        await db.commit()
        await db.refresh(user)
        return {"message": "Success"}
    except Exception as exc:
        raise HTTPException(400, "User confirmation failed") from exc


@auth_router.post(
    "/refresh-token/", response_model=schemas.RefreshTokenResponse, status_code=200
)
async def refresh_token(
    data: schemas.RefreshTokenInput = Body(), db: AsyncSession = Depends(get_db)
):
    try:
        logger.debug("User token refresh started")
        user_id = JWTRepo.decode_token(data.refresh_token, "refresh")
        result = await db.execute(select(User).filter_by(id=user_id))
        auth_user = result.scalar_one_or_none()
        if auth_user is None:
            raise HTTPException(401, "Invalid user")
        access_token = JWTRepo.create_token(auth_user.id, "access")
        logger.debug("User token refresh completed")
        return {"token_type": "Bearer", "access_token": access_token}
    except Exception as exc:
        raise HTTPException(400, "An error occurred during token refresh") from exc


@auth_router.get(
    "/password-forgot-email/", response_model=schemas.Success, status_code=200
)
async def password_forgot_email(
    bg_task: BackgroundTasks,
    email: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).filter_by(email=email))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(403, "Invalid user")
    bg_task.add_task(send_forgot_password_email, user)
    return {"message": "Email to reset password sent"}


@auth_router.post(
    "/password-reset/", response_model=schemas.UserResponse, status_code=200
)
async def password_reset(
    data: schemas.PasswordResetInput = Body(), db: AsyncSession = Depends(get_db)
):
    try:
        user_id = JWTRepo.decode_token(data.reset_token, "reset")
        result = await db.execute(select(User).filter_by(id=user_id))
        user_obj = result.scalar_one_or_none()
        if user_obj is None or not user_obj.is_active:
            raise HTTPException(403, "Invalid user")
        user_obj.hash(data.password)
        await db.commit()
        await db.refresh(user_obj)
        return {"user": user_obj, "message": "Password reset done"}
    except Exception as exc:
        await db.rollback()
        raise HTTPException(400, "Password reset failed") from exc
