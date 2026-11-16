from fastapi import APIRouter
from sqlalchemy import select

from deps import SessionDep, PostDep
from models import Post
from schemas import PostOut

router = APIRouter(prefix='/api/posts')


@router.get('', response_model=list[PostOut])
def post_list(db: SessionDep):
    posts = db.scalars(select(Post).order_by(Post.created_at.desc())).all()

    return posts


@router.get('/{post_id}', response_model=PostOut)
def post_detail(post: PostDep):
    return post