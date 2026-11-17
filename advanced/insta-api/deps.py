from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from database import engine
from models import Post, User, Comment
from config import settings


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


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = 'HS256'

def create_access_token(user_id: int):
  exp = datetime.now(timezone.utc) + timedelta(minutes=30)
  return jwt.encode({'sub': str(user_id), 'exp': exp}, SECRET_KEY, algorithm=ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep):
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # 서명 검증 및 페이로드 추출
  except:
    raise HTTPException(status_code=401, detail='토큰이 올바르지 않습니다.', headers={'WWW-Authenticate': 'Bearer'})

  user = db.get(User, int(payload['sub']))

  if user is None:
    raise HTTPException(status_code=401, detail='존재하지 않는 사용자입니다.', headers={'WWW-Authenticate': 'Bearer'})

  return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]


def get_my_post(post: PostDep, user: CurrentUserDep):
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='본인이 작성한 게시글만 변경 가능합니다.')
  
  return post

MyPostDep = Annotated[Post, Depends(get_my_post)]


def get_comment_or_404(comment_id: int, db: SessionDep):
  comment = db.get(Comment, comment_id)

  if comment is None:
    raise HTTPException(status_code=404, detail='존재하지 않는 댓글입니다.')
  
  return comment

CommentDep = Annotated[Comment, Depends(get_comment_or_404)]


def get_my_comment(comment: CommentDep, user: CurrentUserDep):
  if comment.user_id != user.id:
    raise HTTPException(status_code=403, detail='본인이 작성한 댓글만 변경 가능합니다.')

  return comment

MyCommentDep = Annotated[Comment, Depends(get_my_comment)]