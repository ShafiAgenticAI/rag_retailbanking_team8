from pathlib import Path
from rag_retailbanking_team8.ingestion.ingestion import ingest_retailbankingpdf

def handle_file_upload(filename, file_bytes):
    destination = f"rag_retailbanking_team8/data/{filename}"

    with open(destination, "wb") as f:
        f.write(file_bytes)
https://github.com/ShafiAgenticAI/rag_retailbanking_team8/pull/8/conflict?name=services%252Fupload_service.py&ancestor_oid=e69de29bb2d1d6434b8b29ae775ad8c2e48c5391&base_oid=1e2b524738710487729bc4453ef4eb4f7b0f7fc0&head_oid=079ae2c085135527595c17cb7f2ee1f20d903457
    ingest_retailbankingpdf(str(destination))

    return {
        "status": "success",
        "message": "Document uploaded successfully.",
    }
