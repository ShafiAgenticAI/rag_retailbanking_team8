from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.upload_service import UploadService

router = APIRouter(prefix="/api/v1", tags=["Upload"])


@router.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        return UploadService.upload_pdf(file)

    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
