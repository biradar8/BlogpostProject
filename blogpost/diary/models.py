from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from ..config import Base


class Draft(Base):
    __tablename__ = "drafts"

    id = Column(Integer, primary_key=True)
    title = Column(String(250))
    body = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    author = relationship("User", back_populates="drafts")
