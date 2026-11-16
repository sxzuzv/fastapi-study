from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from deps import SessionDep, password_hash, create_access_token
from models import User
from schemas import Token, UserCreate, UserOut


router = APIRouter(prefix='/api/auth', tags=['auth'])


@router.post('/signup', response_model=UserOut)
def signup(data: UserCreate, db: SessionDep):
    # 아이디 중복 확인
    user = db.scalar(select(User).where(User.username == data.username))
    if user:
        raise HTTPException(status_code=409, detail='사용 중인 아이디입니다.')

    user = User(username=data.username, password_hash=password_hash.hash(data.password))

    db.add(user)
    db.commit()

    return user


@router.post('/login', response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep):
    user = db.scalar(select(User).where(User.username == form.username))

    # 사용자가 없거나 비밀번호 불일치
    if user is None or not password_hash.verify(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail='아이디 또는 비밀번호가 올바르지 않습니다.')

    token = create_access_token(user.id)

    return {'access_token': token, 'token_type': 'bearer'}