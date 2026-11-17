from fastapi import APIRouter

from models import Comment
from schemas import CommentCreate
from deps import PostDep, CurrentUserDep, SessionDep


router = APIRouter(prefix='/api')


@router.get('/posts/{post_id}/comments')
def comment_list(post: PostDep):
    return post.comments


@router.post('/posts/{post_id}/comments')
def comment_create(
    post: PostDep,
    db: SessionDep,
    user: CurrentUserDep,
    data: CommentCreate
):
    comment = Comment(content=data.content, post_id=post.id, user_id=user.id)

    db.add(comment)
    db.commit()
    
    return comment


@router.patch('/post/comments/{comment_id}')
def comment_update():
    pass


@router.delete('/post/comments/{comment_id}')
def comment_delete():
    pass