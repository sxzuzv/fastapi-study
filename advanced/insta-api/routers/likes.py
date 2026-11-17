from fastapi import APIRouter, HTTPException

from models import Like
from schemas import PostOut
from deps import PostDep, CurrentUserDep, SessionDep

router = APIRouter(prefix='/api/posts/{post_id}/likes', tags=['likes'])


@router.post('', response_model=PostOut)
def like_create(post: PostDep, user: CurrentUserDep, db: SessionDep):
    if db.get(Like, (user.id, post.id)):
        raise HTTPException(status_code=409, detail='이미 좋아요 한 게시글입니다.')

    db.add(Like(user_id=user.id, post_id=post.id))
    db.commit()

    return post
    

@router.delete('', response_model=PostOut)
def like_delete(post: PostDep, db: SessionDep, user: CurrentUserDep):
    like = db.get(Like, (user.id, post.id))

    if like is None:
        raise HTTPException(status_code=404, detail='좋아요 이력이 없습니다.')

    db.delete(like)
    db.commit()

    return post