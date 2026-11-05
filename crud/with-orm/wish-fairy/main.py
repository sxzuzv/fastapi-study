import os
from datetime import date

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

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
    name: Mapped[str]
    nickname: Mapped[str]
    birth_date: Mapped[date]