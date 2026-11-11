# 로그인 관련 기능

# 표준 라이브러리
import secrets

# 서드파티 라이브러리
from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select

# 프로젝트 모듈
from deps import CurrentUserDep, SessionDep, password_hash, templates
from models import User, UserSession


router = APIRouter()


# 회원가입(<a>)을 통해 접근하는 API
@router.get('/signup')
def signup_form(
  request: Request,
  user: CurrentUserDep
):
  return templates.TemplateResponse(
    request=request,
    name='signup.html',
    context={'user': user}
  )


# form method='post' 방식으로 접근하는 API
@router.post('/signup')
def signup(
  request: Request,
  db: SessionDep,
  username: str = Form(),
  password: str = Form()
):
  # 이미 존재하는 사용자인지 검증
  # SELECT * FROM users WHERE username='...'
  exists = db.scalar(select(User).where(User.username == username))

  # 이미 존재하는 사용자인 경우(exists != None)
  if exists:
    return templates.TemplateResponse(
      request=request,
      name='signup.html',
      context={'error': '이미 존재하는 아이디입니다.'}
    )
  
  # 사용자로부터 입력받은 비밀번호를 암호화
  hashed_pw = password_hash.hash(password)

  user = User(username=username, password_hash=hashed_pw)
  db.add(user)
  db.commit()

  return RedirectResponse('/login', status_code=303)


@router.get('/login')
def login_form(
  request: Request,
  user: CurrentUserDep
):
  return templates.TemplateResponse(
    request=request,
    name='login.html',
    context={'user': user}
  )


@router.post('/login')
def login(
  request: Request,
  db: SessionDep,
  username: str = Form(),
  password: str = Form()
):
  # 사용자가 입력한 아이디에 해당하는 유저를 데이터베이스에서 찾는다.
  user = db.scalar(select(User).where(User.username == username))

  # 유저 정보 없음 or 사용자 입력 비밀번호가 저장된 비밀번호와 동일하지 않음
  if (user is None) or not (password_hash.verify(password, user.password_hash)):
    return templates.TemplateResponse(
      request=request,
      name='login.html',
      context={'error': '아이디가 존재하지 않거나 비밀번호가 틀렸습니다.'}
    )

  # 실제 존재하는 유저 + 비밀번호 일치
  session_id = secrets.token_urlsafe(32) # 세션 ID 생성

  # 사용자 세션 생성
  user_session = UserSession(id=session_id, user=user)

  # 데이터베이스 저장
  db.add(user_session)
  db.commit()

  # 생성된 세션을 유저에게 전달 - 브라우저 쿠키에 저장
  response = RedirectResponse('/posts', status_code=303)
  response.set_cookie('session_id', session_id, httponly=True, samesite='lax') # set_cookie(key, value)

  return response


@router.post('/logout')
def logout(
  request: Request,
  db: SessionDep
):
  # 브라우저 쿠키에서 세션 정보 가져오기
  session_id = request.cookies.get('session_id')

  # 데이터베이스에서 세션 정보 조회
  user_session = db.get(UserSession, session_id)

  # 유효한 세션인 경우 데이터베이스에서 삭제
  if user_session:
    db.delete(user_session)
    db.commit()

  response = RedirectResponse('/posts', status_code=303)
  response.delete_cookie('session_id') # 브라우저 쿠키의 세션 정보도 삭제
  return response