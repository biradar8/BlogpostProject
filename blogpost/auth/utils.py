import logging
import smtplib
import textwrap
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Literal

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from blogpost.auth.models import User
from blogpost.config.db import get_db
from blogpost.config.settings import config

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login/")


class JWTRepo:
    @staticmethod
    def create_token(
        user_id: int,
        token_type: Literal["access", "confirm", "refresh"],
        expiry_minutes: int = 30,
    ):
        try:
            expires = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
            payload = {"sub": str(user_id), "exp": expires, "type": token_type}
            return jwt.encode(
                payload, key=config.SECRET_KEY, algorithm=config.ALGORITHM
            )
        except JWTError as exc:
            logger.error(f"{token_type} JWT token could not be created : {str(exc)}")
            raise exc

    @staticmethod
    def decode_token(
        token: str, token_type: Literal["access", "confirm", "refresh"]
    ) -> int:
        try:
            payload = jwt.decode(
                token, key=config.SECRET_KEY, algorithms=config.ALGORITHM
            )
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


def send_user_confirm_email(user: User):
    token = JWTRepo.create_token(user.id, "confirm", 1440)
    url_endpoint = f"/api/auth/confirm/{token}"

    sender_email = f"{config.WEBSITE_NAME}<{config.EMAIL_USER}>"
    subject = "Activate Your Account"
    body = textwrap.dedent(
        f"""<p>Hello {user.full_name},</p><p>Thank you for signing up.</p>\
        <p>To activate your account on the {config.WEBSITE_NAME}, \
        please confirm your email by clicking the link below:</p>\
        <p><a href="{config.WEBSITE_DOMAIN}{url_endpoint}">Confirm Your Email</a></p>\
        <br><p>Best Regards,</p><p>{config.WEBSITE_NAME}</p>"""
    )

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = user.email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(config.EMAIL_SERVER, int(config.EMAIL_PORT)) as server:
            server.starttls()
            server.login(config.EMAIL_USER, config.EMAIL_PASSWORD)
            server.sendmail(sender_email, user.email, message.as_string())
            logger.info(f"Confirmation email sent to {user.email}")
    except Exception as exc:
        logger.error(f"Error sending email to {user.email}: {exc}")
