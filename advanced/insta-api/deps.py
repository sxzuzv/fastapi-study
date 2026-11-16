from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from database import engine
from models import Post


password_hash = PasswordHash.recommended()

def get_db():
  with Session(engine) as db:
    yield db

SessionDep = Annotated[Session, Depends(get_db)]


def get_post_or_404(post_id: int, db: SessionDep):
  post = db.get(Post, post_id)

  if post is None:
    raise HTTPException(status_code=404, detail='존재하지 않는 게시물입니다.')

  return post

PostDep = Annotated[Post, Depends(get_post_or_404)]


SECRET_KEY = 'haem-secret'
ALGORITHM = 'HS256'

def create_access_token(user_id: int):
  exp = datetime.now(timezone.utc) + timedelta(minutes=30)
  return jwt.encode({'sub': str(user_id), 'exp': exp}, SECRET_KEY, algorithm=ALGORITHM)