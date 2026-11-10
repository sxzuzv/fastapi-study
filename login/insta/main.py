from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from sqlalchemy import create_engine, select, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from datetime import datetime
from pwdlib import PasswordHash
import secrets


DB_URL = 'postgresql+psycopg://sd4:sd4@localhost:5432/insta'
engine = create_engine(DB_URL, echo=True)

# 모델 정의
class Base(DeclarativeBase):
  pass

class Post(Base):
  __tablename__ = 'posts'

  id: Mapped[int] = mapped_column(primary_key=True)
  content: Mapped[str]
  created_at: Mapped[datetime] = mapped_column(server_default=func.now())
  # created_at: Mapped[datetime]
  comments: Mapped[list['Comment']] = relationship(
    back_populates='post',
    cascade='all, delete-orphan'
  )

class Comment(Base):
  __tablename__ = 'comments'

  id: Mapped[int] = mapped_column(primary_key=True)
  content: Mapped[str]
  created_at: Mapped[datetime] = mapped_column(server_default=func.now())
  post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'))
  post: Mapped['Post'] = relationship(back_populates='comments')

class User(Base):
  __tablename__ = 'users'

  id: Mapped[int] = mapped_column(primary_key=True)
  username: Mapped[str] = mapped_column(unique=True)
  password_hash: Mapped[str]

class UserSession(Base):
  __tablename__ = 'sessions'

  id: Mapped[str] = mapped_column(primary_key=True)
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
  created_at: Mapped[datetime] = mapped_column(server_default=func.now())
  user: Mapped['User'] = relationship()


app = FastAPI()
templates = Jinja2Templates(directory='templates')
password_hash = PasswordHash.recommended()

def get_db():
  with Session(engine) as db:
    yield db

def get_post_or_404(post_id: int, db: Session = Depends(get_db)):
  post = db.get(Post, post_id)

  if post is None:
    # from fastapi import HTTPException
    raise HTTPException(status_code=404, detail='해당 게시물이 없습니다.')
  
  return post

def get_current_user(request: Request, db: Session = Depends(get_db)):
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


@app.get('/')
def home():
  return {'hi': 'hello'}


@app.get('/posts')
def post_list(
  request: Request, 
  db: Session = Depends(get_db),
  user: User | None = Depends(get_current_user)
):
  # with Session(engine) as db:
  
  # posts = db.scalars(select(Post)).all()
  posts = db.scalars(select(Post).order_by(Post.created_at.desc())).all()
  return templates.TemplateResponse(
    request=request,
    name='list.html',
    context={'posts': posts, 'user': user}
  )


@app.get('/posts/new')
def post_new(
  request: Request,
  user: User | None = Depends(get_current_user)
):
  # 로그인을 하지 않은 상태 > 로그인 페이지로 리다이렉션
  if user is None:
    return RedirectResponse('/login', status_code=303)

  return templates.TemplateResponse(
    request=request,
    name='new.html',
    context={'user': user}
  )


@app.post('/posts/create')
def post_create(
  content: str = Form(),
  db: Session = Depends(get_db),
  user: User | None = Depends(get_current_user)
):
  if user is None:
    return RedirectResponse('/login', status_code=303)
  
  # db = Session(engine)
  post = Post(content=content)
  db.add(post)
  db.commit()

  # from fastapi.responses import RedirectResponse
  return RedirectResponse('/posts', status_code=303)


@app.get('/posts/{post_id}')
def post_detail(
  request: Request, 
  post: Post = Depends(get_post_or_404),
  user: User | None = Depends(get_current_user)
):
  # comments = db.scalars(select(Comment).where().order_by(Comment.created_at.desc()))
  return templates.TemplateResponse(
    request=request,
    name='detail.html',
    context={'post': post, 'user': user}
  )


@app.get('/posts/{post_id}/edit')
def post_edit(
  request: Request,
  post: Post = Depends(get_post_or_404),
  user: User | None = Depends(get_current_user)
):
  return templates.TemplateResponse(
    request=request,
    name='edit.html',
    context={'post': post, 'user': user}
  )


@app.post('/posts/{post_id}/update')
def post_update(
  content: str = Form(), 
  post: Post = Depends(get_post_or_404),
  db: Session = Depends(get_db)
):
  post.content = content
  db.commit()

  return RedirectResponse('/posts', status_code=303)


@app.post('/posts/{post_id}/delete')
def post_delete(
  post: Post = Depends(get_post_or_404),
  db: Session = Depends(get_db)
):
  db.delete(post)
  db.commit()
  return RedirectResponse('/posts', status_code=303)


@app.post('/posts/{post_id}/comments/create')
def comment_create(
  content: str = Form(),
  post: Post = Depends(get_post_or_404),
  db: Session = Depends(get_db)
):
  comment = Comment(content=content, post=post)
  db.add(comment)
  db.commit()

  return RedirectResponse(f'/posts/{post.id}', status_code=303)


@app.post('/posts/{post_id}/comments/{comment_id}/delete')
def comment_delete(post_id: int, comment_id: int, db: Session = Depends(get_db)):
  comment = db.get(Comment, comment_id)
  db.delete(comment)
  db.commit()

  return RedirectResponse(f'/posts/{post_id}', status_code=303)


# 회원가입(<a>)을 통해 접근하는 API
@app.get('/signup')
def signup_form(
  request: Request,
  user: User | None = Depends(get_current_user)
):
  return templates.TemplateResponse(
    request=request,
    name='signup.html',
    context={'user': user}
  )


# form method='post' 방식으로 접근하는 API
@app.post('/signup')
def signup(
  request: Request,
  username: str = Form(),
  password: str = Form(),
  db: Session = Depends(get_db)
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


@app.get('/login')
def login_form(
  request: Request,
  user: User | None = Depends(get_current_user)
):
  return templates.TemplateResponse(
    request=request,
    name='login.html',
    context={'user': user}
  )


@app.post('/login')
def login(
  request: Request,
  username: str = Form(),
  password: str = Form(),
  db: Session = Depends(get_db)
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


@app.post('/logout')
def logout(
  request: Request,
  db: Session = Depends(get_db)
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