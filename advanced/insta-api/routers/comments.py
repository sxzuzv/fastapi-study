from fastapi import APIRouter

from models import Comment
from schemas import CommentCreate, CommentUpdate, CommentOut
from deps import PostDep, CurrentUserDep, SessionDep, MyCommentDep


router = APIRouter(prefix='/api', tags=['comments'])


@router.get('/posts/{post_id}/comments', response_model=list[CommentOut])
def comment_list(post: PostDep):
    return post.comments


@router.post('/posts/{post_id}/comments', response_model=CommentOut, status_code=201)
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


@router.patch('/posts/comments/{comment_id}', response_model=CommentOut)
def comment_update(comment: MyCommentDep, data: CommentUpdate, db: SessionDep):
    comment.content = data.content
    db.commit()
    return comment


@router.delete('/posts/comments/{comment_id}', status_code=204)
def comment_delete(comment: MyCommentDep, db: SessionDep):
    db.delete(comment)
    db.commit()