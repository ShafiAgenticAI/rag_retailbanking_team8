from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException
)  # type: ignore

from services.upload_service import UploadService


router = APIRouter(
    prefix="/api/upload",
    tags=["Upload"]
)


upload_service = UploadService()


@router.post("/")
async def upload_document(
        file: UploadFile = File(...),
        customer_id: str = Form(...)
):

    try:

        response = await upload_service.upload(
            file,
            customer_id
        )

        return response


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )