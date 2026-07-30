import logging

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.upload_service import UploadService

<<<<<<< Updated upstream
router = APIRouter(prefix="/api/v1", tags=["Upload"])
=======
logger = logging.getLogger(__name__)

upload_router = APIRouter(prefix="/api/v1", tags=["Upload"])
>>>>>>> Stashed changes


@router.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    logger.info(
        "Received upload request. File Name: %s, Content Type: %s",
        file.filename,
        file.content_type,
    )

    if file.content_type != "application/pdf":
        logger.warning(
            "Invalid file type received. File Name: %s, Content Type: %s",
            file.filename,
            file.content_type,
        )

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    try:
<<<<<<< Updated upstream
        return UploadService.upload_pdf(file)
=======
        logger.debug("Reading uploaded file: %s", file.filename)

        file_bytes = await file.read()

        logger.info(
            "File read successfully. File Name: %s, Size: %d bytes",
            file.filename,
            len(file_bytes),
        )

        response = handle_file_upload(file.filename, file_bytes)

        logger.info(
            "File processed successfully. File Name: %s",
            file.filename,
        )

        return response

    except HTTPException:
        logger.exception(
            "HTTPException occurred while processing file: %s",
            file.filename,
        )
        raise
>>>>>>> Stashed changes

    except Exception as ex:
        logger.exception(
            "Unexpected error while processing file: %s",
            file.filename,
        )

        raise HTTPException(
            status_code=500,
            detail=str(ex),
        )