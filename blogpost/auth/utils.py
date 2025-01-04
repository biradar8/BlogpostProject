import logging
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from blogpost.auth.models import User
from blogpost.config.db import get_db
from blogpost.config.settings import config

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
EMAIL_USER = config.EMAIL_USER
EMAIL_PASSWORD = config.EMAIL_PASSWORD
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login/")


class JWTRepo:
    @staticmethod
    def create_token(
        user_id: int, token_type: Literal["access", "confirm"], expiry_minutes: int = 30
    ):
        try:
            expires = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
            payload = {"sub": str(user_id), "exp": expires, "type": token_type}
            return jwt.encode(payload, key=SECRET_KEY, algorithm=ALGORITHM)
        except JWTError as exc:
            logger.error(f"{token_type} JWT token could not be created : {str(exc)}")
            raise exc

    @staticmethod
    def decode_token(token: str, token_type: Literal["access", "confirm"]) -> int:
        try:
            payload = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
            if payload is None:
                raise HTTPException(401, "Invalid token")
            exp = payload.get("exp", None)
            decode_token_type = payload.get("type", None)
            user_id = payload.get("sub", None)
            if user_id is None or exp is None or decode_token_type != token_type:
                raise HTTPException(401, "Invalid token")
            if datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
                raise HTTPException(401, "Token has expired")
            return user_id
        except Exception as exc:
            raise HTTPException(401, "Token has expired") from exc


async def current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    user_id = JWTRepo.decode_token(token, "access")
    result = await db.execute(select(User).filter_by(id=user_id))
    auth_user = result.scalar_one_or_none()
    if auth_user is None:
        raise HTTPException(401, "Invalid user")
    return auth_user


async def send_user_confirm_email(user_id: int, email: str):
    token = JWTRepo.create_token(user_id, "confirm", 1440)
    url_endpoint = f"/auth/confirm/{token}"
    logger.info(token)
