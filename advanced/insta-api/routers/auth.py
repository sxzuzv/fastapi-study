from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from deps import SessionDep, password_hash
from models import User
from schemas import UserCreate, UserOut

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