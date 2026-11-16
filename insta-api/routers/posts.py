from fastapi import APIRouter
from sqlalchemy import select

from deps import SessionDep
from models import Post

router = APIRouter(prefix='/api/posts')

@router.get('/')
def post_list(db: SessionDep):
    posts = db.scalars(select(Post).order_by(Post.created_at.desc())).all()
    return posts