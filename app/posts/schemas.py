from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserAuthor(BaseModel):
    full_name: str
    model_config = ConfigDict(from_attributes=True)


class PostIn(BaseModel):
    title: str
    body: str


class Comment(BaseModel):
    message: str


class CommentDetail(BaseModel):
    message: str
    author: UserAuthor
    model_config = ConfigDict(from_attributes=True)


class PostList(BaseModel):
    title: str
    body: str
    slug: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PostListOwner(BaseModel):
    id: int
    title: str
    body: str
    slug: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PostResponse(BaseModel):
    id: int
    title: str
    body: str
    slug: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PostDetail(BaseModel):
    title: str
    body: str
    author: UserAuthor
    created_at: datetime
    comments: list[CommentDetail]
    model_config = ConfigDict(from_attributes=True)
