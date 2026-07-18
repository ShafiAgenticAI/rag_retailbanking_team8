# Load the pdf file from data folder
# extract the content
# arrive at the chunking strategy

# Load the embedding model
# embed the chunks
# connect to postges and activate pgvector extension
# save the vector embeddings and original text in db

# uv add python-dotenv langchain-community pypdf
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag_retailbanking_team8.core.db import get_retailbankingvector_store

import os

load_dotenv()


def ingest_retailbankingpdf(file_path):
    print("Ingestion Started")

    # 1 load pdf
    loader = PyPDFLoader(file_path)
    docs = loader.load()

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

    print(docs)
    print("Before Chunking")

    # 3. Chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,  # upto 2000 characters
        chunk_overlap=400,  # upto 400 characters
    )

    chunks = splitter.split_documents(docs)
    print("Total Chunks")
    print(len(chunks))

    # 4 load the embedding model & 5 generate the embeddings
    # 6. save it in vector db
    vector_store = get_retailbankingvector_store(
        collection_name="retailbanking_knowledge_base"
    )
    vector_store.add_documents(chunks)

    print("Ingestion Completed")


ingest_retailbankingpdf(
    "rag_retailbanking_team8/data/Personalized_Retail_Banking_FAQ.pdf"
)

# to run this try the following command (from the project root):
# uv run python -m app.ingestion.ingestion
