from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class GlobalConfig(BaseSettings):
    ENV_STATE: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    ALGORITHM: Optional[str] = None
    EMAIL_USER: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None
    EMAIL_SERVER: Optional[str] = None
    EMAIL_PORT: Optional[str] = None
    WEBSITE_DOMAIN: Optional[str] = None
    WEBSITE_NAME: Optional[str] = None
    USER_CONFIRM_ENDPOINT: Optional[str] = None
    model_config = SettingsConfigDict(env_file="blogpost/.env", extra="ignore")


global_config = GlobalConfig()
