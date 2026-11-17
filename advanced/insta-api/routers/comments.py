from fastapi import APIRouter

from models import Comment
from schemas import CommentCreate, CommentUpdate
from deps import PostDep, CurrentUserDep, SessionDep, MyCommentDep


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
def comment_update(comment: MyCommentDep, data: CommentUpdate, db: SessionDep):
    comment.content = data.content
    db.commit()
    return comment


@router.delete('/post/comments/{comment_id}')
def comment_delete(comment: MyCommentDep, db: SessionDep):
    db.delete(comment)
    db.commit()