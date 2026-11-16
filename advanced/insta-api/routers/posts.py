from fastapi import APIRouter
from sqlalchemy import select

from deps import SessionDep, PostDep
from models import Post
from schemas import PostOut, PostCreate, PostUpdate

router = APIRouter(prefix='/api/posts')


@router.get('', response_model=list[PostOut])
def post_list(db: SessionDep):
    posts = db.scalars(select(Post).order_by(Post.created_at.desc())).all()

    return posts


@router.get('/{post_id}', response_model=PostOut)
def post_detail(post: PostDep):
    return post


@router.post('', response_model=PostOut, status_code=201)
def post_create(data: PostCreate, db: SessionDep):
    post = Post(content=data.content, user_id=data.user_id)

    db.add(post)
    db.commit()

    return post


@router.patch('/{post_id}', response_model=PostOut)
def post_update(post: PostDep, data: PostUpdate, db: SessionDep):
    post.content = data.content

    db.commit()

    return post