from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DraftIn(BaseModel):
    title: str
    body: str


class DraftResponse(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DraftDetail(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
