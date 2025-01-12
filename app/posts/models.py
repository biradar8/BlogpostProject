from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from ..config import Base


class Post(Base):
    """
    Model to store `Blogs` posted to public.
    - Only owner of post can edit or delete post.
    - Anyone with or without a account can view posts.
    - contain relationship to:
      - author = relationship("User", back_populates="posts")
    """

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True, index=True)
    title = Column(String(250))
    body = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    """
    Model to store `Comments` posted by people on a `Blog`.
    - Only owner of post can edit or delete post.
    - Anyone with a account can comment on post.
    - contain relationship to:
      - commentor = relationship("Post", back_populates="comments")
    """

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    message = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    created_at = Column(DateTime, server_default=func.now())
    author = relationship("User")
    post = relationship("Post", back_populates="comments")
