from langchain.agents import create_agent
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage
from rag_retailbanking_team8.tools.tools import (
    search_vector,
    search_fts,
    search_hybrid,
)
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s -  %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# load env variables
if not load_dotenv():
    logger.warning("No .env file found.")

# ===========================================================
#     STORE SESSION HISTORY
# ===========================================================
store = {}


def get_session_history(session_id: str):
    try:
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]
    except Exception as e:
        logger.error(f"session history error for {session_id} - {e}")


# ===========================================================
#     PYDANTIC SCHEMAS
# ===========================================================
class Metadata(BaseModel):
    page_number: int
    file_name: str
    file_extension: str


class Retrieved_Chunks(BaseModel):
    content: str
    metadata: Metadata


class FinancialAdvice(BaseModel):
    user_query: str = Field(description="customer query")
    customer_details: str
    output_response: str = Field(description="recommendation provided")
    retrieved_chunks: List[Retrieved_Chunks]


# ===========================================================
#     PROMPT TEMPLATE
# ===========================================================


prompt = """ 
            You are an expert Financial Advisor with access to three retrieval tools.

            CRITICAL RULE: If users greets you  (example- Hi/Hello/Hey) or says something conversational DO NOT USE ANY TOOLS. 
            Reply politely and ask how you can help with related content.

            Only use a tool if the user asks a specific question requiring information from pdf.

            1. search_vector
            Use for semantic, conceptual and understanding questions.

            2. search_fts
            Use for keyword or exact-term queries (for example: SIP, FD, ROI).

            3. search_hybrid
            Use when both semantic understanding and exact keyword matching are required.

            Routing rules:
            - Always use exactly one search tool.
            - Always pass:
            - query = user's question
            - k = 5
            - collection_name = "retailbanking_knowledge_base"
             
            The retrieval results contain financial FAQs along with document metadata.

            You will also receive customer financial information in JSON format.

            Your task:

            1. Retrieve the most relevant FAQ information.
            2. Analyze the customer's financial profile using the provided JSON.
            3. Answer the user's financial question by combining the retrieved information with the customer's profile.
            4. Personalize recommendations only when supported by the retrieved information or the customer data.
            5. If the retrieved information is insufficient, explicitly say so instead of making assumptions.

            Response guidelines:
            - Answer only the user's question.
            - Be concise and direct.
            - Do not explain your reasoning or analysis process.
            - Do not repeat information.
            - Do not include section headings unless the user requests them.
            - Do not provide background information unless it is necessary to answer the question.
            - Limit the response to 3-6 short sentences (or 5 bullet points if a list is more appropriate).
            - Include only actionable recommendations that are directly relevant to the user's question.

            """


# ===========================================================
#     AGENT FUNCTIONS
# ===========================================================


def create_rag_agent():
    """Create the agent"""

    try:
        financial_agent = create_agent(
            model="openai:gpt-5.5",
            tools=[search_vector, search_fts, search_hybrid],
            response_format=FinancialAdvice,
            system_prompt=prompt,
        )

        return financial_agent
    
    except Exception as e:
        logger.error(f"Failed to create RAG agent: {e}")


def call_agent(question: str, customer_details: dict, session_id: str):
    """Executes the agent call"""

    try:
        agent = create_rag_agent()

        try:
            history = get_session_history(session_id)
        except Exception as e:
            logger.error(
                f"Failed to get session history for session_id {session_id} - {e}"
            )

        user_content = f"""
        User question: {question}

        Customer financial details in JSON:
        {customer_details}
        """

        messages = history.messages + [HumanMessage(content=user_content)]

        response = agent.invoke(
            {"messages": messages},
            config={
                "run_name": "retailbanking_knowledge_base",
                "tags": ["chatbot", "user-query"],
                "metadata": {
                    "user_id": "user_001",
                    "session_id": session_id,
                    "interface": "cli",
                },
            },
        )

        history.add_message(HumanMessage(content=user_content))

        history.add_message(response["messages"][-1])

        output = response["structured_response"]

        return output

    except Exception as e:
        logger.error(f"Failed to invoke agent : {e}")
        return {
            "status": "error",
            "message": "Internal server error. Please try again later.",
        }


# uv run python -m rag_retailbanking_team8.agents.rag_agent
