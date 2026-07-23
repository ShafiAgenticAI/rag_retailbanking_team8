from pathlib import Path
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
