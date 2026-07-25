from fastapi import FastAPI
from app.routes.query_routes import query_router
from app.routes.upload_routes import upload_router

app = FastAPI()

app.include_router(upload_router)
app.include_router(query_router)

# To run
# uv run uvicorn app.main:app --reload