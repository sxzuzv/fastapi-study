from fastapi import APIRouter, UploadFile

from deps import CurrentUserDep
from schemas import UploadOut
from photos import save_photo

router = APIRouter(prefix='/api/uploads', tags=['uploads'])


@router.post('', response_model=UploadOut, status_code=201)
def upload(photo: UploadFile, user: CurrentUserDep):
    return {'image_url': save_photo(photo)}