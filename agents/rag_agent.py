from langchain.agents import create_agent
from dotenv import load_dotenv
from rag_retailbanking_team8.tools.tools import (
    search_vector,
    search_fts,
    search_hybrid,
)
from pydantic import BaseModel, Field
from typing import List
import uuid

# load env variables
if not load_dotenv():
    print("No .env file found.")

# Session ID
try:
    session_id = str(uuid.uuid4())
except Exception as e:
    print(f"Failed to generate session id: {e}")


class Metadata(BaseModel):
    page_number: int
    file_name: str
    file_extension: str


class Retrieved_Chunks(BaseModel):
    content: str
    metadata: Metadata


class FinancialAdvice(BaseModel):
    User_Query: str = Field(description="customer query")
    customer_profile: str
    output_response: str = Field(description="recommendation provided")
    retrieved_chunks: List[Retrieved_Chunks]


prompt = """ 
            You are an expert Financial Advisor with access to three retrieval tools.

            CRITICAL RULE: If users greets you  (example- Hi/Hello/Hey) or says something conversational DO NOT USE ANY TOOLS. 
            Reply politely and ask how you can help with related content.

            Only use a tool if the user asks a specific question requiring information from pdf.

            1. search_vector
            Use for semantic, conceptual, "why", or "how" questions.

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

            Only answer financial questions. If the request is unrelated to finance, politely decline.

            """


def create_rag_agent():
    try:
        financial_agent = create_agent(
            model="openai:gpt-5.5",  # brain
            tools=[search_vector, search_fts, search_hybrid],  # register tool
            response_format=FinancialAdvice,
            system_prompt=prompt,  # role
        )
        return financial_agent
    except Exception as e:
        print(f"Failed to create RAG agent: {e}")


def call_agent(question, customer_details):
    try:
        agent = create_rag_agent()

        response = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"""
                        User question: {question}
                        Customer financial details in json :{customer_details}
                        
                        """,
                    }
                ]
            },
            config={
                "configurable": {"session_id": session_id},
                "run_name": "retailbanking_knowledge_base",
                "tags": ["chatbot", "user-query"],
                "metadata": {
                    "user_id": "user_001",
                    "session_id": session_id,
                    "interface": "cli",
                },
            },
        )

        output = response["structured_response"]
        # print(output)
        return output

    except Exception as e:
        print(f"Failed to invoke agent : {e}")
        return {"status": "error", "message": str(e)}


# question = """Should I invest in FD or debt funds for buying a car in 2 years?"""
# # question = """Tell about mutual funds"""

# customer_details = {
#     "customer_id": "CUST001",
#     "age": 40,
#     "income": 1200000,
#     "employment": "Salaried",
#     "risk_appetite": "Moderate",
#     "goals": [{"goal": "Car Purchase", "target_amount": 1000000, "years": 2}],
#     "existing_investments": {"equity": 300000, "debt": 200000, "fd": 100000},
#     "liabilities": {"home_loan": 2000000},
#     "monthly_expenses": 50000,
#     "credit_score": 750,
# }

# result = call_agent(question, customer_details)  # call agent
# print(result.model_dump_json(indent=2))

# uv run python -m app.agents.rag_agent
