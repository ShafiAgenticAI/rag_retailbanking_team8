from pathlib import Path
from rag_retailbanking_team8.ingestion.ingestion import ingest_retailbankingpdf

def handle_file_upload(filename, file_bytes):
    destination = f"rag_retailbanking_team8/data/{filename}"

    with open(destination, "wb") as f:
        f.write(file_bytes)

    ingest_retailbankingpdf(str(destination))

    return {
        "status": "success",
        "message": "Document uploaded successfully.",
    }