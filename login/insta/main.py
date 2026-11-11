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
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
  user: Mapped['User'] = relationship(back_populates='posts')

  likes: Mapped[list['Like']] = relationship(cascade='all, delete-orphan')

class Comment(Base):
  __tablename__ = 'comments'

  id: Mapped[int] = mapped_column(primary_key=True)
  content: Mapped[str]
  created_at: Mapped[datetime] = mapped_column(server_default=func.now())
  post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'))
  post: Mapped['Post'] = relationship(back_populates='comments')

  # Post(1) : Comment(N)
  post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'))
  post: Mapped['Post'] = relationship(back_populates='comments')

  # User(1) : Comment(N)
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
  user: Mapped['User'] = relationship()

class User(Base):
  __tablename__ = 'users'

  id: Mapped[int] = mapped_column(primary_key=True)
  username: Mapped[str] = mapped_column(unique=True)
  password_hash: Mapped[str]
  posts: Mapped[list['Post']] = relationship(back_populates='user')

class UserSession(Base):
  __tablename__ = 'sessions'

  id: Mapped[str] = mapped_column(primary_key=True)
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
  created_at: Mapped[datetime] = mapped_column(server_default=func.now())
  user: Mapped['User'] = relationship()

class Like(Base):
  __tablename__ = 'likes'

  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
  post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'), primary_key=True)

  
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
  liked_ids = []  # 현재 로그인한 사용자가 좋아요를 누른 게시글 ID
  if user:
    liked_ids = db.scalars(select(Like.post_id).where(user.id == Like.user_id)).all()

  posts = db.scalars(select(Post).order_by(Post.created_at.desc())).all()
  return templates.TemplateResponse(
    request=request,
    name='list.html',
    context={'posts': posts, 'user': user, 'liked_ids': liked_ids}
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
  post = Post(content=content, user=user)
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
  if user is None:
    return RedirectResponse('/login', status_code=303)

  # 게시글 작성자 == 현재 로그인 중인 사용자 인 경우에만 수정 가능
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='본인이 작성한 게시글만 수정 가능합니다.')
  
  return templates.TemplateResponse(
    request=request,
    name='edit.html',
    context={'post': post, 'user': user}
  )


@app.post('/posts/{post_id}/update')
def post_update(
  content: str = Form(), 
  post: Post = Depends(get_post_or_404),
  db: Session = Depends(get_db),
  user: User | None = Depends(get_current_user)
):
  if user is None:
      return RedirectResponse('/login', status_code=303)
  
  # 게시글 작성자 == 현재 로그인 중인 사용자 인 경우에만 수정 가능
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='본인이 작성한 게시글만 수정 가능합니다.')
  
  post.content = content
  db.commit()

  return RedirectResponse('/posts', status_code=303)


@app.post('/posts/{post_id}/delete')
def post_delete(
  post: Post = Depends(get_post_or_404),
  db: Session = Depends(get_db),
  user: User | None = Depends(get_current_user)
):
  if user is None:
      return RedirectResponse('/login', status_code=303)
  
  # 게시글 작성자 == 현재 로그인 중인 사용자 인 경우에만 삭제 가능
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='본인이 작성한 게시글만 삭제 가능합니다.')
  
  db.delete(post)
  db.commit()
  return RedirectResponse('/posts', status_code=303)


@app.post('/posts/{post_id}/comments/create')
def comment_create(
  content: str = Form(),
  post: Post = Depends(get_post_or_404),
  user: User = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  # 로그인 하지 않은 사용자는 댓글 작성 불가
  if user is None:
    return RedirectResponse('/login', status_code=303)
  
  comment = Comment(content=content, post=post, user=user)
  db.add(comment)
  db.commit()

  return RedirectResponse(f'/posts/{post.id}', status_code=303)


@app.post('/posts/{post_id}/comments/{comment_id}/delete')
def comment_delete(
  post_id: int, 
  comment_id: int,
  user: User | None = Depends(get_current_user), 
  db: Session = Depends(get_db)
):
  # 로그인하지 않은 사용자는 댓글 삭제 권한 X
  if user is None:
    return RedirectResponse('/login', status_code=303)

  comment = db.get(Comment, comment_id)

  # 로그인한 사용자와 댓글 작성자가 동일해야 댓글 삭제 가능
  if comment.user_id != user.id:
    raise HTTPException(status_code=403, detail='본인 댓글만 삭제 가능합니다.') # 권한 없음

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


@app.post('/posts/{post_id}/likes')
def post_like(
  post: Post = Depends(get_post_or_404),
  user: User | None = Depends(get_current_user),
  db: Session = Depends(get_db)
):
  # 로그인한 사용자만 좋아요 가능
  if user is None:
    return RedirectResponse('/login', status_code=303)

  # 게시글에 대한 좋아요 이력 여부
  result = db.get(Like, (user.id, post.id)) # 복합키를 ID로 사용하면 단순화 가능

  if result:  # 이미 좋아요를 누른 경우 > 기존 내역을 지운다.
    db.delete(result)
    db.commit()
  else:       # 좋아요를 누르지 않은 경우
    like = Like(user_id=user.id, post_id=post.id)

    # 좋아요(likes) 테이블에 데이터 적재
    db.add(like)
    db.commit()


  return RedirectResponse('/posts', status_code=303)