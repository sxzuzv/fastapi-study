from pydantic import BaseModel, Field
from datetime import datetime


class UserOut(BaseModel):
    id: int
    username: str


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=4)


class LikeOut(BaseModel):
    user_id: int


class PostOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    user: UserOut
    likes: list[LikeOut]
    comments: list[CommentOut]


class PostCreate(BaseModel):
    content: str = Field(min_length=1, max_length=500)
    # user_id: int > JWT 적용으로 사용자 ID 불필요


class PostUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=500)


class Token(BaseModel):
    access_token: str
    token_type: str


class CommentOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    user: UserOut


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=100)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=100)