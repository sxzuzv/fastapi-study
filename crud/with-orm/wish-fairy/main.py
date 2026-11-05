import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv() # .env 파일을 읽어 환경 변수로 등록한다.

DB_URL = os.getenv('DB_URL')
if DB_URL is None:
    raise RuntimeError('DB_URL 환경 변수가 설정되지 않았습니다.')

engine = create_engine(DB_URL, echo=True)