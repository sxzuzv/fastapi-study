from pydantic import BaseModel
from datetime import datetime


class UserOut(BaseModel):
    id: int
    username: str


class PostOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    user: UserOut