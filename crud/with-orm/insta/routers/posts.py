# 게시글 관련 기능

# 서드파티 라이브러리
from fastapi import Depends, Form, HTTPException, Request, APIRouter
from fastapi.responses import RedirectResponse
from sqlalchemy import select

# 프로젝트 모듈
from deps import CurrentUserDep, PostDep, SessionDep, templates
from models import Comment, Like, Post


router = APIRouter()


@router.get('/posts')
def post_list(
  db: SessionDep,
  request: Request, 
  user: CurrentUserDep
):
  liked_ids = []  # 현재 로그인한 사용자가 좋아요를 누른 게시글 ID
  if user:
    liked_ids = [like.post_id for like in user.likes]
    # liked_ids = db.scalars(select(Like.post_id).where(user.id == Like.user_id)).all()

  posts = db.scalars(select(Post).order_by(Post.created_at.desc())).all()
  return templates.TemplateResponse(
    request=request,
    name='list.html',
    context={'posts': posts, 'user': user, 'liked_ids': liked_ids}
  )


@router.get('/posts/new')
def post_new(
  request: Request,
  user: CurrentUserDep
):
  # 로그인을 하지 않은 상태 > 로그인 페이지로 리다이렉션
  if user is None:
    return RedirectResponse('/login', status_code=303)

  return templates.TemplateResponse(
    request=request,
    name='new.html',
    context={'user': user}
  )


@router.post('/posts/create')
def post_create(
  db: SessionDep,
  user: CurrentUserDep,
  content: str = Form()
):
  if user is None:
    return RedirectResponse('/login', status_code=303)
  
  # db = Session(engine)
  post = Post(content=content, user=user)
  db.add(post)
  db.commit()

  # from fastapi.responses import RedirectResponse
  return RedirectResponse('/posts', status_code=303)


@router.get('/posts/{post_id}')
def post_detail(
  request: Request, 
  post: PostDep,
  user: CurrentUserDep
):
  # comments = db.scalars(select(Comment).where().order_by(Comment.created_at.desc()))
  return templates.TemplateResponse(
    request=request,
    name='detail.html',
    context={'post': post, 'user': user}
  )


@router.get('/posts/{post_id}/edit')
def post_edit(
  request: Request,
  post: PostDep,
  user: CurrentUserDep
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


@router.post('/posts/{post_id}/update')
def post_update(
  post: PostDep,
  db: SessionDep,
  user: CurrentUserDep,
  content: str = Form(),
):
  if user is None:
      return RedirectResponse('/login', status_code=303)
  
  # 게시글 작성자 == 현재 로그인 중인 사용자 인 경우에만 수정 가능
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='본인이 작성한 게시글만 수정 가능합니다.')
  
  post.content = content
  db.commit()

  return RedirectResponse('/posts', status_code=303)


@router.post('/posts/{post_id}/delete')
def post_delete(
  post: PostDep,
  db: SessionDep,
  user: CurrentUserDep
):
  if user is None:
      return RedirectResponse('/login', status_code=303)
  
  # 게시글 작성자 == 현재 로그인 중인 사용자 인 경우에만 삭제 가능
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='본인이 작성한 게시글만 삭제 가능합니다.')
  
  db.delete(post)
  db.commit()
  return RedirectResponse('/posts', status_code=303)


@router.post('/posts/{post_id}/comments/create')
def comment_create(
  post: PostDep,
  db: SessionDep,
  user: CurrentUserDep,
  content: str = Form(),
):
  # 로그인 하지 않은 사용자는 댓글 작성 불가
  if user is None:
    return RedirectResponse('/login', status_code=303)
  
  comment = Comment(content=content, post=post, user=user)
  db.add(comment)
  db.commit()

  return RedirectResponse(f'/posts/{post.id}', status_code=303)


@router.post('/posts/{post_id}/comments/{comment_id}/delete')
def comment_delete(
  post_id: int, 
  comment_id: int,
  user: CurrentUserDep,
  db: SessionDep
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


@router.post('/posts/{post_id}/likes')
def post_like(
  post: PostDep,
  user: CurrentUserDep,
  db: SessionDep
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