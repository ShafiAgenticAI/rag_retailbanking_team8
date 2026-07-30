<<<<<<< Updated upstream
from app.agents.rag_agent import call_agent


class QueryService:

    @staticmethod
    def process_query(request):

        response = call_agent(
            question=request.question, customer_details=request.input_json
        )

        return {
            "answer": response.output_response,
            "sources": [
                {
                    "file_name": chunk.metadata.file_name,
                    "page_number": chunk.metadata.page_number,
                    "snippet": chunk.content,
                    "file_extension": chunk.metadata.file_extension,
                }
                for chunk in response.retrieved_chunks
            ],
        }
=======
import logging

from rag_retailbanking_team8.agents.rag_agent import call_agent

logger = logging.getLogger(__name__)


def process_query(request):
    """Receives query and customer details, invokes the RAG agent."""

    logger.info("Processing query request.")

    try:
        user_query = request.get("question", "")
        customer_details = request.get("customer_details")
        session_id = request.get("session_id")

        logger.debug("Session ID: %s", session_id)
        logger.debug("Customer details received: %s", customer_details is not None)

        if not user_query:
            logger.warning("Empty user query received. Session ID: %s", session_id)
            return {
                "status": "error",
                "message": "No user query"
            }

        logger.info("Passing query to RAG agent. Session ID: %s", session_id)

        agent_response = call_agent(
            user_query,
            customer_details=customer_details,
            session_id=session_id,
        )

        logger.info("Successfully received response from RAG agent. Session ID: %s", session_id)

        return {
            "status": "success",
            "answer": agent_response,
        }

    except Exception:
        logger.exception(
            "Unexpected error while processing query. Session ID: %s",
            request.get("session_id"),
        )
        raise
>>>>>>> Stashed changes
