from fastapi import Depends
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from typing import Annotated
from database import engine


password_hash = PasswordHash.recommended()

def get_db():
  with Session(engine) as db:
    yield db

SessionDep = Annotated[Session, Depends(get_db)]