import logging
from pathlib import Path
<<<<<<< Updated upstream
import shutil

from app.ingestion.ingestion import ingest_retailbankingpdf


class UploadService:

    DATA_FOLDER = Path("rag_retailbanking_team8/data")

    @classmethod
    def upload_pdf(cls, uploaded_file):

        cls.DATA_FOLDER.mkdir(parents=True, exist_ok=True)

        destination = cls.DATA_FOLDER / uploaded_file.filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(uploaded_file.file, buffer)

        ingest_retailbankingpdf(str(destination))

        return {
            "status": "success",
            "message": "Document uploaded successfully.",
            "file_name": uploaded_file.filename,
        }
=======

from rag_retailbanking_team8.ingestion.ingestion import ingest_retailbankingpdf

logger = logging.getLogger(__name__)


def handle_file_upload(filename, file_bytes):
    logger.info("Started processing uploaded file: %s", filename)

    try:
        destination = Path(f"rag_retailbanking_team8/data/{filename}")

        logger.debug("Saving file to: %s", destination)

        with open(destination, "wb") as f:
            f.write(file_bytes)

        logger.info(
            "File saved successfully. File Name: %s, Size: %d bytes",
            filename,
            len(file_bytes),
        )

        logger.info("Starting document ingestion for file: %s", filename)

        ingest_retailbankingpdf(str(destination))

        logger.info("Document ingestion completed successfully. File: %s", filename)

        return {
            "status": "success",
            "message": "Document uploaded successfully.",
        }

    except FileNotFoundError:
        logger.exception(
            "Destination directory not found while uploading file: %s",
            filename,
        )
        raise

    except PermissionError:
        logger.exception(
            "Permission denied while saving file: %s",
            filename,
        )
        raise

    except Exception:
        logger.exception(
            "Unexpected error while processing uploaded file: %s",
            filename,
        )
        raise
>>>>>>> Stashed changes
