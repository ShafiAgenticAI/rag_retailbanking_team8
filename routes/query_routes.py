import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.query_service import QueryService

<<<<<<< Updated upstream
router = APIRouter(prefix="/api/v1", tags=["Query"])
=======
logger = logging.getLogger(__name__)

query_router = APIRouter(prefix="/api/v1", tags=["Query"])
>>>>>>> Stashed changes


class QueryRequest(BaseModel):
    question: str
    input_json: Optional[Dict] = None


@router.post("/query")
async def query(request: QueryRequest):
<<<<<<< Updated upstream

    try:
        return QueryService.process_query(request)
=======
    logger.info("Received query request. Session ID: %s", request.session_id)

    request_dict = request.model_dump()

    try:
        logger.debug("Processing query for session: %s", request.session_id)

        response = process_query(request_dict)

        logger.info(
            "Query processed successfully. Session ID: %s",
            request.session_id,
        )

        return response

    except HTTPException:
        logger.exception(
            "HTTPException occurred while processing query. Session ID: %s",
            request.session_id,
        )
        raise
>>>>>>> Stashed changes

    except Exception as ex:
        logger.exception(
            "Unexpected error while processing query. Session ID: %s",
            request.session_id,
        )

        raise HTTPException(
            status_code=500,
            detail=str(ex),
        )