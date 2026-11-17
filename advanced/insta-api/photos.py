import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from PIL import Image, ImageOps, UnidentifiedImageError

Path('media').mkdir(exist_ok=True)


def save_photo(photo: UploadFile):
  try:
    image = Image.open(photo.file)
  except UnidentifiedImageError:
    raise HTTPException(status_code=400, detail='이미지 파일만 올릴 수 있습니다.')

  image = ImageOps.exif_transpose(image)
  image = ImageOps.fit(image, (1080, 1080))
  image = image.convert('RGB')

  name = f'{uuid.uuid4().hex}.jpg'
  image.save(f'media/{name}')

  return f'/media/{name}'