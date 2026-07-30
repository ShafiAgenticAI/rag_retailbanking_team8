# Load the pdf file from data folder
# extract the content
# arrive at the chunking strategy

# Load the embedding model
# embed the chunks
# connect to postges and activate pgvector extension
# save the vector embeddings and original text in db

# uv add python-dotenv langchain-community pypdf
import logging
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag_retailbanking_team8.core.db import get_retailbankingvector_store

import os

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def ingest_retailbankingpdf(file_path):
    logging.info("Ingestion Started for %s", file_path)

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # 1 load pdf
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        if not docs:
            raise ValueError(f"No documents extracted from {file_path}")

        # 2. Metadata enrichment (for citataion)
        for doc in docs:
            doc.metadata.update(
                {
                    "source": file_path,
                    "document_extension": "pdf",
                    "page": doc.metadata.get("page"),
                    "last_updated": os.path.getmtime(file_path),
                }
            )

        logging.info("Loaded %d documents from PDF", len(docs))
        logging.info("Before Chunking")

        # 3. Chunking
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # up to 1000 characters
            chunk_overlap=200,  # up to 200 characters
        )

        chunks = splitter.split_documents(docs)
        logging.info("Total Chunks: %d", len(chunks))

        # 4 load the embedding model & 5 generate the embeddings
        # 6. save it in vector db
        vector_store = get_retailbankingvector_store(
            collection_name="retailbanking_knowledge_base"
        )
        vector_store.add_documents(chunks)

        logging.info("Ingestion Completed")
        return True

    except FileNotFoundError as error:
        logging.error("Ingestion Error: %s", error)
        return False

    except ValueError as error:
        logging.error("Ingestion Error: %s", error)
        return False

    except Exception as error:
        logging.exception("Unexpected ingestion failure for %s", file_path)
        return False


def ingest_document(file_path, customer_id=None, document_id=None):
    return ingest_retailbankingpdf(file_path)


if __name__ == "__main__":
    ingest_retailbankingpdf(
        "rag_retailbanking_team8/data/Personalized_Retail_Banking_FAQ.pdf"
    )

# to run this try the following command (from the project root):
# uv run python -m app.ingestion.ingestion
