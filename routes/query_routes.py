from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

from app.services.query_service import QueryService

router = APIRouter(prefix="/api/v1", tags=["Query"])


class QueryRequest(BaseModel):
    question: str
    input_json: Optional[Dict] = None


@router.post("/query")
async def query(request: QueryRequest):

    try:
        return QueryService.process_query(request)

    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
