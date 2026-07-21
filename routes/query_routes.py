from dataclasses import dataclass
from fastapi import (
    APIRouter,
    HTTPException
)

from services.query_service import QueryService



router = APIRouter(
    prefix="/api/query",
    tags=["Query"]
)



query_service = QueryService()



@dataclass
class QueryRequest:

    customer_id: str

    question: str



@router.post("/")
async def ask_question(
        request: QueryRequest
):

    try:

        response = await query_service.ask(
            request
        )

        return response


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )