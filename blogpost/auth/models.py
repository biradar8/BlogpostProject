import bcrypt
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from ..config import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(250))
    email = Column(String(250), unique=True)
    username = Column(String(250), unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    is_confirmed = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    posts = relationship("Post", back_populates="author")
    drafts = relationship("Draft", back_populates="author")

    def hash(self, raw_password: str):
        self.password = bcrypt.hashpw(raw_password.encode(), salt=bcrypt.gensalt())

    def verify(self, plain_password: str):
        return bcrypt.checkpw(plain_password.encode(), self.password)
