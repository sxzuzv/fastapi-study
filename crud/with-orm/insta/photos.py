# 파일 업로드 관련 코드 관리

import uuid
import shutil
from pathlib import Path

from fastapi import UploadFile

Path('media').mkdir(exist_ok=True)

def save_photo(photo: UploadFile):
    ext = Path(photo.filename).suffix   # 파일 확장자 추출
    name = f'{uuid.uuid4().hex}{ext}'   # 임의의 난수 생성하여 파일명으로 사용

    with open(f'media/{name}', 'wb') as f:
        shutil.copyfileobj(photo.file, f)

    return f'/media/{name}'
