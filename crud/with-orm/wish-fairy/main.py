import os
from datetime import date, datetime
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Depends, Path, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


load_dotenv() # .env 파일을 읽어 환경 변수로 등록한다.

DB_URL = os.getenv('DB_URL')
if DB_URL is None:
    raise RuntimeError('DB_URL 환경 변수가 설정되지 않았습니다.')

engine = create_engine(DB_URL, echo=True)


class Base(DeclarativeBase):
    pass

class Fairy(Base):
    __tablename__ = 'fairies'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    name: Mapped[str]
    birth_date: Mapped[date]
    nickname: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


app = FastAPI(
    title='Wish Fairy',
    description="소원 요정 정보를 관리하는 서비스",
    version="0.1.0"
)
templates = Jinja2Templates(directory='templates')


def get_db():
    with Session(engine) as db:
        yield db    # 라우트 함수에 세션을 넘기고, 응답이 끝나면 with 블록이 마무리된다.


# 전체 요정 리스트 가져오기
def get_fairies(db: Session) -> list[Fairy]:
    return list(db.scalars(select(Fairy)).all())


# 지정한 요정 정보 가져오기
def get_fairy(db: Session, fairy_id: int) -> Fairy | None:
    return db.get(Fairy, fairy_id)


@app.get(
    '/fairies',
    tags=['fairies'],
    summary='전체 요정 목록 조회',
    response_class=HTMLResponse,
    response_description='전체 요정 목록 페이지',
)
def fairy_list(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    """
    등록된 모든 요정을 조회하고 목록 페이지를 반환한다.
    """
    fairies = get_fairies(db)
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={'fairies': fairies},
    )


@app.get(
    '/fairies/new',
    tags=['fairies'],
    summary='요정 등록 폼',
    response_class=HTMLResponse,
    response_description='요정 등록 페이지',
)
def fairy_new(
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name='new.html'
    )


@app.get(
    '/fairies/{fairy_id}',
    tags=['fairies'],
    summary='요정 프로필 조회',
    response_class=HTMLResponse,
    response_description='요정 프로필 페이지',
    responses={404: {'description': '존재하지 않는 요정'}}
)
def fairy_detail(
    request: Request,
    fairy_id: Annotated[int, Path(description='프로필을 확인할 요정의 id', ge=1)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    지정한 요정의 정보를 조회하고 프로필 페이지를 반환한다.
    """
    fairy = get_fairy(db, fairy_id)
    if fairy is None:
            return HTTPException(status_code=404, detail='존재하지 않는 요정입니다.')

    return templates.TemplateResponse(
        request=request,
        name='detail.html',
        context={'fairy': fairy}
    )


@app.post(
    '/fairies/create',
    tags=['fairies'],
    summary='요정 추가 폼',
    response_class=HTMLResponse,
    response_description='추가 후 프로필 페이지로 이동'
)
def fairy_create(
    request: Request,
    name: Annotated[str, Form(description='추가할 요정 이름')],
    nickname: Annotated[str, Form(description='추가할 요정 닉네임')],
    birth_date: Annotated[date, Form(description='추가할 요정 생년월일')],
    db: Annotated[Session, Depends(get_db)]
):
    fairy = Fairy(name=name, nickname=nickname, birth_date=birth_date)

    db.add(fairy)
    db.commit()

    fairy_id = fairy.id

    return RedirectResponse(f'/fairies/{fairy_id}', status_code=303)


@app.get(
    '/fairies/{fairy_id}/edit',
    tags=['fairies'],
    summary='요정 프로필 수정 폼',
    response_class=HTMLResponse,
    response_description='요정 프로필 수정 페이지',
    responses={404: {'description': '존재하지 않는 요정'}}
)
def fairy_edit(
    request: Request,
    fairy_id: Annotated[int, Path(description='프로필을 수정할 요정의 id', ge=1)],
    db: Annotated[Session, Depends(get_db)]
):
    fairy = get_fairy(db, fairy_id)
    if fairy is None:
        raise HTTPException(status_code=404, detail='존재하지 않는 요정입니다.')

    return templates.TemplateResponse(
        request=request,
        name='edit.html',
        context={'fairy': fairy}
    )


@app.post(
    '/fairies/{fairy_id}/update',
    tags=['fairies'],
    summary='요정 프로필 수정 내역 반영',
    status_code=303,
    response_description='수정 후 프로필 페이지로 이동',
    responses={404: {'description': '존재하지 않는 요정'}}
)
def fairy_update(
    fairy_id: Annotated[int, Path(description='수정 내역을 반영할 요정의 id', ge=1)],
    name: Annotated[str, Form(description='수정된 요정 이름')],
    nickname: Annotated[str, Form(description='수정된 요정 닉네임')],
    birth_date: Annotated[date, Form(description='수정된 요정 생년월일')],
    db: Annotated[Session, Depends(get_db)]
):
    fairy = get_fairy(db, fairy_id)
    if fairy is None:
        raise HTTPException(status_code=404, detail='존재하지 않는 요정입니다.')
    
    fairy.name = name
    fairy.nickname = nickname
    fairy.birth_date = birth_date
    db.commit()

    return RedirectResponse(f'/fairies/{fairy.id}', status_code=303)


@app.post(
    '/fairies/{fairy_id}/delete',
    tags=['fairies'],
    summary='요정 프로필 삭제',
    status_code=303,
    response_description='삭제 후 요정 리스트 페이지로 이동'
)
def fairy_delete(
    fairy_id: Annotated[int, Path(description='삭제할 요정의 id', ge=1)],
    db: Annotated[Session, Depends(get_db)]
):
    fairy = db.get(Fairy, fairy_id)
    if fairy is None:
        raise HTTPException(status_code=404, detail='요정을 찾을 수 없습니다.')

    db.delete(fairy)
    db.commit()

    return RedirectResponse('/fairies', status_code=303)


@app.get(
    '/signup',
    tags=['auth'],
    summary='회원가입 폼',
    response_class=HTMLResponse,
    response_description='요정 프로필 페이지',
    responses={404: {'description': '존재하지 않는 요정'}}
)
def signup(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='signup.html'
    )


@app.post('/signup')
def signup():
    pass