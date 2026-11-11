# 사용자 관련 기능 (auth.py는 로그인(인증) 관련 기능)

# 서드파티 라이브러리
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import select

# 프로젝트 모듈
from deps import SessionDep, templates, CurrentUserDep
from models import User, Post


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

    return templates.TemplateResponse(
        request=request,
        name='profile.html',
        context={
            'owner': owner,
            'posts': posts,
            'user': user
        }
    )