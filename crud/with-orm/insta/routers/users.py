# 사용자 관련 기능 (auth.py는 로그인(인증) 관련 기능)

# 서드파티 라이브러리
from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import RedirectResponse
from sqlalchemy import select

# 프로젝트 모듈
from deps import SessionDep, templates, CurrentUserDep
from models import User, Post, Follow


router = APIRouter()


@router.get('/users/{username}')
def user_profile(
    request: Request,
    username: str,
    user: CurrentUserDep,
    db: SessionDep
):
    # 프로필을 보여줄 사용자 정보
    owner = db.scalar(select(User).where(User.username == username))
    if owner is None:
        raise HTTPException(status_code=404, detail='존재하지 않는 사용자입니다.')

    # 사용자가 작성한 게시글 목록 (최근 작성일 기준)
    posts = db.scalars(select(Post).where(Post.user_id == owner.id).order_by(Post.created_at.desc())).all()

    # owner가 팔로우하는 사람들 = 팔로잉
    following_list = db.scalars(select(Follow).where(Follow.follower_id == owner.id)).all()
    # owner를 팔로우하는 사람들 = 팔로워
    follower_list = db.scalars(select(Follow).where(Follow.following_id == owner.id)).all()

    return templates.TemplateResponse(
        request=request,
        name='profile.html',
        context={
            'owner': owner,
            'posts': posts,
            'user': user,
            'follower_list': follower_list,
            'following_list': following_list
        }
    )


@router.post('/users/{username}/follows')
def user_follow(
    username: str,
    user: CurrentUserDep,
    db: SessionDep
):
    # 로그인한 사용자만 팔로우 가능
    if user is None:
        return RedirectResponse('/login', status_code=303)

    # 프로필 페이지 주인 = 팔로우할 대상
    owner = db.scalar(select(User).where(User.username == username))

    # 현재 로그인 중인 사용자가 프로필 페이지 주인을 팔로우 하는가?
    follow = db.get(Follow, (user.id, owner.id))

    if follow:  # 팔로우가 돼있으면 취소
        db.delete(follow)
    else:       # 팔로우가 안 돼있으면 추가
        follow = Follow(follower_id=user.id, following_id=owner.id)
        db.add(follow)

    db.commit()

    # 팔로우한 사용자의 프로필로 리다이렉션
    return RedirectResponse(f'/users/{username}', status_code=303)