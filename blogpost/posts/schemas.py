from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserAuthor(BaseModel):
    full_name: str
    model_config = ConfigDict(from_attributes=True)


class PostIn(BaseModel):
    title: str
    body: str


class PostList(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PostResponse(BaseModel):
    id: int
    title: str
    body: str
    author: UserAuthor
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PostDetail(BaseModel):
    id: int
    title: str
    body: str
    author: UserAuthor
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
