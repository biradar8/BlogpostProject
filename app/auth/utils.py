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

from ..config import get_db, global_config
from .models import User

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/user/login/")


class JWTRepo:
    @staticmethod
    def create_token(
        user_id: int,
        token_type: Literal["access", "confirm", "refresh", "reset"],
        expiry_minutes: int = 30,
    ):
        try:
            expires = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
            payload = {"sub": str(user_id), "exp": expires, "type": token_type}
            return jwt.encode(
                payload, key=global_config.SECRET_KEY, algorithm=global_config.ALGORITHM
            )
        except JWTError as exc:
            logger.error(f"{token_type} JWT token could not be created : {str(exc)}")
            raise exc

    @staticmethod
    def decode_token(
        token: str, token_type: Literal["access", "confirm", "refresh", "reset"]
    ) -> int:
        try:
            payload = jwt.decode(
                token, key=global_config.SECRET_KEY, algorithms=global_config.ALGORITHM
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


def send_mail(from_email, to_email, subject, content, content_type):
    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(content, content_type))
    try:
        with smtplib.SMTP(
            global_config.EMAIL_SERVER, int(global_config.EMAIL_PORT)
        ) as server:
            server.starttls()
            server.login(global_config.EMAIL_USER, global_config.EMAIL_PASSWORD)
            server.sendmail(from_email, to_email, message.as_string())
            logger.info(f"Email sent to {to_email}")
    except Exception as exc:
        logger.error(f"Error sending email to {to_email}: {exc}")


def send_user_confirm_email(user: User):
    token = JWTRepo.create_token(user.id, "confirm", 1440)
    url_endpoint = f"{global_config.USER_CONFIRM_ENDPOINT}{token}"
    sender_email = f"{global_config.WEBSITE_NAME}<{global_config.EMAIL_USER}>"
    subject = "Activate Your Account"
    body = textwrap.dedent(
        f"""<div style="font-family: Verdana, Geneva, sans-serif;">\
        <p>Hello {user.full_name},</p><p>Thank you for signing up.</p>\
        <p>Activate your account, by clicking the link below:</p>\
        <p><a href="{global_config.WEBSITE_DOMAIN}{url_endpoint}">Confirm Your Email</a></p>\
        <br><p>Best Regards,</p><p>{global_config.WEBSITE_NAME}</p></div>"""
    )
    send_mail(sender_email, user.email, subject, body, "html")


def send_forgot_password_email(user: User):
    token = JWTRepo.create_token(user.id, "reset", 1440)
    url_endpoint = f"/api/user/password-forgot/{token}"
    sender_email = f"{global_config.WEBSITE_NAME}<{global_config.EMAIL_USER}>"
    subject = "Reset Your password"
    body = textwrap.dedent(
        f"""<div style="font-family: Verdana, Geneva, sans-serif;">\
        <p>Hello {user.full_name},</p><p>Thank you for signing up.</p>\
        <p>Reset your password, by clicking the link below:</p><p>\
        <a href="{global_config.WEBSITE_DOMAIN}{url_endpoint}">Reset Password</a></p>\
        <br><p>Best Regards,</p><p>{global_config.WEBSITE_NAME}</p></div>"""
    )
    send_mail(sender_email, user.email, subject, body, "html")
