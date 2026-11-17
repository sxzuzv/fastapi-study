# 데이터베이스 접근 관련 코드 관리

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

DB_URL = 'postgresql+psycopg://sd4:sd4@localhost:5432/insta'
engine = create_engine(DB_URL, echo=True)

# 모델 정의
class Base(DeclarativeBase):
  pass