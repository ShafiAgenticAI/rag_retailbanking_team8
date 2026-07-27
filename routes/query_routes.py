from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional, Dict

from rag_retailbanking_team8.services.query_service import process_query

query_router = APIRouter(prefix="/api/v1", tags=["Query"])


class QueryRequest(BaseModel):
    question: str
    input_json: Optional[Dict] = None


@query_router.post("/query")
async def query(request: QueryRequest):
    request_dict = request.model_dump()
    try:
        content = process_query(request_dict)
        return PlainTextResponse(content=content, status_code=200)

    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
