# 파일 업로드 관련 코드 관리

import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile
from PIL import Image, ImageOps


Path('media').mkdir(exist_ok=True)


def save_photo(photo: UploadFile):
    image = Image.open(photo.file)              # 업로드 이미지를 pillow 객체로 변환

    image =ImageOps.exif_transpose(image)       # 모바일 기기 업로드 사진 회전 문제 처리

    image = image.convert('RGB')                # png 파일 변환

    image = ImageOps.fit(image, (1080, 1080))   # 정방향으로 이미지 리사이즈

    name = f'{uuid.uuid4().hex}.jpg'            # 디폴트 확장자는 .jpeg, 그대로 고정값 설정
    image.save(f'media/{name}')                 # 이미지 저장

    return f'media/{name}'