# 의존성 관리

# 표준 라이브러리
from typing import Annotated

# 서드파티 라이브러리
from fastapi import Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

# 프로젝트 모듈
from database import engine
from models import Post, User, UserSession


templates = Jinja2Templates(directory='templates')
password_hash = PasswordHash.recommended()

def get_db():
  with Session(engine) as db:
    yield db

SessionDep = Annotated[Session, Depends(get_db)]

def get_post_or_404(post_id: int, db: SessionDep):
  post = db.get(Post, post_id)

  if post is None:
    # from fastapi import HTTPException
    raise HTTPException(status_code=404, detail='해당 게시물이 없습니다.')
  
  return post

PostDep = Annotated[Post, Depends(get_post_or_404)]

def get_current_user(request: Request, db: SessionDep):
  # Request 객체 안 쿠키({})의 session_id를 가지고 온다.
  session_id = request.cookies.get('session_id')

  if session_id is None:
    # 세션 ID가 존재하지 않는 경우 = 로그인 하지 않은 상태
    return None

  # 저장된 세션 ID에 session_id가 존재하는가?
  user_session = db.get(UserSession, session_id)

  # 유효한 세션인가?
  if user_session is None:
    return None

  # 로그인 한 상태 + 유효한 세션을 가지고 있음 > 사용자 정보를 반환
  return user_session.user

CurrentUserDep = Annotated[User | None, Depends(get_current_user)]