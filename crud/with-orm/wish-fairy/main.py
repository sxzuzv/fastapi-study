import os
from datetime import date
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Depends, Path, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


load_dotenv() # .env 파일을 읽어 환경 변수로 등록한다.

DB_URL = os.getenv('DB_URL')
if DB_URL is None:
    raise RuntimeError('DB_URL 환경 변수가 설정되지 않았습니다.')

engine = create_engine(DB_URL, echo=True)


class Base(DeclarativeBase):
    pass


# fairies 테이블은 DBeaver에서 직접 생성했으므로 create_all()은 호출하지 않는다.
class Fairy(Base):
    __tablename__ = 'fairies'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    nickname: Mapped[str]
    birth_date: Mapped[date]


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