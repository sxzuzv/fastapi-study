from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from config import settings


DB_URL = settings.DB_URL
engine = create_engine(DB_URL)

class Base(DeclarativeBase):
  pass