from fastapi import FastAPI
from rag_retailbanking_team8.routes.query_routes import query_router
from rag_retailbanking_team8.routes.upload_routes import upload_router

rag_retailbanking_team8 = FastAPI()

rag_retailbanking_team8.include_router(upload_router)
rag_retailbanking_team8.include_router(query_router)

# To run
# uv run uvicorn rag_retailbanking_team8.main:rag_retailbanking_team8 --reload
# streamlit run rag_retailbanking_team8/ui/retailbanking.py
