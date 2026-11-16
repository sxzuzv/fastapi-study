from pydantic import BaseModel, Field
from datetime import datetime


class UserOut(BaseModel):
    id: int
    username: str


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=4)


class PostOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    user: UserOut


class PostCreate(BaseModel):
    content: str = Field(min_length=1, max_length=500)
    user_id: int


class PostUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=500)


class Token(BaseModel):
    access_token: str
    token_type: str