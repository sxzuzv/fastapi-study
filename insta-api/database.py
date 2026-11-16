from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

DB_URL = 'postgresql+psycopg://sd4:sd4@localhost:5432/insta_api'
engine = create_engine(DB_URL)

class Base(DeclarativeBase):
  pass
